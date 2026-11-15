"""Exact fixed synthetic 01-6/GTGT (CSSX) annex contract (Pluc_01_6_GTGT_CSSX) for the web->HTKK cases.

Privacy allowlist only, NOT native proof. Same shape as htkk_annex10_web_cases.py: callers validate the PLuc subtree
exactly, then remove it from an in-memory copy so the unchanged no-annex allowlist (fake NNT, C0/M10/2026) plus the
case's main-sheet money vector is reused. Raw bytes are never rewritten, staged or published here. Any extra row, id,
attribute, amount or string fails closed. Values: htkk_web scripts/generate-htkk-web-annex16-cssx-reference.mjs
(annex16-cssx-formula, annex16-cssx-ratio), the HTKK 5.8.2 formulas of sheet 01_6_GTGT_CSSX.
"""
NS='http://kekhaithue.gdt.gov.vn/TKhaiThue'
FORMULA_CASE='01GTGT-annex16-cssx-formula-M10-2026'
RATIO_CASE='01GTGT-annex16-cssx-ratio-M10-2026'
# 01-6/GTGT (ĐTVT): same nodes under Pluc_01_6_GTGT_DVVT (htkk_web generate-htkk-web-annex16-dvvt-reference.mjs).
DVVT_CASE='01GTGT-annex16-dvvt-M10-2026'
# The producer pins both dates to this fixed day (same as the 01-2 and 01-10 cases).
FIXED_DATE='2026-10-27'
CODES=frozenset(('NAMESPACE','STRUCTURE','ATTRIBUTES','CONTENT','VALUE','LEAF_COUNT','CASE'))
FIELDS=('pluc','annex','header','row','row/value','province','total')
ROW_LEAVES=('ct09','ct10','ma_xa','ten_xa','ct11_huyen_ma','ct11_huyen_ten','ct12_tinh_ma','ct12_tinh_ten','ct13_cqt_ma','ct13_cqt_ten','ct14','ct15','ct16','ct17','ct21')
PROVINCE_LEAVES=('ct18','ct22','ct18_tinh_ma','ct18_tinh_ten')
SECTION_HEAD=('ct10a_csxs','ct10a_dvvt','ct06','ct07')

class AnnexWebContractError(ValueError):
 def __init__(self,code,field='pluc'):
  if code not in CODES or field not in FIELDS:raise ValueError('Invalid bounded annex web diagnostic')
  self.code=code;self.field=field;self.fieldId=FIELDS.index(field);super().__init__(code)
def reject(code,field='pluc'):raise AnnexWebContractError(code,field)

HN=('10129087','Phường Sơn Tây','','','101','Thành phố Hà Nội','10129','Thuế cơ sở 16 Thành phố Hà Nội')
HP=('10309019','Phường Đồ Sơn','','','103','Thành phố Hải Phòng','10309','Thuế cơ sở 6 Thành phố Hải Phòng')
def _row(n,place,amounts):return ('ID_'+str(n),('CO SO SAN XUAT GIA LAP '+str(n)+' - KHONG NOP','9999999997-00'+str(n))+place+amounts)
# Exact values: both the web input and the native re-export must carry these strings (the native comparison is
# exact), so the same allowlist protects both files. Leaves: 74 of the no-annex main declaration + 4 header + 3x15
# rows + 2x4 provinces + 4 totals = 135; minus 4 service leaves = 131 tax leaves.
CASES={
 FORMULA_CASE:{
  'head':('1','0','50000000','900000000'),
  'rows':[_row(1,HN,('100000050','200000050','300000100','5000002','0')),_row(2,HP,('0','150000075','150000075','3000002','0')),_row(3,HN,('50','0','50','1','0'))],
  'provinces':[('ID_1',('5000003','0','101','Thành phố Hà Nội')),('ID_2',('3000002','0','103','Thành phố Hải Phòng'))],
  'totals':('8000005','0','41999995','0'),
  'money':{'ct27':'1000000000','ct28':'80000000','ct30':'400000000','ct31':'20000000','ct32':'600000000','ct33':'60000000','ct34':'1000000000','ct35':'80000000','ct36':'80000000','ct40a':'80000000','ct40':'80000000'},
  'totalLeaves':135,'taxLeaves':131,
 },
 DVVT_CASE:{
  'node':'Pluc_01_6_GTGT_DVVT','head':('0','1','30000000','0'),
  'rows':[_row(1,HN,('0','200000050','200000050','4000001','0')),_row(2,HP,('0','150000075','150000075','3000002','0')),_row(3,HN,('0','50','50','1','0'))],
  'provinces':[('ID_1',('4000002','0','101','Thành phố Hà Nội')),('ID_2',('3000002','0','103','Thành phố Hải Phòng'))],
  'totals':('7000004','0','22999996','0'),
  'money':{'ct27':'600000000','ct28':'60000000','ct32':'600000000','ct33':'60000000','ct34':'600000000','ct35':'60000000','ct36':'60000000','ct40a':'60000000','ct40':'60000000'},
  'totalLeaves':135,'taxLeaves':131,
 },
 RATIO_CASE:{
  'head':('1','0','70000001','7000000000'),
  'rows':[_row(1,HN,('1000000000','2000000001','3000000001','0','30000000')),_row(2,HP,('0','1500000000','1500000000','0','15000000')),_row(3,HN,('333333333','0','333333333','0','3333333'))],
  'provinces':[('ID_1',('0','33333333','101','Thành phố Hà Nội')),('ID_2',('0','15000000','103','Thành phố Hải Phòng'))],
  'totals':('0','48333333','0','21666668'),
  'money':{'ct27':'8000000000','ct28':'700000000','ct30':'2000000000','ct31':'100000000','ct32':'6000000000','ct33':'600000000','ct34':'8000000000','ct35':'700000000','ct36':'700000000','ct40a':'700000000','ct40':'700000000'},
  'totalLeaves':135,'taxLeaves':131,
 },
}
def is_case(case_id):return case_id in CASES
def tax_leaves(case_id):
 if case_id not in CASES:reject('CASE')
 return CASES[case_id]['taxLeaves']
