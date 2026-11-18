"""Compile our source with the pinned official local Tectonic, no shell escape."""
import hashlib,json,os,resource,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
engine=ROOT/'research/external/tectonic/tectonic';source=ROOT/'paper/main.tex'
meta=json.loads((ROOT/'research/tectonic-acquisition.json').read_text());assert sha(engine)==meta['binary_sha256']
out=ROOT/'paper/build-c19-v4';out.mkdir()
(out/'main.tex').write_bytes(source.read_bytes())
cache=ROOT/'research/external/tectonic/cache';cache.mkdir(exist_ok=True)
command=[str(engine),'--untrusted','--only-cached','--keep-logs','--makefile-rules',str(out/'dependencies.mk'),'--outdir',str(out),str(out/'main.tex')]
env={'PATH':'/usr/bin:/bin:/usr/sbin:/sbin','LANG':'fr_FR.UTF-8','TECTONIC_CACHE_DIR':str(cache)}
before=sha(source);start=time.perf_counter();error=None;code=None
with (out/'stdout.txt').open('x') as a,(out/'stderr.txt').open('x') as b:
 try:code=subprocess.run(command,cwd=ROOT,env=env,stdout=a,stderr=b,timeout=480).returncode
 except Exception as e:error=type(e).__name__+': '+str(e)
result={'command':command,'binary_sha256':sha(engine),'tex_sha256_before':before,'tex_sha256_after':sha(source),'exit_code':code,'error':error,'runtime_seconds':time.perf_counter()-start,'environment_scope':'only PATH,LANG,TECTONIC_CACHE_DIR passed; cache local; no shell escape','outputs':{str(p.relative_to(ROOT)):sha(p) for p in out.iterdir() if p.is_file()},'scope':'compilation checks syntax/layout only, not scientific truth or final refereeing'}
(ROOT/'research/c19-pdf-build-v4.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'exit_code':code,'error':error,'runtime_seconds':result['runtime_seconds']}))
raise SystemExit(0 if code==0 and error is None else 1)
