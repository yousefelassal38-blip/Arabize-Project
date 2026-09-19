import json,base64
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
def canonical(m):return json.dumps({k:v for k,v in m.items() if k!='signature'},ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
def verify(m,path):
 key=serialization.load_pem_public_key(Path(path).read_bytes())
 if not isinstance(key,Ed25519PublicKey):raise ValueError('مفتاح غير صالح')
 key.verify(base64.b64decode(m['signature'],validate=True),canonical(m))
