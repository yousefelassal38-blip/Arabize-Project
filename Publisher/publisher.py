from pathlib import Path
import tkinter as tk
from tkinter import ttk,messagebox
import json,zipfile,hashlib,datetime,subprocess,shutil,base64,os
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
REPO='yousefelassal38-blip/Arabize-Project'
def canon(m):return json.dumps({k:v for k,v in m.items() if k!='signature'},ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
def keydir():p=Path(os.environ.get('LOCALAPPDATA',Path.home()))/'ArabizePublisher';p.mkdir(parents=True,exist_ok=True);return p
def run(a):
 p=subprocess.run(a,capture_output=True,text=True,encoding='utf-8',errors='replace')
 if p.returncode:raise RuntimeError(p.stderr or p.stdout)
 return p.stdout
class App(tk.Tk):
 def __init__(self):
  super().__init__();self.title('Arabize Publisher');self.geometry('680x520');self.v=tk.StringVar(value='7.1.0');self.n=tk.StringVar();self.m=tk.BooleanVar()
  ttk.Label(self,text='الإصدار').pack(pady=4);ttk.Entry(self,textvariable=self.v).pack(fill='x',padx=20);ttk.Label(self,text='ملاحظات').pack();ttk.Entry(self,textvariable=self.n).pack(fill='x',padx=20);ttk.Checkbutton(self,text='إجباري',variable=self.m).pack()
  for t,f in [('0. فحص GitHub',self.check),('1. تهيئة التوقيع مرة واحدة',self.init),('2. إنشاء نسخة المستخدم الأساسية',self.user),('3. بناء وتوقيع التحديث',self.build),('4. نشر التحديث',self.publish)]:ttk.Button(self,text=t,command=f).pack(fill='x',padx=20,pady=5)
  self.log=tk.Text(self);self.log.pack(fill='both',expand=True,padx=20,pady=10)
 def say(self,x):self.log.insert('end',str(x)+'\\n')
 def check(self):
  try:self.say(run(['gh','auth','status']));messagebox.showinfo('جاهز','GitHub جاهز')
  except Exception as e:messagebox.showerror('ثبت GitHub CLI','نفذ gh auth login\\n'+str(e))
 def init(self):
  k=Ed25519PrivateKey.generate();d=keydir();(d/'private.pem').write_bytes(k.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()));(Path(__file__).parents[1]/'Arabize_Data/updater/public_key.pem').write_bytes(k.public_key().public_bytes(serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo));messagebox.showinfo('نجاح','تمت التهيئة. لا تحذف المفتاح في LocalAppData')
 def pack(self,path,user=False):
  root=Path(__file__).parents[1];skip={'.git','dist','dist_user','user_data','backups','logs','__pycache__','Project_Docs','Tools'}|({'Publisher'} if user else set())
  with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
   for p in root.rglob('*'):
    r=p.relative_to(root)
    if p.is_file() and not any(x in skip for x in r.parts) and (not user or p.name!='تشغيل_ناشر_التحديثات.bat'):z.write(p,r)
 def user(self):
  r=Path(__file__).parents[1];p=r/'dist_user/Arabize_Online_User_Edition.zip';p.parent.mkdir(exist_ok=True);self.pack(p,True);self.say(p)
 def build(self):
  r=Path(__file__).parents[1];v=self.v.get();k=serialization.load_pem_private_key((keydir()/'private.pem').read_bytes(),None);(r/'Arabize_Data/VERSION').write_text(v+'\\n');d=r/'dist';shutil.rmtree(d,ignore_errors=True);d.mkdir();p=d/'Arabize_Update.zip';self.pack(p);h=hashlib.sha256(p.read_bytes()).hexdigest();m={'schema':1,'version':v,'mandatory':self.m.get(),'package_url':f'https://github.com/{REPO}/releases/latest/download/Arabize_Update.zip','sha256':h,'size':p.stat().st_size,'published_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'notes_ar':[self.n.get() or 'تحديث Arabize']};m['signature']=base64.b64encode(k.sign(canon(m))).decode();(d/'update.json').write_text(json.dumps(m,ensure_ascii=False,indent=2));(d/'SHA256SUMS.txt').write_text(h+'  Arabize_Update.zip\\n');self.say('تم البناء')
 def publish(self):
  r=Path(__file__).parents[1];v=self.v.get();d=r/'dist';self.say(run(['gh','release','create','v'+v,str(d/'Arabize_Update.zip'),str(d/'update.json'),str(d/'SHA256SUMS.txt'),'--repo',REPO,'--title','Arabize '+v,'--notes',self.n.get() or 'Arabize update','--latest']))
if __name__=='__main__':App().mainloop()
