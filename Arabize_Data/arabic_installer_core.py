# -*- coding: utf-8 -*-
"""
Core patch logic for the theHunter:COTW Arabic installer.
In-place patch of game72 Arabic strings and the game78 Arabic font.
Small backup (~1MB) enables clean uninstall (no need to keep 900MB arcs).
"""
import struct, json, os
from pathlib import Path

SP = 448
POOLREL = 14_111_712    # updated 2026-09-15 for game v0.14 (Old West Weapon Pack patch)
ALIGN = 0x1000
ORIGINAL_SHA256 = {
    "game72.arc": "36b07bfaab3740e49823e3c8b3af80ac9ac7b0ec16a813b0f1a8ae4f309ac794",
    "game72.tab": "f07d7a200aa2a4e03761212c4666e9ae24578ac761bb0454ab16b8f97105df41",
    "game78.arc": "ca045386152ba88f6b4b3df64923878fd66e534083020259beaf57042ab37f94",
    "game78.tab": "8202e8fe22e81bd892f43e533059b5b4a44d877ff3c975614ed05f901d71b6e9",
}
STR_ENTRY = 157         # game72 entry: the StringLookup ADF (was 157 in v0.13)
FONT_ENTRY = 2529       # game78 entry: font_en.gfx (CFX) (was 2529 in v0.13)
LOGO_ENTRY = 2562       # game78 entry: UI atlas holding the main-menu logo (was 2562 in v0.13)


def _rd(pool, off, n=2000):   # Maximum UTF-8 string scan length used by the source dictionary
    if off < 0 or off >= len(pool):
        return None
    e = pool.find(b'\x00', off, off + n)
    e = e if e != -1 else min(off + n, len(pool))
    try:
        return pool[off:e].decode('utf-8', 'strict')
    except Exception:
        return None


def _tab_entry(tab, idx):
    if idx < 0:
        raise ValueError("TAB entry index cannot be negative")
    o = 0xC + idx * 12
    if o + 12 > len(tab):
        raise ValueError(f"TAB entry {idx} is outside file bounds")
    return struct.unpack_from("<III", tab, o)  # (hash, offset, size)


def _tab_set(tab, idx, offset, size):
    if offset < 0 or size <= 0:
        raise ValueError("Invalid archive offset or entry size")
    o = 0xC + idx * 12
    if o + 12 > len(tab):
        raise ValueError(f"TAB entry {idx} is outside file bounds")
    struct.pack_into("<I", tab, o + 4, offset)
    struct.pack_into("<I", tab, o + 8, size)


def build_string_entry(entry, trans, keyov, hk):
    """Grow the StringLookup pool with Thai. Returns (new_entry_bytes, blen)."""
    entry = bytearray(entry)
    if len(entry) < 120 or struct.unpack_from("<I", entry, 0)[0] != 0x41444620:
        raise RuntimeError("String entry is not a valid ADF entry")
    if struct.unpack_from("<I", entry, 96 + 0x10)[0] != POOLREL:
        raise RuntimeError("Unexpected string-pool layout; game version mismatch")
    pool_base = 96 + POOLREL
    pool = bytes(entry[pool_base:])
    pool_used = struct.unpack_from("<I", entry, 96 + 0x18)[0]
    inst_off = struct.unpack_from("<I", entry, 0x0C)[0]
    total = struct.unpack_from("<I", entry, 0x28)[0]
    if total != len(entry):
        raise RuntimeError("String entry size does not match its ADF header")
    insert_pos = pool_base + pool_used
    if insert_pos > inst_off or insert_pos > len(entry):
        raise RuntimeError("String-pool insertion point is outside the entry")
    required_table_end = SP + 22049 * 8
    if required_table_end > len(entry):
        raise RuntimeError("String table is shorter than the expected 22,049 slots")

    blob = bytearray(); newoffs = {}
    for i in range(22049):    # was 22049 in v0.13 · +33 slots for Old West Weapon Pack
        h = struct.unpack_from("<I", entry, SP + i * 8)[0]
        t = struct.unpack_from("<I", entry, SP + i * 8 + 4)[0]
        en = _rd(pool, t) if 0 < t < len(pool) else None
        kn = hk.get("%08X" % h)
        th = None
        if kn and kn in keyov:
            th = keyov[kn]
        elif en:
            th = trans.get(en)
        if th:
            newoffs[i] = pool_used + len(blob)
            blob.extend(th.encode('utf-8') + b'\x00')
    blen = len(blob)

    new = bytearray(entry[:insert_pos]) + blob + bytearray(entry[insert_pos:])

    def add(off, delta):
        v = struct.unpack_from("<I", new, off)[0]
        struct.pack_into("<I", new, off, v + delta)
    add(96 + 0x18, blen)  # pool_used
    add(0x0C, blen)       # instance_offset
    add(0x14, blen)       # typedef_offset
    add(0x1C, blen)       # stringhash_offset
    add(0x24, blen)       # nametable_offset
    add(0x28, blen)       # total_size
    new_inst_off = struct.unpack_from("<I", new, 0x0C)[0]
    add(new_inst_off + 12, blen)  # instance[0].size
    for i, no in newoffs.items():
        struct.pack_into("<I", new, SP + i * 8 + 4, no)
    return bytes(new), blen


