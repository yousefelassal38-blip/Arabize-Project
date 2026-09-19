from pathlib import Path
import json,urllib.request,tempfile,subprocess,sys,os,hashlib,tkinter as tk
from tkinter import messagebox
from .security import sha256,extract
from .signing import verify
DATA=Path(__file__).resolve().parents[1];ROOT=DATA.parent;KEY=Path(__file__).with_name('public_key.pem')
def version(v):return tuple([int(x) for x in str(v).split('.')]+[0,0,0])[:3]
def get(url,limit=536870912):
 req=urllib.request.Request(url,headers={'User-Agent':'Arabize/7.1'})
 with urllib.request.urlopen(req,timeout=90) as r:
  data=r.read(limit+1)
  if len(data)>limit:raise ValueError('الملف أكبر من الحد')
  return data
def run_update_preflight():
 cfg=json.loads((DATA/'update_config.json').read_text(encoding='utf-8'));current=(DATA/'VERSION').read_text().strip()
 try:
  if not KEY.is_file():raise ValueError('لم تثبت هوية ناشر التحديثات بعد')
  m=json.loads(get(cfg['manifest_url'],1024*1024).decode('utf-8-sig'));verify(m,KEY)
  if version(m['version'])<=version(current):return True
  root=tk.Tk();root.withdraw();notes='\n'.join('• '+x for x in m.get('notes_ar',[]));ok=messagebox.askyesno('تحديث Arabize',f"يتوفر الإصدار {m['version']}\n\n{notes}\n\nتنزيل وتثبيت؟");root.destroy()
  if not ok and not m.get('mandatory'):return True
  stage=Path(tempfile.mkdtemp(prefix='ArabizeUpdate_'));pkg=stage/'u.zip';pkg.write_bytes(get(m['package_url'],int(cfg['max_package_bytes'])))
  if pkg.stat().st_size!=int(m['size']) or sha256(pkg)!=m['sha256']:raise ValueError('فشل التحقق من التحديث')
  payload=stage/'payload';extract(pkg,payload)
  if (payload/'Arabize_Data/VERSION').read_text().strip()!=m['version']:raise ValueError('الإصدار غير مطابق')
  plan=DATA/'user_data/pending_update.json';plan.parent.mkdir(parents=True,exist_ok=True);plan.write_text(json.dumps({'payload':str(payload),'version':m['version']}),encoding='utf-8')
  subprocess.Popen([sys.executable,str(Path(__file__).with_name('installer.py')),str(ROOT),str(plan),str(os.getpid())],creationflags=0x08000000 if os.name=='nt' else 0);return False
 except Exception as e:
  root=tk.Tk();root.withdraw();messagebox.showwarning('Arabize',f'تعذر فحص التحديث الآمن:\n{e}\n\nسيعمل الإصدار الحالي.');root.destroy();return True
