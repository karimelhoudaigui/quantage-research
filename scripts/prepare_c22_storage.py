"""Bounded task-cache preparation before the official 8B acquisition."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
from scripts import continue_c19_comparison as manager
r=Path('runs/20261115-c22-model-capacity');assert r.is_dir();manager.RUN=r;manager.tidy()
needed=5027783488+3*1024**3
record={'free_bytes_initial':shutil.disk_usage('.').free,'minimum_before_download':needed,'cache_evictions':[]}
if shutil.disk_usage('.').free<needed:
 p=Path('research/external/c17-public-v2/models/Qwen3.5-2B-Q4_K_M.gguf');h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 assert h.hexdigest()=='a8b50de00b780c0f3c16f07cb041a1ecd678b6e22fd8cde91e57fe4b5031523b'
 check=subprocess.run(['lsof','-F','n',str(p)],capture_output=True,text=True,timeout=10)
 assert check.returncode==1 and not check.stdout and not check.stderr,'cache is open'
 n=p.stat().st_size;p.unlink()
 record['cache_evictions'].append({'path':str(p),'bytes':n,'sha256_before':h.hexdigest(),'lsof_closed':True,'restore_url':'https://huggingface.co/SoAIHQ/Qwen3.5-2B-GGUF/resolve/377fa65bb36aa83414de1ab3b40f6f15b0324cdc/Qwen3.5-2B-Q4_K_M.gguf','scope':'unused public cache only; no raw/source/evidence removed'})
if shutil.disk_usage('.').free<needed:manager.tidy()
record['free_bytes_after']=shutil.disk_usage('.').free
(r/'storage-preparation.json').write_text(json.dumps(record,indent=2)+'\n')
assert record['free_bytes_after']>=needed,'insufficient reserve; no acquisition/inference'
raise SystemExit(subprocess.call([sys.executable,'scripts/acquire_c22_model.py']))
