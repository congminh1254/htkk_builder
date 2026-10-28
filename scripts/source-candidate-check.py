"""Reverify the fixed public baseline, not a claim of fresh release discovery."""
import importlib.util,json,os,pathlib
spec=importlib.util.spec_from_file_location('candidate',pathlib.Path(__file__).with_name('source-candidate.py'));candidate=importlib.util.module_from_spec(spec);spec.loader.exec_module(candidate)
def main():
 root=pathlib.Path(os.environ['RUNNER_TEMP'])/'htkk-source-candidate'
 if root.exists() or root.is_symlink():raise ValueError('DIRECTORY')
 root.mkdir()
 try:
  official=candidate.fetch_resource('https://www.fshare.vn/file/TPW3FMLVAJL1',root/'official.rar',candidate.BASELINE_OFFICIAL_SHA256)
  mirror=candidate.fetch_baseline_mirror(root/'mirror.zip',official['sha256'])
  report={'format':'htkk-pinned-source-reverification-v1','scope':'pinned-baseline-not-new-release-discovery','official':official,'mirror':mirror,'ready':False,'automaticActivation':False}
  (root/'downloads.json').write_text(json.dumps(report)+'\n')
  print(json.dumps({'status':'downloaded-pinned-baseline','officialSha256':official['sha256'],'mirrorSha256':mirror['sha256'],'ready':False}))
 except candidate.CandidateError as error:
  print(json.dumps({'status':'blocked','failureCode':error.code,'httpStatus':error.status,'ready':False}));return 1
 return 0
if __name__=='__main__':raise SystemExit(main())
