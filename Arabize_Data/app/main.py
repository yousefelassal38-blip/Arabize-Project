# -*- coding: utf-8 -*-
import sys,json,ctypes,threading,traceback,re
from pathlib import Path
import customtkinter as ctk
from tkinter import filedialog,messagebox
from core.registry import GameRegistry
from core.stats import translation_stats
from core.settings import Settings
from core.logging_config import configure
HERE=Path(__file__).resolve().parent.parent
C={'bg':'#090C11','panel':'#111720','card':'#182230','line':'#2A394B','text':'#F7F9FC','muted':'#9AA8B8','orange':'#F5A524','green':'#3DDC97','red':'#FF6B81','blue':'#5BA7FF'}
T={
'ar':{'tag':'منصة تعريب الألعاب','library':'مكتبة الألعاب','choose':'اختر لعبة للمتابعة','path':'مسار تثبيت اللعبة','browse':'تصفح','entries':'النصوص','words':'الكلمات','coverage':'التقدم','backup':'النسخة الاحتياطية','none':'غير موجودة','exists':'موجودة','scan':'فحص الملفات','install':'تثبيت التعريب','restore':'إنشاء حزمة أمان','initial':'اختر المسار ثم ابدأ الفحص','unchecked':'غير مفحوص','compatible':'متوافق','bad':'غير متوافق','admin':'تشغيل كمسؤول','admin_on':'صلاحية المسؤول مفعلة','details':'تفاصيل الفحص','close':'إغلاق','ready':'جاهز','lang':'EN','future':'تثبيت التعريب داخل اللعبة','confirm':'أغلق اللعبة وSteam قبل المتابعة. هل تريد البدء؟','done':'تمت العملية بنجاح.','log':'سجل النشاط','no_log':'لا توجد عمليات بعد.','game_manage':'فحص اللعبة وإنشاء حزمة أمان دون تعديل الملفات','idle':'جاهز للاستخدام','scanning':'جار فحص ملفات اللعبة...','plan':'تثبيت التعريب داخل اللعبة','plan_ready':'تم تثبيت التعريب داخل مجلد اللعبة.','backup_ready':'تم إنشاء حزمة أمان موثقة خارج مجلد اللعبة.' },
'en':{'tag':'Game Localization Platform','library':'Game Library','choose':'Select a game to continue','path':'Game installation folder','browse':'Browse','entries':'Entries','words':'Words','coverage':'Coverage','backup':'Backup','none':'Not found','exists':'Available','scan':'Scan files','install':'Install translation','restore':'Create safety pack','initial':'Choose the folder, then run a scan','unchecked':'Not scanned','compatible':'Compatible','bad':'Incompatible','admin':'Run as admin','admin_on':'Administrator enabled','details':'Scan details','close':'Close','ready':'Ready','lang':'ع','future':'Install Arabic into game','confirm':'Close the game and Steam before continuing. Start now?','done':'Operation completed successfully.','log':'Activity log','no_log':'No activity yet.','game_manage':'Scan the game and create a safety pack without changing files','idle':'Ready','scanning':'Scanning game files...','plan':'Install Arabic into game','plan_ready':'Arabic was installed into the game folder.','backup_ready':'Verified safety pack created outside the game folder.' } }
ctk.set_appearance_mode('dark');ctk.set_default_color_theme('dark-blue')
def admin():
 try:return bool(ctypes.windll.shell32.IsUserAnAdmin())
 except:return False
def stats(p):
 try:
  d=json.loads(Path(p).read_text(encoding='utf-8'));v=list(d.get('translations',d).values());e=sum(isinstance(x,str) and x.strip()!='' for x in v);w=sum(len(re.findall(r'[\u0600-\u06FF\uFB50-\uFDFF\uFE70-\uFEFF]+',x)) for x in v if isinstance(x,str));return e,w
 except:return 0,0
