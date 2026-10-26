"""Candidate fixed-case privacy contract, NOT native proof or a publisher.

No network calls, workflow hooks, schema claim, source execution or XML writes.
The first original annex export must pass this contract unchanged before a
separate private-retention path can use it. Existing 13 web cases stay untouched.
"""
import copy,hashlib,importlib.util,io,pathlib,re
import xml.etree.ElementTree as ET

_spec=importlib.util.spec_from_file_location('annex12_base_privacy',pathlib.Path(__file__).with_name('publish-gtgt-export-evidence.py'))
privacy=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(privacy)
NS=privacy.NS
CASE_ID='01GTGT-annex12-zero-two-locations-M10-2026'
SOURCE_PINS={
 'InterfaceTemplates/xml/01_2_GTGT_TT80_283.xml':'9512dcfef9551892d132fd905250427c580a1320f77318ab048d6d26fd3a32e5',
 'InterfaceTemplates/xml/01_2_GTGT_TT80_xml_283.xml':'9dafb55263fa2729383cf57bc73f3b97cf48dc9a28632a596806ad0afe8f17d3',
 'InterfaceIni/DM_DUNG_CHUNG.xml':'cff4311dff86113853b2a70ca43992d72f4f5dd7ac643041e3d4d9ac2b1ba0b0',
}
GROUP_ORDER=('sTT','ten_nhaMay','ma_nhaMay','DiaBanPhanBo','DiaBanPhanBo','ct10_a','ct11_a','ct12_a')
LOCATION_ORDER=('sTT','loai','ct05','ct06','ma_xa','ten_xa','ct07_huyen_ma','ct07_huyen_ten','ct08_tinh_ma','ct08_tinh_ten','ct09_cqt_ma','ct09_cqt_ten','ct10','ct11','ct12')
LOCATION_VALUES={'ct05':'','ct06':'','ma_xa':'10129087','ten_xa':'Phường Sơn Tây','ct07_huyen_ma':'','ct07_huyen_ten':'','ct08_tinh_ma':'101','ct08_tinh_ten':'Thành phố Hà Nội','ct09_cqt_ma':'10129','ct09_cqt_ten':'Thuế cơ sở 16 Thành phố Hà Nội','ct10':'@ZERO','ct11':'@FIFTY','ct12':'@ZERO'}
CODES=frozenset(('SIZE','ENCODING','DECLARATION','XML_PARSE','NAMESPACE','STRUCTURE','ATTRIBUTES','CONTENT','VALUE','BASE_PRIVACY','LEAF_COUNT','LIMIT'))
class AnnexContractError(ValueError):
 def __init__(self,code):
  if code not in CODES:raise ValueError('Invalid bounded annex contract code')
  self.code=code;super().__init__(code)
def reject(code):raise AnnexContractError(code)
def local(node):
 if not isinstance(node.tag,str) or not node.tag.startswith('{'+NS+'}'):reject('NAMESPACE')
 return node.tag[len(NS)+2:]
def container(node,order,attributes=None):
 if node.attrib!=(attributes or {}):reject('ATTRIBUTES')
 if (node.text or '').strip() or (node.tail or '').strip():reject('CONTENT')
 if tuple(local(child) for child in node)!=order:reject('STRUCTURE')
def value(node,expected):
 if node.attrib or len(node):reject('ATTRIBUTES')
 if (node.tail or '').strip():reject('CONTENT')
 text=node.text or ''
 if expected=='@ZERO':matched=bool(re.fullmatch(r'0(?:\.0{1,8})?',text))
 elif expected=='@FIFTY':matched=bool(re.fullmatch(r'50(?:\.0{1,8})?',text))
 elif expected=='@HUNDRED':matched=bool(re.fullmatch(r'100(?:\.0{1,8})?',text))
 else:matched=text==expected or expected=='' and text.isspace()
 if not matched:reject('VALUE')
def parse(body):
 if not isinstance(body,bytes) or not 0<len(body)<=privacy.MAX_XML:reject('SIZE')
 try:text=body.decode('utf-8-sig')
 except UnicodeError:reject('ENCODING')
 if re.search(r'<!|<\?(?!xml\s)',text,re.I) or text.count('<?')>1:reject('DECLARATION')
 try:
  for _,(prefix,uri) in ET.iterparse(io.BytesIO(body),events=('start-ns',)):
   if (prefix,uri) not in (('',NS),('xsi',privacy.XSI)):reject('NAMESPACE')
  root=ET.fromstring(body)
  pending=[(root,1)];count=0
  while pending:
   node,depth=pending.pop();count+=1
   if depth>32 or count>512:reject('LIMIT')
   pending.extend((child,depth+1) for child in node)
  return root
 except ET.ParseError:reject('XML_PARSE')
def validate_candidate(body,today=None):
 """Fail closed on exactly one source-predicted synthetic two-row annex.

 ID_1 / ID_44 / ID_45 are source predictions awaiting actual native capture.
 Every byte of body stays unchanged. The private base copy is only a validation
 projection; it is never returned as XML, staged or published.
 """
 root=parse(body)
 if local(root)!='HSoThueDTu':reject('STRUCTURE')
 ns='{'+NS+'}'
 plucs=root.findall('./'+ns+'HSoKhaiThue/'+ns+'PLuc')
 if len(plucs)!=1:reject('STRUCTURE')
 pluc=plucs[0];container(pluc,('PLuc_01_2_GTGT',));annex=pluc[0]
 container(annex,('TenNhaMay','ct13','ct14'));group=annex[0]
 container(group,GROUP_ORDER,{'id':'ID_1'})
 for index,expected in ((0,'1'),(1,'NHA MAY GIA LAP - KHONG NOP'),(2,'9999999997-001'),(5,'@ZERO'),(6,'@HUNDRED'),(7,'@ZERO')):value(group[index],expected)
 for position,row_id,serial,kind in ((3,'ID_44','1.1','01'),(4,'ID_45','1.2','02')):
  location=group[position];container(location,LOCATION_ORDER,{'id':row_id})
  expected={'sTT':serial,'loai':kind,**LOCATION_VALUES}
  for child in location:value(child,expected[local(child)])
 value(annex[1],'@ZERO');value(annex[2],'@ZERO')
 # Reuse the original no-annex allowlist without changing that allowlist or raw
 # bytes. This enforces exact fake NNT/service identity, C0/M10/2026 and 27 zeros.
 projected=copy.deepcopy(root);projected_pluc=projected.find('./'+ns+'HSoKhaiThue/'+ns+'PLuc');projected_pluc.remove(projected_pluc[0])
 ET.register_namespace('',NS);ET.register_namespace('xsi',privacy.XSI)
 try:base=privacy.validate_xml(ET.tostring(projected,encoding='utf-8'),today)
 except privacy.EvidenceError:reject('BASE_PRIVACY')
 leaves=sum(1 for node in root.iter() if len(node)==0)
 if base['leafCount']!=74 or leaves!=112:reject('LEAF_COUNT')
 return {'format':'htkk-annex12-fixed-export-candidate-v1','caseId':CASE_ID,'sha256':hashlib.sha256(body).hexdigest(),'bytes':len(body),'fixedSyntheticValuesVerified':True,'totalLeafCount':112,'annexLeafCount':38,'taxLeafCount':108,'sourcePredictedRowIdsMatched':True,'originalAnnexExportVerified':False,'independentSchemaVerification':False,'nativeAnnexRoundTripVerified':False,'fullCompatibilityVerified':False}
