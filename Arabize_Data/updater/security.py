from pathlib import Path
import hashlib,zipfile
def sha256(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def extract(path,dst):
 dst=Path(dst).resolve();dst.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(path) as z:
  for i in z.infolist():
   q=(dst/i.filename).resolve()
   if '..' in Path(i.filename).parts or (q!=dst and dst not in q.parents):raise ValueError('حزمة غير آمنة')
  z.extractall(dst)