def _sha256(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _strict_original_match(game_root):
    root = Path(game_root) / "archives_win64"
    return all((root / name).is_file() and _sha256(root / name) == digest
               for name, digest in ORIGINAL_SHA256.items())


def arcs(game_root):
    a = Path(game_root) / "archives_win64"
    return a / "game72.arc", a / "game72.tab", a / "game78.arc", a / "game78.tab"


def find_game():
    """Best-effort auto-detect of the COTW install (Epic/Steam). Returns path or ''."""
    import re
    cands = []
    pf = [os.environ.get("ProgramFiles", r"C:\Program Files"),
          os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")]
    for p in pf:
        cands.append(Path(p) / "Epic Games" / "theHunterCallOfTheWild")
        cands.append(Path(p) / "Steam" / "steamapps" / "common" / "theHunterCotW")
        vdf = Path(p) / "Steam" / "steamapps" / "libraryfolders.vdf"
        if vdf.exists():
            try:
                for m in re.findall(r'"path"\s*"([^"]+)"', vdf.read_text(errors='ignore')):
                    cands.append(Path(m.replace('\\\\', '\\')) / "steamapps" / "common" / "theHunterCotW")
            except Exception:
                pass
    for d in "CDEFGH":
        cands.append(Path(f"{d}:/Epic/theHunterCallOfTheWild"))
        cands.append(Path(f"{d}:/Program Files/Epic Games/theHunterCallOfTheWild"))
        cands.append(Path(f"{d}:/SteamLibrary/steamapps/common/theHunterCotW"))
        cands.append(Path(f"{d}:/Games/theHunterCallOfTheWild"))
    for c in cands:
        try:
            if (c / "archives_win64" / "game72.arc").exists():
                return str(c)
        except Exception:
            pass
    return ""


def validate(game_root, moddata):
    """Return dict: valid, message, version_ok, already_installed."""
    root = Path(game_root)
    g72a, g72t, g78a, g78t = arcs(root)
    exe = root / "theHunterCotW_F.exe"
    if (root / "archives_win64" / "_arabic_font_test_backup" / "manifest.json").exists():
        return {"valid": False, "message": "أزل اختبار الخط 0.6 أولاً ثم أعد الفحص"}
    for f in (g72a, g72t, g78a, g78t):
        if not f.exists():
            return {"valid": False, "message": f"لم يتم العثور على {f.name}، اختر مجلد اللعبة الرئيسي"}
    if not exe.exists():
        return {"valid": False, "message": "لم يتم العثور على theHunterCotW_F.exe، اختر مجلد اللعبة الرئيسي"}
    ref = json.loads((Path(moddata) / "refinfo.json").read_text(encoding='utf-8'))
    bkdir = root / "archives_win64" / "_arabic_beta_backup"
    already = (bkdir / "manifest.json").exists()
    sz = g72a.stat().st_size
    version_ok = (sz == ref["game72_arc_size"]) or already
    msg = "تم العثور على لعبة COTW بنجاح"
    if already:
        msg += "  (التعريب مثبت بالفعل، اضغط تثبيت لإعادة التثبيت)"
    elif not version_ok:
        msg += f"  إصدار ملفات اللعبة غير متوافق"
    return {"valid": True, "message": msg, "version_ok": version_ok, "already_installed": already}


def _load_mod(moddata):
    md = Path(moddata)
    required = ("ar_full.json", "overrides_ar.json", "overrides_by_key.json", "hash_keyname.json", "font_en_arabic.gfx", "refinfo.json")
    missing = [name for name in required if not (md / name).is_file()]
    if missing:
        raise FileNotFoundError("Missing Arabize runtime files: " + ", ".join(missing))
    trans_raw = json.loads((md / "ar_full.json").read_text(encoding='utf-8'))
    trans = trans_raw.get("translations", trans_raw) if isinstance(trans_raw, dict) else None
    if not isinstance(trans, dict):
        raise ValueError("ar_full.json must contain a translation dictionary")
    override_raw = json.loads((md / "overrides_ar.json").read_text(encoding='utf-8'))
    ov = override_raw.get("overrides", {}) if isinstance(override_raw, dict) else None
    if not isinstance(ov, dict):
        raise ValueError("overrides_ar.json must contain an overrides dictionary")
    trans = dict(trans)
    trans.update(ov)
    raw_keyov = json.loads((md / "overrides_by_key.json").read_text(encoding='utf-8'))
    keyov = raw_keyov.get("overrides", raw_keyov) if isinstance(raw_keyov, dict) else None
    if not isinstance(keyov, dict):
        raise ValueError("overrides_by_key.json must contain a dictionary")
    hk = json.loads((md / "hash_keyname.json").read_text(encoding='utf-8'))
    if not isinstance(hk, dict):
        raise ValueError("hash_keyname.json must contain a dictionary")
    return trans, keyov, hk


def _install_impl(game_root, moddata, progress=lambda p, m: None):
    check = validate(game_root, moddata)
    root = Path(game_root)
    own_manifest = root / "archives_win64" / "_arabic_beta_backup" / "manifest.json"
    if not own_manifest.exists() and not _strict_original_match(game_root):
        raise RuntimeError("تم إيقاف التثبيت: بصمات ملفات اللعبة لا تطابق النسخة التي تم اختبارها.")
    if not check.get("valid") or not check.get("version_ok"):
        raise RuntimeError(check.get("message", "فشل فحص التوافق"))
    root = Path(game_root)
    g72a, g72t, g78a, g78t = arcs(root)
    bkdir = root / "archives_win64" / "_arabic_beta_backup"
    ref = json.loads((Path(moddata) / "refinfo.json").read_text(encoding='utf-8'))
    expected_clean_72 = ref["game72_arc_size"]
    # 1) if already installed, restore first so we build from the clean base
    #    BUT: if backup manifest is stale (game updated after mod was installed),
    #    the stored clean sizes are wrong and calling uninstall would DAMAGE the new archives.
    if (bkdir / "manifest.json").exists():
        try:
            m = json.loads((bkdir / "manifest.json").read_text())
            manifest_clean72 = m.get("clean72", 0)
            current_g72 = g72a.stat().st_size
            # Heuristic: if current file already matches the CURRENT mod's expected clean size,
            # OR current does NOT match the manifest's clean+patch bounds, backup is stale.
            stale = (current_g72 == expected_clean_72) or (current_g72 < manifest_clean72)
        except Exception:
            stale = True
        if stale:
            progress(2, "اكتشف تحديث للعبة، جار تنظيف النسخة الاحتياطية القديمة بأمان...")
            for p in bkdir.glob("*"):
                try:
                    p.unlink()
                except OSError:
                    pass
            try:
                bkdir.rmdir()
            except OSError:
                pass
            if not _strict_original_match(game_root):
                raise RuntimeError("تم إيقاف التثبيت: النسخة الاحتياطية قديمة وملفات اللعبة الحالية غير موثقة.")
        else:
            progress(2, "جار استعادة الأصل قبل إعادة التثبيت...")
            uninstall(game_root, quiet=True)
    bkdir.mkdir(parents=True, exist_ok=True)

    progress(5, "جار إنشاء نسخة احتياطية...")
    clean72 = g72a.stat().st_size
    clean78 = g78a.stat().st_size
    (bkdir / "game72.tab.bak").write_bytes(g72t.read_bytes())
    (bkdir / "game78.tab.bak").write_bytes(g78t.read_bytes())
    (bkdir / "manifest.json").write_text(json.dumps(
        {"clean72": clean72, "clean78": clean78}))

    # 2) patch game72 strings
    progress(15, "جار تحميل الترجمة العربية...")
    trans, keyov, hk = _load_mod(moddata)
    tab72 = bytearray(g72t.read_bytes())
    _, ro, size = _tab_entry(tab72, STR_ENTRY)
    with open(g72a, "rb") as f:
        f.seek(ro); entry = f.read(size)
    progress(30, "جار تجهيز النصوص العربية...")
    new_entry, blen = build_string_entry(entry, trans, keyov, hk)
    new_off = (clean72 + ALIGN - 1) // ALIGN * ALIGN
    progress(55, "جار تثبيت النصوص العربية...")
    with open(g72a, "r+b") as f:
        f.truncate(clean72)                 # ensure clean base
        f.seek(clean72); f.write(b'\x00' * (new_off - clean72))
        f.write(new_entry)
    _tab_set(tab72, STR_ENTRY, new_off, len(new_entry))
    g72t.write_bytes(tab72)

    # 3) patch game78 font + logo
    progress(75, "جار تثبيت الخط العربي...")
    tab78 = bytearray(g78t.read_bytes())
    # Arabic font: append + retarget; original logo remains unchanged.
    font = (Path(moddata) / "font_en_arabic.gfx").read_bytes()
    if len(font) < 4 or font[:3] != b'CFX':
        raise RuntimeError("Arabic font payload is not a valid CFX file")
    font_off = (clean78 + ALIGN - 1) // ALIGN * ALIGN
    with open(g78a, "r+b") as f:
        f.truncate(clean78)
        f.seek(clean78); f.write(b'\x00' * (font_off - clean78))
        f.write(font)                                    # font append
    _tab_set(tab78, FONT_ENTRY, font_off, len(font))
    g78t.write_bytes(tab78)
    verify72 = g72t.read_bytes()
    verify78 = g78t.read_bytes()
    _, check72_off, check72_size = _tab_entry(verify72, STR_ENTRY)
    _, check78_off, check78_size = _tab_entry(verify78, FONT_ENTRY)
    if (check72_off, check72_size) != (new_off, len(new_entry)):
        raise RuntimeError("Post-install verification failed for Arabic strings")
    if (check78_off, check78_size) != (font_off, len(font)):
        raise RuntimeError("Post-install verification failed for Arabic font")
    if g72a.stat().st_size < new_off + len(new_entry) or g78a.stat().st_size < font_off + len(font):
        raise RuntimeError("Post-install archive size verification failed")
    progress(100, "تم تثبيت التعريب بنجاح!")
    return True


def install(game_root, moddata, progress=lambda p, m: None):
    """Install Arabic and roll back automatically if any write step fails."""
    try:
        return _install_impl(game_root, moddata, progress=progress)
    except Exception as install_error:
        backup = Path(game_root) / "archives_win64" / "_arabic_beta_backup" / "manifest.json"
        rollback_error = None
        if backup.exists():
            try:
                progress(0, "حدث خطأ، جار استعادة ملفات اللعبة الأصلية...")
                uninstall(game_root, quiet=True)
            except Exception as error:
                rollback_error = error
        if rollback_error is not None:
            raise RuntimeError(f"فشل التثبيت، وفشلت الاستعادة التلقائية: {rollback_error}") from install_error
        raise


def uninstall(game_root, quiet=False, progress=lambda p, m: None):
    root = Path(game_root)
    g72a, g72t, g78a, g78t = arcs(root)
    bkdir = root / "archives_win64" / "_arabic_beta_backup"
    man = bkdir / "manifest.json"
    if not man.exists():
        return False
    m = json.loads(man.read_text())
    if not quiet:
        progress(20, "جار استعادة game72...")
    # game72: truncate + restore tab
    with open(g72a, "r+b") as f:
        f.truncate(m["clean72"])
    g72t.write_bytes((bkdir / "game72.tab.bak").read_bytes())
    if not quiet:
        progress(60, "جار استعادة game78 والخط الأصلي...")
    # game78: restore logo bytes + truncate font + restore tab
    with open(g78a, "r+b") as f:
        f.truncate(m["clean78"])
    g78t.write_bytes((bkdir / "game78.tab.bak").read_bytes())
    # remove backup
    for p in bkdir.glob("*"):
        p.unlink()
    bkdir.rmdir()
    if not quiet:
        progress(100, "تمت إزالة التعريب واستعادة الأصل")
    return True
