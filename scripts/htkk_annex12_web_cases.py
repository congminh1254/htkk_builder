"""Exact fixed synthetic 01-2/GTGT annex contracts for the two web->HTKK cases.

Privacy allowlist only, NOT native proof. No network, no XML writes. Callers
validate the PLuc subtree exactly, then remove it from an in-memory copy so the
unchanged no-annex allowlist (fake NNT, C0/M10/2026, 27 zeros) is reused. Raw
bytes are never rewritten, staged or published by this module. Any extra
plant, row, ID, attribute, amount or string fails closed.
"""
import re

NS='http://kekhaithue.gdt.gov.vn/TKhaiThue'
ZERO_CASE='01GTGT-annex12-zero-two-locations-M10-2026'
TWO_PLANTS_CASE='01GTGT-annex12-two-plants-nonzero-M10-2026'
# The annex producer pins both dates to this fixed historical day.
FIXED_DATE='2026-10-27'
LOCATION_ORDER=('sTT','loai','ct05','ct06','ma_xa','ten_xa','ct07_huyen_ma','ct07_huyen_ten','ct08_tinh_ma','ct08_tinh_ten','ct09_cqt_ma','ct09_cqt_ten','ct10','ct11','ct12')
FIXED_LOCATION={'ct05':'','ct06':'','ma_xa':'10129087','ten_xa':'Phường Sơn Tây','ct07_huyen_ma':'','ct07_huyen_ten':'','ct08_tinh_ma':'101','ct08_tinh_ten':'Thành phố Hà Nội','ct09_cqt_ma':'10129','ct09_cqt_ten':'Thuế cơ sở 16 Thành phố Hà Nội'}
PLANT_NAMES=('NHA MAY GIA LAP - KHONG NOP','NHA MAY GIA LAP 2 - KHONG NOP')
PLANT_CODES=('9999999997-001','99997')
CODES=frozenset(('NAMESPACE','STRUCTURE','ATTRIBUTES','CONTENT','VALUE','LEAF_COUNT','CASE','BASE_PRIVACY'))
FIELDS=('pluc','annex','group','group/value','row','row/value','annex/total','base')

class AnnexWebContractError(ValueError):
 def __init__(self,code,field='pluc'):
  if code not in CODES or field not in FIELDS:raise ValueError('Invalid bounded annex web diagnostic')
  self.code=code;self.field=field;self.fieldId=FIELDS.index(field);super().__init__(code)
def reject(code,field='pluc'):raise AnnexWebContractError(code,field)

# A second fixed synthetic place in the same tỉnh, used only by the KHBS two-places variant (public HTKK 5.8.2 catalogues
# Catalogue_Dia_Ban_Xa_Moi.xml and the CQT list of that ward, as htkk_web data/htkk-taxpayer-profile.json pins them).
SECOND_LOCATION={**FIXED_LOCATION,'ma_xa':'10131091','ten_xa':'Xã Phúc Lộc','ct09_cqt_ma':'10131','ct09_cqt_ten':'Thuế cơ sở 25 Thành phố Hà Nội'}
# Plant 3 exists only in the KHBS add-plant variant.
EXTRA_PLANT_NAMES=PLANT_NAMES+('NHA MAY GIA LAP 3 - KHONG NOP',)
EXTRA_PLANT_CODES=PLANT_CODES+('99996',)
def location(serial,kind,ct11,ct12,row_id,place=None):
 return {'id':row_id,'values':{'sTT':serial,'loai':kind,**(place or FIXED_LOCATION),'ct10':'0','ct11':ct11,'ct12':ct12}}
def plant(index,group_id,ct10_a,rows,ct12_a='0'):
 return {'id':group_id,'values':{'sTT':str(index+1),'ten_nhaMay':EXTRA_PLANT_NAMES[index],'ma_nhaMay':EXTRA_PLANT_CODES[index]},'totals':{'ct10_a':ct10_a,'ct11_a':'100.00','ct12_a':ct12_a},'rows':rows}

