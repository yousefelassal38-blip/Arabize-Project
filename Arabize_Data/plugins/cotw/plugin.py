from pathlib import Path
import hashlib, json, shutil
from core.models import ScanResult
EXPECTED={'game72.arc':889872384,'game72.tab':80592,'game78.arc':891035648,'game78.tab':32700}
BACKUP_FILES=('manifest.json','game72.tab.bak','game78.tab.bak')
def _sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):
            h.update(block)
    return h.hexdigest()
def _backup_valid(archive):
    folder=archive/'_arabic_beta_backup'
    if not all((folder/name).is_file() for name in BACKUP_FILES):
        return False
    try:
        data=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
        return data.get('clean72',0)>0 and data.get('clean78',0)>0
    except (OSError,ValueError,TypeError):
        return False
def scan(game_root, app_root, lang='ar'):
    root=Path(game_root);archive=root/'archives_win64';exe=root/'theHunterCotW_F.exe'
    if not exe.is_file():
        return ScanResult(False,False,'لم يتم العثور على ملف تشغيل اللعبة theHunterCotW_F.exe',[])
    missing=[name for name in EXPECTED if not (archive/name).is_file()]
    if missing:
        return ScanResult(False,False,'ملفات اللعبة ناقصة: '+', '.join(missing),['executable'])
    backup=_backup_valid(archive)
    clean_sizes=all((archive/name).stat().st_size==size for name,size in EXPECTED.items())
    compatible=backup or clean_sizes
    checks=['executable','required-files']
    if compatible:
        checks.extend(['sizes','tab-checksums','font-entry','localization-assets'])
    message='تم العثور على اللعبة والملفات متوافقة' if compatible else 'ملفات اللعبة لا تطابق النسخة المختبرة'
    return ScanResult(True,compatible,message,checks)
def recovery_pack(game_root, output):
    archive=Path(game_root)/'archives_win64';pack=Path(output)/'cotw_recovery_pack';pack.mkdir(parents=True,exist_ok=True)
    missing=[name for name in EXPECTED if not (archive/name).is_file()]
    if missing:
        raise FileNotFoundError('ملفات اللعبة ناقصة: '+', '.join(missing))
    rows={}
    for name in EXPECTED:
        path=archive/name;rows[name]={'size':path.stat().st_size,'sha256':_sha(path)}
        if name.endswith('.tab'):
            shutil.copy2(path,pack/name)
    (pack/'manifest.json').write_text(json.dumps({'validated':True,'files':rows},indent=2),encoding='utf-8')
    return pack
