"""Synthetic parser fixtures only: no fixture is a captured original export."""
import copy,datetime,hashlib,importlib.util,pathlib,unittest
import xml.etree.ElementTree as ET
ROOT=pathlib.Path(__file__).parent
spec=importlib.util.spec_from_file_location('annex_contract',ROOT/'htkk_annex12_fixed_export.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
spec=importlib.util.spec_from_file_location('annex_parser_fixture',ROOT/'test_gtgt_export_evidence.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
TODAY=f.TODAY
NS='{'+a.NS+'}'
def fixture():
 root=ET.fromstring(f.parser_fixture());pluc=ET.SubElement(root.find('./'+NS+'HSoKhaiThue'),NS+'PLuc');annex=ET.SubElement(pluc,NS+'PLuc_01_2_GTGT');group=ET.SubElement(annex,NS+'TenNhaMay',{'id':'ID_1'})
 for name,text in (('sTT','1'),('ten_nhaMay','NHA MAY GIA LAP - KHONG NOP'),('ma_nhaMay','9999999997-001')):ET.SubElement(group,NS+name).text=text
 for row_id,serial,kind in (('ID_44','1.1','01'),('ID_45','1.2','02')):
  row=ET.SubElement(group,NS+'DiaBanPhanBo',{'id':row_id});values={'sTT':serial,'loai':kind,**a.LOCATION_VALUES}
  for name in a.LOCATION_ORDER:ET.SubElement(row,NS+name).text={'@ZERO':'0','@FIFTY':'50'}.get(values[name],values[name])
 for name,text in (('ct10_a','0'),('ct11_a','100'),('ct12_a','0')):ET.SubElement(group,NS+name).text=text
 ET.SubElement(annex,NS+'ct13').text='0';ET.SubElement(annex,NS+'ct14').text='0'
 return ET.tostring(root,encoding='utf-8',xml_declaration=True)
def edited(body,edit):
 root=ET.fromstring(body);edit(root);return ET.tostring(root,encoding='utf-8')
class AnnexCandidateContractTests(unittest.TestCase):
 def test_fixed_leaf_count_and_unchanged_bytes_never_claim_native_or_schema_proof(self):
  body=fixture();before=bytes(body);result=a.validate_candidate(body,TODAY)
  self.assertEqual(body,before);self.assertEqual(result['sha256'],hashlib.sha256(body).hexdigest())
  self.assertEqual((result['totalLeafCount'],result['annexLeafCount'],result['taxLeafCount']),(112,38,108))
  for key in ('originalAnnexExportVerified','independentSchemaVerification','nativeAnnexRoundTripVerified','fullCompatibilityVerified'):self.assertIs(result[key],False)
 def test_original_no_annex_validator_still_rejects_annex(self):
  with self.assertRaises(a.privacy.EvidenceError):a.privacy.validate_xml(fixture(),TODAY)
 def test_private_or_unexpected_child_text_rejected_in_every_annex_leaf(self):
  root=ET.fromstring(fixture());annex=root.find('.//'+NS+'PLuc_01_2_GTGT');leaves=[node for node in annex.iter() if not len(node)]
  self.assertEqual(len(leaves),38)
  for index in range(38):
   with self.subTest(index=index),self.assertRaises(a.AnnexContractError):
    r=copy.deepcopy(root);nodes=[n for n in r.find('.//'+NS+'PLuc_01_2_GTGT').iter() if not len(n)];nodes[index].text='PRIVATE';a.validate_candidate(ET.tostring(r),TODAY)
 def test_row_ids_count_order_attributes_and_extra_annex_fail_closed(self):
  for edit in (
   lambda r:r.find('.//'+NS+'TenNhaMay').set('id','ID_2'),
   lambda r:r.find('.//'+NS+'DiaBanPhanBo').set('id','ID_43'),
   lambda r:r.find('.//'+NS+'DiaBanPhanBo').set('private','PRIVATE'),
   lambda r:r.find('.//'+NS+'TenNhaMay').append(copy.deepcopy(r.find('.//'+NS+'DiaBanPhanBo'))),
   lambda r:ET.SubElement(r.find('.//'+NS+'PLuc'),NS+'PLuc_01_3_GTGT'),
   lambda r:r.find('.//'+NS+'PLuc_01_2_GTGT').set('private','PRIVATE'),
  ):
   with self.subTest(edit=edit),self.assertRaises(a.AnnexContractError):a.validate_candidate(edited(fixture(),edit),TODAY)
 def test_base_tax_profile_and_period_still_checked(self):
  for name in ('mst','tenNNT','ct22','ma_NganhNghe','loaiTKhai','kyKKhai'):
   with self.subTest(name=name),self.assertRaises(a.AnnexContractError):a.validate_candidate(edited(fixture(),lambda r:r.find('.//'+NS+name).__setattr__('text','PRIVATE')),TODAY)
 def test_dtd_pi_namespace_and_size_rejected_before_projection(self):
  for body in (b'<!DOCTYPE x>'+fixture(),b'<!-- PRIVATE -->'+fixture(),b'<?private x?>'+fixture(),fixture().replace(a.NS.encode(),b'https://private.invalid/'),b'x'*(a.privacy.MAX_XML+1)):
   with self.assertRaises(a.AnnexContractError):a.validate_candidate(body,TODAY)
 def test_numeric_fixed_values_allow_only_zero_fraction_not_exponents_or_rounding(self):
  for replacement,accepted in (('50.00',True),('5e1',False),('49.999999999',False),('050',False),('50,00',False),('-50',False)):
   body=edited(fixture(),lambda r:r.find('.//'+NS+'ct11').__setattr__('text',replacement))
   if accepted:a.validate_candidate(body,TODAY)
   else:
    with self.assertRaises(a.AnnexContractError):a.validate_candidate(body,TODAY)

 def test_deep_unknown_tree_is_bounded_before_deep_copy_or_base_projection(self):
  for body in (b'<HSoThueDTu xmlns="'+a.NS.encode()+b'">'+b'<unknown>'*40+b'</unknown>'*40+b'</HSoThueDTu>',b'<HSoThueDTu xmlns="'+a.NS.encode()+b'">'+b'<unknown/>'*513+b'</HSoThueDTu>'):
   with self.assertRaises(a.AnnexContractError) as caught:a.validate_candidate(body,TODAY)
   self.assertEqual(caught.exception.code,'LIMIT')

class AnnexBoundedDiagnosticTests(unittest.TestCase):
 def test_value_mismatches_identify_static_field_without_returning_xml_content(self):
  for xpath,name in (('.//'+NS+'ma_nhaMay','group/ma_nhaMay'),('.//'+NS+'ct09_cqt_ten','row0/ct09_cqt_ten'),('.//'+NS+'ct13','annex/ct13')):
   body=edited(fixture(),lambda root:root.find(xpath).__setattr__('text','PRIVATE-CONTENT-DO-NOT-LOG'))
   with self.subTest(name=name),self.assertRaises(a.AnnexContractError) as caught:a.validate_candidate(body,TODAY)
   error=caught.exception
   self.assertEqual(error.code,'VALUE');self.assertEqual(error.field,a.field_id(name));self.assertNotIn('PRIVATE',str(error))
 def test_structural_mismatch_has_static_container_id_and_invalid_diagnostics_fail(self):
  body=edited(fixture(),lambda root:root.find('.//'+NS+'TenNhaMay').set('id','PRIVATE'))
  with self.assertRaises(a.AnnexContractError) as caught:a.validate_candidate(body,TODAY)
  self.assertEqual((caught.exception.code,caught.exception.field),('ATTRIBUTES',a.field_id('group')))
  for field in (-1,len(a.FIELD_NAMES),'PRIVATE',True):
   with self.assertRaises(ValueError):a.AnnexContractError('VALUE',field)
 def test_powershell_accepts_only_fixed_code_and_field_range_including_json_int64(self):
  import re
  probe=(ROOT/'probe-htkk-windows.ps1').read_text()
  codes=set(re.search(r"\$annexStageResult.contractCode -cin @\(([^)]+)\)",probe).group(1).replace("'",'').split(','))
  self.assertEqual(codes,a.CODES)
  self.assertIn('$annexStageResult.contractFieldId -lt '+str(len(a.FIELD_NAMES)),probe)
  self.assertIn('$annexStageResult.contractFieldId -is [long]',probe)