# Exact values come from the application's actual producer at the source commit;
# both input and the native reexport must carry identical strings (the native
# comparison is exact), so the same allowlist protects both files.
CASES={
 ZERO_CASE:{'plants':[plant(0,'ID_1','0',[location('1.1','01','50.00','0','ID_1'),location('1.2','02','50.00','0','ID_2')])],'ct13':'0','ct14':'0','totalLeaves':112,'taxLeaves':108,'groupRows':(2,)},
 TWO_PLANTS_CASE:{'plants':[
   plant(0,'ID_1','7',[location('1.1','01','33.33','2','ID_1'),location('1.2','02','66.67','5','ID_2')]),
   plant(1,'ID_2','3',[location('2.1','01','50.00','2','ID_1'),location('2.2','02','25.00','1','ID_2'),location('2.3','02','25.00','1','ID_3')]),
  ],'ct13':'10','ct14':'10','totalLeaves':163,'taxLeaves':159,'groupRows':(2,3)},
}
# Annex VARIANTS that are not native annex cases of their own: only a KHBS case carries them (validate_annex accepts them,
# is_case does not). Case 5 (htkk_khbs_web_cases ANNEX12_LAN2_CASE): the two-plant annex with plant 1 at 40/60. Cases 6-9
# (the wider-scope captures, bổ sung lần 2 against the capture B1): a third plant added; plant 2 removed; plant 2's rows 2
# and 3 moved to SECOND_LOCATION; plant 2's [10] 3 -> 4.
TWO_PLANTS_CHANGED_VARIANT='01GTGT-annex12-two-plants-changed-khbs-lan2'
ADD_PLANT_VARIANT='01GTGT-annex12-add-plant-khbs-lan2'
REMOVE_PLANT_VARIANT='01GTGT-annex12-remove-plant-khbs-lan2'
TWO_PLACES_VARIANT='01GTGT-annex12-two-places-khbs-lan2'
CT10_VARIANT='01GTGT-annex12-ct10-khbs-lan2'
_PLANT1=lambda:plant(0,'ID_1','7',[location('1.1','01','33.33','2','ID_1'),location('1.2','02','66.67','5','ID_2')])
VARIANTS={
 TWO_PLANTS_CHANGED_VARIANT:{'plants':[
   plant(0,'ID_1','7',[location('1.1','01','40.00','3','ID_1'),location('1.2','02','60.00','4','ID_2')]),
   plant(1,'ID_2','3',[location('2.1','01','50.00','2','ID_1'),location('2.2','02','25.00','1','ID_2'),location('2.3','02','25.00','1','ID_3')]),
  ],'ct13':'10','ct14':'10','totalLeaves':163,'taxLeaves':159,'groupRows':(2,3)},
 ADD_PLANT_VARIANT:{'plants':[_PLANT1(),
   plant(1,'ID_2','3',[location('2.1','01','50.00','2','ID_1'),location('2.2','02','25.00','1','ID_2'),location('2.3','02','25.00','1','ID_3')]),
   plant(2,'ID_3','5',[location('3.1','01','60.00','3','ID_1'),location('3.2','02','40.00','2','ID_2')]),
  ],'ct13':'15','ct14':'15','totalLeaves':199,'taxLeaves':195,'groupRows':(2,3,2)},
 REMOVE_PLANT_VARIANT:{'plants':[_PLANT1()],'ct13':'7','ct14':'7','totalLeaves':112,'taxLeaves':108,'groupRows':(2,)},
 TWO_PLACES_VARIANT:{'plants':[_PLANT1(),
   plant(1,'ID_2','3',[location('2.1','01','50.00','2','ID_1'),location('2.2','02','25.00','1','ID_2',SECOND_LOCATION),location('2.3','02','25.00','1','ID_3',SECOND_LOCATION)]),
  ],'ct13':'10','ct14':'10','totalLeaves':163,'taxLeaves':159,'groupRows':(2,3)},
 CT10_VARIANT:{'plants':[_PLANT1(),
   plant(1,'ID_2','4',[location('2.1','01','50.00','2','ID_1'),location('2.2','02','25.00','1','ID_2'),location('2.3','02','25.00','1','ID_3')]),
  ],'ct13':'11','ct14':'11','totalLeaves':163,'taxLeaves':159,'groupRows':(2,3)},
}
def is_case(case_id):return case_id in CASES
def tax_leaves(case_id):
 if case_id not in CASES:reject('CASE')
 return CASES[case_id]['taxLeaves']