class App(ctk.CTk):
 def __init__(self):
  super().__init__();self.lang='ar';self.registry=GameRegistry(HERE/'games.json');self.games=self.registry.games;self.game=self.games[0];self.plugin=self.registry.load(self.game);self.path=ctk.StringVar(value=self.game['default_path']);self.status=ctk.StringVar();self.busy=False;self.log_lines=[]
  self.title('Arabize 6.8.0 Codex Tutorial Continuation');self.geometry('1180x720');self.minsize(1020,680);self.configure(fg_color=C['bg']);self.grid_columnconfigure(0,weight=1);self.grid_rowconfigure(1,weight=1);self.draw()
 def t(self,k):return T[self.lang][k]
 def draw(self):
  saved=self.path.get();
  for w in self.winfo_children():w.destroy()
  top=ctk.CTkFrame(self,height=72,fg_color=C['bg'],corner_radius=0);top.grid(row=0,column=0,sticky='ew',padx=34);top.grid_columnconfigure(1,weight=1)
  ctk.CTkLabel(top,text='ARABIZE',font=('Segoe UI',24,'bold'),text_color=C['orange']).grid(row=0,column=2,pady=20,sticky='e');ctk.CTkLabel(top,text=self.t('tag'),font=('Segoe UI',12),text_color=C['muted']).grid(row=0,column=1,padx=12,sticky='e')
  tools=ctk.CTkFrame(top,fg_color='transparent');tools.grid(row=0,column=0,sticky='w');ctk.CTkButton(tools,text=self.t('lang'),width=48,height=34,corner_radius=17,fg_color=C['card'],hover_color=C['line'],command=self.toggle).pack(side='left',padx=(0,8));ctk.CTkButton(tools,text=self.t('admin_on') if admin() else self.t('admin'),width=170,height=34,corner_radius=9,fg_color=C['card'],hover_color=C['line'],text_color=C['green'] if admin() else C['text'],state='disabled' if admin() else 'normal',command=self.elevate).pack(side='left')
  body=ctk.CTkFrame(self,fg_color=C['bg']);body.grid(row=1,column=0,sticky='nsew',padx=34,pady=(4,18));body.grid_columnconfigure(0,weight=1);body.grid_rowconfigure(0,weight=1)
  side=ctk.CTkFrame(body,width=258,fg_color=C['panel'],corner_radius=18);side.grid(row=0,column=1,sticky='ns',padx=(16,0));side.grid_propagate(False)
  ctk.CTkLabel(side,text=self.t('library'),font=('Segoe UI',19,'bold')).pack(anchor='e',padx=18,pady=(22,4));ctk.CTkLabel(side,text=self.t('choose'),font=('Segoe UI',10),text_color=C['muted']).pack(anchor='e',padx=18,pady=(0,14))
  for g in self.games:ctk.CTkButton(side,text=g.get('short_name', g.get('name', g.get('id', 'Game'))),height=58,corner_radius=12,anchor='e',fg_color=C['card'],hover_color=C['line'],border_width=1,border_color=C['orange'],command=lambda x=g:self.select(x)).pack(fill='x',padx=12,pady=5)
  ctk.CTkLabel(side,text=('لعبة مدعومة حاليًا: 1' if self.lang=='ar' else 'Supported games: 1'),font=('Segoe UI',9),text_color=C['muted']).pack(side='bottom',anchor='e',padx=18,pady=20)
  main=ctk.CTkFrame(body,fg_color=C['panel'],corner_radius=18);main.grid(row=0,column=0,sticky='nsew');main.grid_columnconfigure(0,weight=1);main.grid_rowconfigure(5,weight=1)
  hero=ctk.CTkFrame(main,height=104,fg_color=C['card'],corner_radius=14);hero.grid(row=0,column=0,sticky='ew',padx=18,pady=18);hero.grid_columnconfigure(0,weight=1)
  self.name=ctk.CTkLabel(hero,text=self.game['name'],font=('Segoe UI',22,'bold'));self.name.grid(row=0,column=1,padx=20,pady=(22,2),sticky='e');ctk.CTkLabel(hero,text=self.t('game_manage'),font=('Segoe UI',11),text_color=C['muted']).grid(row=1,column=1,padx=20,pady=(0,20),sticky='e');self.badge=ctk.CTkLabel(hero,text=self.t('unchecked'),width=120,height=32,corner_radius=16,fg_color=C['line'],text_color=C['muted']);self.badge.grid(row=0,column=0,rowspan=2,padx=20,sticky='w')
  form=ctk.CTkFrame(main,fg_color='transparent');form.grid(row=1,column=0,sticky='ew',padx=22);form.grid_columnconfigure(0,weight=1);ctk.CTkLabel(form,text=self.t('path'),font=('Segoe UI',12,'bold')).grid(row=0,column=1,columnspan=2,sticky='e',pady=(0,7));ctk.CTkEntry(form,textvariable=self.path,height=44,corner_radius=10,fg_color='#0B1118',border_color=C['line']).grid(row=1,column=0,columnspan=2,sticky='ew',padx=(0,8));ctk.CTkButton(form,text=self.t('browse'),width=90,height=44,corner_radius=10,fg_color=C['line'],hover_color='#334256',command=self.pick).grid(row=1,column=2)
  stat=ctk.CTkFrame(main,fg_color='transparent');stat.grid(row=2,column=0,sticky='ew',padx=22,pady=18);stat.grid_columnconfigure((0,1,2,3),weight=1);self.val=[]
  for i,title in enumerate([self.t('entries'),self.t('words'),('إجمالي النصوص' if self.lang=='ar' else 'Total strings'),self.t('coverage')]):
   card=ctk.CTkFrame(stat,fg_color=C['card'],corner_radius=12);card.grid(row=0,column=i,sticky='ew',padx=4);ctk.CTkLabel(card,text=title,font=('Segoe UI',9),text_color=C['muted']).pack(anchor='e',padx=13,pady=(12,1));v=ctk.CTkLabel(card,text='0',font=('Segoe UI',17,'bold'));v.pack(anchor='e',padx=13,pady=(0,12));self.val.append(v)
  actions=ctk.CTkFrame(main,fg_color='transparent');actions.grid(row=3,column=0,sticky='ew',padx=22);actions.grid_columnconfigure((0,1,2,3),weight=1);self.remove=ctk.CTkButton(actions,text=('إزالة التعريب' if self.lang=='ar' else 'Remove Arabic'),height=46,corner_radius=11,fg_color='#6B2737',hover_color='#843247',state='disabled',command=self.uninstall_it);self.remove.grid(row=0,column=0,sticky='ew',padx=5);self.restore=ctk.CTkButton(actions,text=self.t('restore'),height=46,corner_radius=11,fg_color=C['line'],hover_color='#334256',text_color=C['text'],state='disabled',command=self.restore_it);self.restore.grid(row=0,column=1,sticky='ew',padx=5);self.install=ctk.CTkButton(actions,text=self.t('plan'),height=46,corner_radius=11,fg_color=C['orange'],hover_color='#D88B12',text_color='#111111',font=('Segoe UI',12,'bold'),state='disabled',command=self.install_it);self.install.grid(row=0,column=2,sticky='ew',padx=5);self.scan=ctk.CTkButton(actions,text=self.t('scan'),height=46,corner_radius=11,fg_color=C['line'],hover_color='#334256',command=self.scan_it);self.scan.grid(row=0,column=3,sticky='ew',padx=5)
  self.translation_progress=ctk.CTkProgressBar(main,height=8,corner_radius=4,fg_color=C['line'],progress_color=C['orange']);self.translation_progress.grid(row=4,column=0,sticky='ew',padx=27,pady=(20,7));self.translation_progress.set(1.0);self.progress_text=ctk.CTkLabel(main,text='20,464 / 20,464  •  100%',font=('Segoe UI',11,'bold'),text_color=C['orange']);self.progress_text.grid(row=5,column=0,sticky='e',padx=27,pady=(0,3));ctk.CTkLabel(main,textvariable=self.status,font=('Segoe UI',10),text_color=C['muted']).grid(row=6,column=0,sticky='ne',padx=27,pady=(0,8))
  self.scan_panel=ctk.CTkFrame(main,fg_color=C['card'],corner_radius=12);self.scan_panel.grid(row=7,column=0,sticky='ew',padx=22,pady=(2,10));self.scan_panel.grid_columnconfigure((0,1,2,3,4,5),weight=1)
  self.check_labels=[]
  check_names=['التشغيل','الملفات','الأحجام','البصمات','الخط','بيانات التعريب'] if self.lang=='ar' else ['Executable','Files','Sizes','Checksums','Font','Localization']
  for i,name in enumerate(check_names):
   lab=ctk.CTkLabel(self.scan_panel,text='○  '+name,height=34,font=('Segoe UI',9),text_color=C['muted']);lab.grid(row=0,column=i,sticky='ew',padx=3,pady=7);self.check_labels.append(lab)
  status_card=ctk.CTkFrame(main,height=54,fg_color='#0B1118',corner_radius=12,border_width=1,border_color=C['line']);status_card.grid(row=8,column=0,sticky='ew',padx=22,pady=(0,18));status_card.grid_columnconfigure(0,weight=1);self.status_dot=ctk.CTkLabel(status_card,text='●',font=('Segoe UI',13),text_color=C['blue']);self.status_dot.grid(row=0,column=1,padx=(15,7),pady=14);self.status_line=ctk.CTkLabel(status_card,text=self.t('idle'),font=('Segoe UI',10),text_color=C['muted']);self.status_line.grid(row=0,column=0,sticky='e',padx=(5,15),pady=14)
  self.path.set(saved);self.refresh_stats();self.status.set(self.t('initial'));self.refresh_backup()
 def refresh_stats(self):
  e,w=(lambda x:(x['entries'],x['words']))(translation_stats(HERE/self.game['data_dir']/'ar_full.json',self.game['total_strings']));total=self.game['total_strings'];percent=(e/total*100) if total else 0;self.translation_entries=e;self.translation_total=total;self.val[0].configure(text=f'{e:,}');self.val[1].configure(text=f'{w:,}');self.val[2].configure(text=f'{total:,}');self.val[3].configure(text=f'{percent:.2f}%',text_color=C['orange']);self.status.set(('تمت ترجمة ' if self.lang=='ar' else 'Translated ')+f'{e:,} / {total:,}'+(' نصًا' if self.lang=='ar' else ' strings'))
 def addlog(self,msg):
  clean=str(msg).replace('\n',' ').strip();self.log_lines.append(clean);(HERE/'arabize.log').write_text('\n'.join(self.log_lines),encoding='utf-8');
  if hasattr(self,'status_line'):self.status_line.configure(text=clean[:110])
 def toggle(self):self.lang='en' if self.lang=='ar' else 'ar';self.draw()
 def select(self,g):self.game=g;self.plugin=self.registry.load(g);self.path.set(g['default_path']);self.draw()
 def pick(self):
  p=filedialog.askdirectory(title=self.t('path'))
  if p:self.path.set(p);self.scan_it()
 def module(self):return self.plugin
 def open_beta_installer(self):
  try:
   import subprocess
   installer=HERE/'arabic_installer_gui.py'
   subprocess.Popen([sys.executable,str(installer)],cwd=str(HERE))
  except Exception as error:self.fail(error)
 def elevate(self):
  try:
   launcher=HERE/'launcher.py';params=f'\"{launcher}\"';result=ctypes.windll.shell32.ShellExecuteW(None,'runas',sys.executable,params,str(HERE),1)
   if result>32:self.after(250,self.destroy)
   else:messagebox.showerror('Arabize',('تعذر تشغيل البرنامج كمسؤول.' if self.lang=='ar' else 'Could not restart as administrator.'))
  except Exception as error:self.fail(error)
 def scan_it(self):
  self.status.set(self.t('scanning'));self.status_line.configure(text=self.t('scanning'));self.status_dot.configure(text_color=C['orange']);self.scan.configure(state='disabled')
  for label in self.check_labels:label.configure(text='○  '+label.cget('text').replace('○  ','').replace('✓  ',''),text_color=C['muted'])
  try:
   result=self.module().scan(self.path.get(),HERE,self.lang);ok=result.valid and result.compatible;self.status.set(result.message);self.badge.configure(text=self.t('compatible') if ok else self.t('bad'),fg_color='#15392B' if ok else '#44202A',text_color=C['green'] if ok else C['red']);self.install.configure(state='normal' if ok else 'disabled');self.restore.configure(state='normal' if ok else 'disabled');self.remove.configure(state='normal' if (Path(self.path.get())/'archives_win64'/'_arabic_beta_backup'/'manifest.json').exists() else 'disabled');self.addlog(result.message);self.refresh_backup();self.status_dot.configure(text_color=C['green'] if ok else C['red'])
   order=['executable','required-files','sizes','tab-checksums','font-entry','localization-assets']
   passed=set(result.checks)
   for i,key in enumerate(order):
    base=self.check_labels[i].cget('text').replace('○  ','').replace('✓  ','')
    self.check_labels[i].configure(text=('✓  ' if key in passed else '○  ')+base,text_color=C['green'] if key in passed else C['muted'])
  except Exception as error:self.fail(error)
  finally:self.scan.configure(state='normal')
 def setprogress(self,p,m):self.after(0,lambda:(self.status.set(m),self.status_dot.configure(text_color=C['orange'] if p<100 else C['green']),self.addlog(m)))
 def job(self,fn,done):
  if self.busy:return
  self.busy=True;self.scan.configure(state='disabled');self.install.configure(state='disabled')
  def run():
   try:fn();self.after(0,done)
   except Exception as e:
    details=traceback.format_exc();self.after(0,lambda error=e,report=details:self.fail(error,report))
   finally:self.after(0,self.finish_job)
  threading.Thread(target=run,daemon=True).start()
 def finish_job(self):
  self.busy=False;self.scan.configure(state='normal');self.scan_it()
 def install_it(self):
  if not messagebox.askyesno('Arabize',self.t('confirm')):return
  try:
   import arabic_installer_core as installer
   def work():return installer.install(self.path.get(),HERE,progress=self.setprogress)
   def done():
    self.status.set(self.t('plan_ready'));self.addlog(self.t('plan_ready'));self.remove.configure(state='normal');messagebox.showinfo('Arabize',self.t('plan_ready'))
   self.job(work,done)
  except Exception as error:self.fail(error)
 def uninstall_it(self):
  ask=('سيتم حذف التعريب واستعادة الملفات الأصلية. متابعة؟' if self.lang=='ar' else 'Arabic will be removed and original files restored. Continue?')
  if not messagebox.askyesno('Arabize',ask):return
  try:
   import arabic_installer_core as installer
   def work():
    if not installer.uninstall(self.path.get(),progress=self.setprogress):raise RuntimeError('لا توجد نسخة احتياطية للاستعادة.')
   def done():
    msg=('تمت إزالة التعريب واستعادة الأصل.' if self.lang=='ar' else 'Arabic removed and originals restored.');self.status.set(msg);self.addlog(msg);self.remove.configure(state='disabled');messagebox.showinfo('Arabize',msg)
   self.job(work,done)
  except Exception as error:self.fail(error)
 def restore_it(self):
  try:
   output=HERE/'backups';pack=self.module().recovery_pack(self.path.get(),output);self.status.set(self.t('backup_ready'));self.addlog(self.t('backup_ready'));messagebox.showinfo('Arabize',self.t('backup_ready')+'\n\n'+str(pack))
  except Exception as error:self.fail(error)
 def refresh_backup(self):
  p=Path(self.path.get())/'archives_win64'/'_arabic_beta_backup'/'manifest.json';has=p.exists()
  if has:self.addlog('توجد نسخة احتياطية سابقة' if self.lang=='ar' else 'An existing backup was detected')
 def fail(self,e,details=None):
  text=details or traceback.format_exc();self.addlog(repr(e));(HERE/'arabize_error.log').write_text(text,encoding='utf-8');messagebox.showerror('Arabize',f'{e}\n\narabize_error.log')
if __name__=='__main__':App().mainloop()
