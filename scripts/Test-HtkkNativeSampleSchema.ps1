# Token-free own validator, invoked inside a bounded Windows Job after supplier shutdown.
param([Parameter(Mandatory=$true)][string]$InstalledRoot,[Parameter(Mandatory=$true)][string]$ResultPath)
$ErrorActionPreference='Stop'
try {
 $pins=[ordered]@{'InterfaceTemplates/Validate/01_GTGT_TT80_283.xsd'='8d4c0d88100e858ddfe221d080a6a338776d1364c7de04347bfb990d04833003';'InterfaceTemplates/TKhaiThue.xsd'='8f451719355b5a6247f65a34a37584b4a0c7f7cc81a568e1033d08b8fe9b8c1d';'InterfaceTemplates/xmldsig-core-schema.xsd'='c3b5160be1852606d10f6928e0b214d418f8dd418667cb2fb88fec31e4e6f56d'}
 function Read-PinnedSchema([string]$Relative) {
  $path=Join-Path $InstalledRoot $Relative
  $item=Get-Item -LiteralPath $path
  if($item.Attributes -band [IO.FileAttributes]::ReparsePoint -or $item.Length -gt 2097152 -or (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() -cne $pins[$Relative]){throw 'SCHEMA_PIN'}
  $settings=[Xml.XmlReaderSettings]::new();$settings.DtdProcessing=[Xml.DtdProcessing]::Prohibit;$settings.XmlResolver=$null;$settings.MaxCharactersInDocument=2097152
  $reader=[Xml.XmlReader]::Create($path,$settings)
  try{return [Xml.Schema.XmlSchema]::Read($reader,$null)}finally{$reader.Dispose()}
 }
 $main=Read-PinnedSchema 'InterfaceTemplates/Validate/01_GTGT_TT80_283.xsd'
 $common=Read-PinnedSchema 'InterfaceTemplates/TKhaiThue.xsd'
 $signature=Read-PinnedSchema 'InterfaceTemplates/xmldsig-core-schema.xsd'
 if($main.Includes.Count -ne 1 -or $main.Includes[0] -isnot [Xml.Schema.XmlSchemaRedefine] -or $main.Includes[0].SchemaLocation -cne '../TKhaiThue.xsd' -or $common.Includes.Count -ne 1 -or $common.Includes[0] -isnot [Xml.Schema.XmlSchemaImport] -or $common.Includes[0].SchemaLocation -cne 'xmldsig-core-schema.xsd' -or $signature.Includes.Count -ne 0){throw 'SCHEMA_GRAPH'}
 # Resolve the complete pinned graph in memory. No filesystem/network resolver.
 $common.Includes[0].Schema=$signature;$main.Includes[0].Schema=$common
 $schemas=[Xml.Schema.XmlSchemaSet]::new();$schemas.XmlResolver=$null;$null=$schemas.Add($main);$schemas.Compile()
 $files=[ordered]@{}
 foreach($name in @('01GTGT.xml','01GTGT-roundtrip.xml')) {
  $path=Join-Path $InstalledRoot ('DataFiles/9999999997/reference-output/'+$name);$item=Get-Item -LiteralPath $path
  if($item.Attributes -band [IO.FileAttributes]::ReparsePoint -or $item.Length -lt 1 -or $item.Length -gt 262144){throw 'XML_SIZE'}
  $before=(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
  $settings=[Xml.XmlReaderSettings]::new();$settings.DtdProcessing=[Xml.DtdProcessing]::Prohibit;$settings.XmlResolver=$null;$settings.MaxCharactersInDocument=262144;$settings.ValidationType=[Xml.ValidationType]::Schema;$settings.Schemas=$schemas
  $reader=[Xml.XmlReader]::Create($path,$settings)
  try{while($reader.Read()){}}finally{$reader.Dispose()}
  if((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() -cne $before){throw 'XML_CHANGED'}
  $files[$name]=@{sha256=$before;bytes=[int]$item.Length}
 }
 if(Test-Path -LiteralPath $ResultPath){throw 'RESULT_EXISTS'}
 [ordered]@{format='htkk-native-sample-schema-v1';valid=$true;engine='System.Xml.Schema/PowerShell7';schemaPins=$pins;files=$files} | ConvertTo-Json -Depth 5 -Compress | Set-Content -LiteralPath $ResultPath -Encoding utf8NoBOM
}catch{exit 1}