def total_leaves(case_id):
 if case_id not in CASES:reject('CASE')
 return CASES[case_id]['totalLeaves']

def local(node,field):
 if not isinstance(node.tag,str) or not node.tag.startswith('{'+NS+'}'):reject('NAMESPACE',field)
 return node.tag[len(NS)+2:]
def container(node,order,attributes,field):
 if node.attrib!=attributes:reject('ATTRIBUTES',field)
 if (node.text or '').strip() or (node.tail or '').strip():reject('CONTENT',field)
 if tuple(local(child,field) for child in node)!=tuple(order):reject('STRUCTURE',field)
def leaf(node,expected,field):
 if node.attrib or len(node):reject('ATTRIBUTES',field)
 if (node.tail or '').strip():reject('CONTENT',field)
 text=node.text or ''
 if callable(expected):matched=expected(text)
 else:matched=text==expected
 if not matched:reject('VALUE',field)

def validate_groups(annex,plants,totals,field_prefix=''):
 order=tuple(['TenNhaMay']*len(plants))+('ct13','ct14')
 container(annex,order,{},'annex')
 for group,spec in zip(annex,plants):
  rows=spec['rows'];group_order=('sTT','ten_nhaMay','ma_nhaMay')+tuple(['DiaBanPhanBo']*len(rows))+('ct10_a','ct11_a','ct12_a')
  container(group,group_order,{'id':spec['id']},'group')
  for index,name in enumerate(('sTT','ten_nhaMay','ma_nhaMay')):leaf(group[index],spec['values'][name],'group/value')
  for offset,row in enumerate(rows):
   node=group[3+offset];container(node,LOCATION_ORDER,{'id':row['id']},'row')
   for child,name in zip(node,LOCATION_ORDER):leaf(child,row['values'][name],'row/value')
  for index,name in enumerate(('ct10_a','ct11_a','ct12_a')):leaf(group[3+len(rows)+index],spec['totals'][name],'group/value')
 leaf(annex[len(plants)],totals[0],'annex/total');leaf(annex[len(plants)+1],totals[1],'annex/total')

def validate_annex(root,case_id):
 """Validate the exact PLuc subtree of one fixed annex case. Returns counts."""
 if case_id not in CASES and case_id not in VARIANTS:reject('CASE')
 spec=CASES.get(case_id) or VARIANTS[case_id];ns='{'+NS+'}'
 plucs=root.findall('./'+ns+'HSoKhaiThue/'+ns+'PLuc')
 if len(plucs)!=1:reject('STRUCTURE','pluc')
 pluc=plucs[0];container(pluc,('PLuc_01_2_GTGT',),{},'pluc')
 validate_groups(pluc[0],spec['plants'],(spec['ct13'],spec['ct14']))
 leaves=sum(1 for node in root.iter() if len(node)==0)
 if leaves!=spec['totalLeaves']:reject('LEAF_COUNT','pluc')
 return {'caseId':case_id,'groupCount':len(spec['plants']),'groupRows':list(spec['groupRows']),'totalLeafCount':spec['totalLeaves'],'taxLeafCount':spec['taxLeaves']}

def strip_annex(root):
 """Remove the already validated annex children from an IN-MEMORY copy only."""
 ns='{'+NS+'}';pluc=root.find('./'+ns+'HSoKhaiThue/'+ns+'PLuc')
 if pluc is None or len(pluc)!=1:reject('STRUCTURE','pluc')
 pluc.remove(pluc[0]);pluc.text=None
 return root

def bounded_decimal(maximum):
 """Synthetic computed amount: plain decimal 0..maximum, at most 8 fraction digits."""
 def matcher(text):
  if not re.fullmatch(r'(?:0|[1-9][0-9]{0,2})(?:\.[0-9]{1,8})?',text):return False
  return 0<=float(text)<=maximum
 return matcher
