"""Remove only old, closed tmp_pack garbage after metadata and ref invariants."""
import json
from pathlib import Path
import re
import shutil
import subprocess
import time

root=Path(__file__).resolve().parents[1]
packs=root/'.git/objects/pack'
count=subprocess.run(['git','count-objects','-vH'],cwd=root,text=True,capture_output=True,check=True)
garbage=set(re.findall(r'garbage found: (\.git/objects/pack/tmp_pack_[A-Za-z0-9]+)',count.stderr))
opened=subprocess.run(['lsof','-F','n','+D',str(packs)],capture_output=True,text=True)
if opened.returncode not in (0,1) or opened.stderr.strip():raise RuntimeError('cannot establish closed files')
open_paths={line[1:] for line in opened.stdout.splitlines() if line.startswith('n')}
now=time.time(); candidates=[]
for name in sorted(garbage):
 p=root/name;st=p.lstat()
 if p.is_symlink() or not p.is_file() or now-st.st_mtime<600 or str(p) in open_paths:continue
 candidates.append({'path':name,'bytes':st.st_size,'mtime_ns':st.st_mtime_ns,'inode':st.st_ino,'age_seconds':now-st.st_mtime})
audit=root/'research/disk-git-temp-audit-v3.json';report=root/'research/disk-git-temp-cleanup-v3.json'
if audit.exists() or report.exists():raise RuntimeError('refuse overwrite')
audit.write_text(json.dumps({'date':'2026-11-15','scope':'metadata only; old600s closed files classified garbage by Git, no contents read','lsof_exit':opened.returncode,'open_temp_paths':sorted(open_paths),'candidates':candidates,'candidate_bytes':sum(x['bytes'] for x in candidates)},indent=2)+'\n')
def refs():return subprocess.check_output(['git','for-each-ref','--format=%(refname) %(objectname)'],cwd=root)
before=refs();removed=[]
for x in candidates:
 p=root/x['path'];s=p.lstat()
 if s.st_ino!=x['inode'] or s.st_size!=x['bytes'] or s.st_mtime_ns!=x['mtime_ns']:raise RuntimeError('candidate changed')
 # Files eligible for deletion must still be closed at the final check.
 check=subprocess.run(['lsof','-F','n',str(p)],capture_output=True,text=True)
 if check.returncode!=1 or check.stdout or check.stderr:raise RuntimeError('file open or lsof failure')
 p.unlink();removed.append(x['path'])
after=refs();assert before==after
report.write_text(json.dumps({'removed_only_closed_old_git_temporary_garbage':True,'files':len(removed),'bytes':sum(x['bytes'] for x in candidates),'removed':removed,'refs_identical':before==after,'free_bytes_after':shutil.disk_usage(root).free,'source_audit':str(audit.relative_to(root))},indent=2)+'\n')
print(json.dumps({'files':len(removed),'free_GiB':shutil.disk_usage(root).free/2**30,'refs_identical':before==after}))
