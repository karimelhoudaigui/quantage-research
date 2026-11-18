"""Evict only public model caches, after integrity validation and closed-file checks."""
import hashlib,json,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];RUN=ROOT/'runs/20261115-c22-model-capacity'
validation=json.loads((ROOT/'research/c19-c21-validation-before-cache-eviction.json').read_text());assert validation['all_valid']
groups=[{'main':'research/external/c19-public/models/Qwen_Qwen3-4B-Instruct-2507-Q4_K_M.gguf','sha':'2fde00ce69dd4899c70d020845e2638353015bba0fdf161b3eb965f2bca4464e','url':'https://huggingface.co/bartowski/Qwen_Qwen3-4B-Instruct-2507-GGUF/resolve/ae44f08e1392f39c0e474af10c3ff8355c8b6688/Qwen_Qwen3-4B-Instruct-2507-Q4_K_M.gguf'}, {'main':'research/external/c16-public/models/qwen2.5-1.5b-instruct-q4_k_m.gguf','sha':'6a1a2eb6d15622bf3c96857206351ba97e1af16c30d7a74ee38970e434e9407e','url':'https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/91cad51170dc346986eccefdc2dd33a9da36ead9/qwen2.5-1.5b-instruct-q4_k_m.gguf'}]
report={'date':'2026-11-16','status':'running','validated_before':'research/c19-c21-validation-before-cache-eviction.json','evicted':[],'scope':'unused public GGUF bytes only, including known aliases; raw/source/valid Gitobjects untouched; reproducibility requires public redownload to these paths'}
path=RUN/'storage-additional-v2.json'
def save():path.write_text(json.dumps(report,indent=2)+'\n')
save()
try:
 files=[ROOT/p for p in subprocess.check_output(['rg','--files','--hidden','--no-ignore','research','runs'],cwd=ROOT,text=True).splitlines() if p.endswith('.gguf')]
 for group in groups:
  p=ROOT/group['main'];s=p.stat();aliases=[]
  for q in files:
   if q.is_file() and not q.is_symlink():
    t=q.stat()
    if (t.st_dev,t.st_ino)==(s.st_dev,s.st_ino):aliases.append(q)
  assert len(aliases)==s.st_nlink and p in aliases,'unlisted link: refuse uncertain eviction'
  h=hashlib.sha256()
  with p.open('rb') as f:
   for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
  assert h.hexdigest()==group['sha']
  check=subprocess.run(['lsof','-F','n',str(p)],capture_output=True,text=True,timeout=10)
  assert check.returncode==1 and not check.stdout and not check.stderr,'cache is open'
  for q in aliases:
   t=q.stat();assert (s.st_ino,s.st_size,s.st_mtime_ns)==(t.st_ino,t.st_size,t.st_mtime_ns);q.unlink()
  report['evicted'].append({'sha256_before':h.hexdigest(),'physical_bytes':s.st_size,'paths':[str(q.relative_to(ROOT)) for q in aliases],'closed_by_lsof':True,'restore_url':group['url'],'restore_aliases':'download main path at exact SHA, then recreate listed hardlinks'})
  save()
 report['status']='completed'
except BaseException as e:
 report['status']='failed';report['error']=type(e).__name__+': '+str(e);raise
finally:
 report['free_bytes_after']=shutil.disk_usage(ROOT).free;save()
print(json.dumps({'status':report['status'],'free_GiB':report['free_bytes_after']/2**30,'cache_groups':len(report['evicted'])}))
