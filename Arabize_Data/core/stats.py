import json, re
from pathlib import Path
def translation_stats(path, total):
    data=json.loads(Path(path).read_text(encoding='utf-8'))
    values=list(data.get('translations',data).values())
    entries=sum(isinstance(v,str) and bool(v.strip()) for v in values)
    words=sum(len(re.findall(r'[\u0600-\u06ff\ufb50-\ufdff\ufe70-\ufeff]+',v)) for v in values if isinstance(v,str))
    return {'entries':entries,'words':words,'total':total,'percent':(entries/total*100 if total else 0)}
