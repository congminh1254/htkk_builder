"""Exact fixed synthetic 01-10/GTGT annex contract (PL_NQ142_GTGT) for the web->HTKK case.

Privacy allowlist only, NOT native proof. Same shape as htkk_annex12_web_cases.py: callers
validate the PLuc subtree exactly, then remove it from an in-memory copy so the unchanged
no-annex allowlist (fake NNT, C0/M10/2026) plus the case's main-sheet money vector is reused.
Raw bytes are never rewritten, staged or published here. Any extra row, ID, attribute, amount
or string fails closed. Values: htkk_web scripts/generate-htkk-web-annex10-reference.mjs
(annex10-nq204), exact decimal arithmetic of the HTKK 5.8.2 formulas.
"""
NS='http://kekhaithue.gdt.gov.vn/TKhaiThue'
NQ204_CASE='01GTGT-annex10-nq204-M10-2026'
# The producer pins both dates to this fixed day (same as the 01-2 cases).
FIXED_DATE='2026-10-27'
CODES=frozenset(('NAMESPACE','STRUCTURE','ATTRIBUTES','CONTENT','VALUE','LEAF_COUNT','CASE'))
FIELDS=('pluc','annex','section','row','row/value','total')
PURCHASE_LEAVES=('tenHHDVMuaVao','giaTriHHDVMuaVao','thueGTGTHHDV')
SALE_LEAVES=('tenHHDV','giaTriHHDV','thueSuatTheoQuyDinh','thueSuatSauGiam','thueGTGTDuocGiam')

class AnnexWebContractError(ValueError):
 def __init__(self,code,field='pluc'):
  if code not in CODES or field not in FIELDS:raise ValueError('Invalid bounded annex web diagnostic')
  self.code=code;self.field=field;self.fieldId=FIELDS.index(field);super().__init__(code)
def reject(code,field='pluc'):raise AnnexWebContractError(code,field)

# Exact values: both the web input and the native re-export must carry these strings
# (the native comparison is exact), so the same allowlist protects both files.
CASES={
 NQ204_CASE:{
  'purchases':[('ID_1',('HANG HOA MUA VAO GIA LAP 8% - KHONG NOP','12345678','987654'))],
  'purchaseTotals':('12345678','987654'),
  'sales':[('ID_1',('HANG HOA BAN RA GIA LAP 1 - KHONG NOP','150000025','10','8','3000001')),
           ('ID_2',('HANG BAN BI TRA LAI GIA LAP - KHONG NOP','-20000075','10','8','-400002'))],
  'saleTotals':('129999950','2599999'),'ct9':'1612345',
  # Main sheet after HTKK's CellChange_7 events: [32] := [07], [33] := ROUND([32]*10/100-[08],0).
  'money':{'ct32':'129999950','ct33':'10399996','ct27':'129999950','ct28':'10399996','ct34':'129999950','ct35':'10399996','ct36':'10399996','ct40a':'10399996','ct40':'10399996'},
  # 74 leaves of the no-annex main declaration + 18 annex leaves; minus 4 service leaves.
  'totalLeaves':92,'taxLeaves':88,
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
 pluc=plucs[0];container(pluc,('PL_NQ142_GTGT',),{},'pluc')
 annex=pluc[0];container(annex,('HH_DV_MuaVaoTrongKy','HH_DV_BanRaTrongKy','ChenhLech'),{},'annex')
 for section,rows,leaves,totals,names in ((annex[0],spec['purchases'],PURCHASE_LEAVES,spec['purchaseTotals'],('tongCongGiaTriHHDVMuaVao','tongCongThueGTGTHHDV')),
                                         (annex[1],spec['sales'],SALE_LEAVES,spec['saleTotals'],('tongCongGiaTriHHDV','tongCongThueGTGTDuocGiam'))):
  container(section,tuple(['BangKeTenHHDV']*len(rows))+names,{},'section')
  for node,(row_id,values) in zip(section,rows):
   container(node,leaves,{'ID':row_id},'row')
   for child,value in zip(node,values):leaf(child,value,'row/value')
  leaf(section[len(rows)],totals[0],'total');leaf(section[len(rows)+1],totals[1],'total')
 container(annex[2],('ct9',),{},'section');leaf(annex[2][0],spec['ct9'],'total')
 leaves=sum(1 for node in root.iter() if len(node)==0)
 if leaves!=spec['totalLeaves']:reject('LEAF_COUNT','pluc')
 return {'caseId':case_id,'purchaseRows':len(spec['purchases']),'saleRows':len(spec['sales']),'totalLeafCount':spec['totalLeaves'],'taxLeafCount':spec['taxLeaves']}

def strip_annex(root):
 """Remove the already validated annex from an IN-MEMORY copy only."""
 ns='{'+NS+'}';pluc=root.find('./'+ns+'HSoKhaiThue/'+ns+'PLuc')
 if pluc is None or len(pluc)!=1:reject('STRUCTURE','pluc')
 pluc.remove(pluc[0]);pluc.text=None
 return root
