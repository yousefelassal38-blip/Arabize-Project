from pathlib import Path
import sys,json,os,time,shutil,subprocess
root=Path(sys.argv[1]);plan=json.loads(Path(sys.argv[2]).read_text());pid=int(sys.argv[3])
for _ in range(80):
 try:os.kill(pid,0);time.sleep(.25)
 except OSError:break
payload=Path(plan['payload']);backup=root/'Arabize_Data/user_data/program_backups'/time.strftime('%Y%m%d_%H%M%S');backup.mkdir(parents=True)
protected={'user_data','backups','logs','.arabize_internal'}
def merge(src,dst):
 for p in src.rglob('*'):
  r=p.relative_to(src)
  if len(r.parts)>1 and r.parts[0]=='Arabize_Data' and r.parts[1] in protected:continue
  q=dst/r
  if p.is_dir():q.mkdir(parents=True,exist_ok=True)
  else:q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
try:
 merge(root/'Arabize_Data',backup/'Arabize_Data');merge(payload,root)
except Exception:merge(backup,root);raise
subprocess.Popen(['cmd','/c',str(root/'تشغيل_Arabize.bat')],cwd=str(root))