def total_leaves(case_id):
 if case_id not in CASES:reject('CASE')
 return CASES[case_id]['totalLeaves']
def money(case_id):
 if case_id not in CASES:reject('CASE')
 return dict(CASES[case_id]['money'])

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
 if (node.text or '')!=expected:reject('VALUE',field)

def validate_annex(root,case_id):
 """Validate the exact PLuc subtree of the fixed annex case. Returns counts."""
 if case_id not in CASES:reject('CASE')
 spec=CASES[case_id];ns='{'+NS+'}'
 plucs=root.findall('./'+ns+'HSoKhaiThue/'+ns+'PLuc')
 if len(plucs)!=1:reject('STRUCTURE','pluc')
 pluc=plucs[0];container(pluc,(spec.get('node','Pluc_01_6_GTGT_CSSX'),),{},'pluc')
 annex=pluc[0];rows=spec['rows'];provinces=spec['provinces']
 container(annex,SECTION_HEAD+('NoiDungBangPhanBo',)*len(rows)+('cong_ct18',)*len(provinces)+('CongCacTinh','SoThuePhaiNop'),{},'annex')
 for node,value in zip(annex,spec['head']):leaf(node,value,'header')
 at=len(SECTION_HEAD)
 for node,(row_id,values) in zip(list(annex)[at:at+len(rows)],rows):
  container(node,ROW_LEAVES,{'id':row_id},'row')
  for child,value in zip(node,values):leaf(child,value,'row/value')
 at+=len(rows)
 for node,(row_id,values) in zip(list(annex)[at:at+len(provinces)],provinces):
  container(node,PROVINCE_LEAVES,{'id':row_id},'province')
  for child,value in zip(node,values):leaf(child,value,'province')
 at+=len(provinces);ct19,ct23,ct20,ct24=spec['totals']
 container(annex[at],('ct19','ct23'),{},'total');leaf(annex[at][0],ct19,'total');leaf(annex[at][1],ct23,'total')
 container(annex[at+1],('ct20','ct24'),{},'total');leaf(annex[at+1][0],ct20,'total');leaf(annex[at+1][1],ct24,'total')
 leaves=sum(1 for node in root.iter() if len(node)==0)
 if leaves!=spec['totalLeaves']:reject('LEAF_COUNT','pluc')
 return {'caseId':case_id,'rows':len(rows),'provinces':len(provinces),'totalLeafCount':spec['totalLeaves'],'taxLeafCount':spec['taxLeaves']}

def strip_annex(root):
 """Remove the already validated annex from an IN-MEMORY copy only."""
 ns='{'+NS+'}';pluc=root.find('./'+ns+'HSoKhaiThue/'+ns+'PLuc')
 if pluc is None or len(pluc)!=1:reject('STRUCTURE','pluc')
 pluc.remove(pluc[0]);pluc.text=None
 return root
