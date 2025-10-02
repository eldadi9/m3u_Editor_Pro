# logo.py
import os
import json
import threading
import os
import json

# same path logic as in your V3 script
LOGO_DB_PATH = os.path.join(os.path.dirname(__file__), "logos_db.json")


# === טעינה חד פעמית וקאש למסד הלוגואים ===
_LOGO_DB = None
_LOGO_DB_ERR = None
_LOGO_DB_LOCK = threading.Lock()
_LOGO_CACHE_LOCAL = {}
_SAVE_LOCK = threading.Lock()

def _load_logo_db_once():
    """
    טוען את logos_db.json פעם אחת לכל ריצה.
    אם יש שגיאה, מדפיס פעם אחת בלבד וממשיך עם DB ריק.
    """
    global _LOGO_DB, _LOGO_DB_ERR
    if _LOGO_DB is not None or _LOGO_DB_ERR is not None:
        return _LOGO_DB or {}
    with _LOGO_DB_LOCK:
        if _LOGO_DB is not None or _LOGO_DB_ERR is not None:
            return _LOGO_DB or {}
        try:
            if not os.path.exists(LOGO_DB_PATH):
                _LOGO_DB = {}
            else:
                with open(LOGO_DB_PATH, "r", encoding="utf-8") as f:
                    _LOGO_DB = json.load(f)
        except Exception as e:
            _LOGO_DB_ERR = str(e)
            print("[LOGO] Failed to load logo DB once. Skipping logo injection. Error:", _LOGO_DB_ERR)
            _LOGO_DB = {}
        return _LOGO_DB

def _safe_get_saved_logo(channel_name):
    """
    עטיפה בטוחה שמחזירה לוגו מה־DB הטעון פעם אחת, עם קאש ברמת תהליך.
    לא זורקת חריגות החוצה.
    """
    try:
        key = (channel_name or "").strip()
        if key in _LOGO_CACHE_LOCAL:
            return _LOGO_CACHE_LOCAL[key]
        db = _load_logo_db_once()
        v = db.get(key) if isinstance(db, dict) else None
        logo = v[0] if isinstance(v, list) and v else (v if isinstance(v, str) else None)
        _LOGO_CACHE_LOCAL[key] = logo
        return logo
    except Exception:
        return None


def load_logo_cache():
    path = os.path.join(os.path.dirname(__file__), "logos_db.json")
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"⚠ שגיאה בטעינת logos_db.json: {e}")
        return {}  # חזרה לקובץ ריק במקום קריסה


def save_logo_for_channel(channel_name, logo_url):
    """Append logo_url under channel_name if not already present."""
    try:
        with _SAVE_LOCK:
            # עבד מול ה־DB שבזיכרון אם נטען כבר, אחרת טען פעם אחת
            db = _load_logo_db_once()
            # ודא מבנה
            lst = db.get(channel_name, [])
            if isinstance(lst, str):
                lst = [lst]
            if logo_url not in lst:
                lst.append(logo_url)
                db[channel_name] = lst
                # כתיבה אטומית לקובץ
                tmp = LOGO_DB_PATH + ".tmp"
                with open(tmp, "w", encoding="utf-8") as f:
                    json.dump(db, f, indent=2, ensure_ascii=False)
                os.replace(tmp, LOGO_DB_PATH)
    except Exception as e:
        print("[logo.py] error saving logo:", e)



def is_israeli_channel(category, name):
    """Return True if channel/category contains Hebrew/Israeli keywords."""
    keywords = [
        'ישראל', 'israel', 'ערוץ', 'עברי', 'hot', 'yes', 'kan', 'keshet', 'reshet',
        'i24', 'channel 9', 'iptv israel'
    ]
    text = f"{category} {name}".lower()
    return any(kw in text for kw in keywords)


def get_saved_logo(channel_name):
    """Return first saved logo URL or None."""
    db = _load_logo_db_once()
    v = db.get(channel_name)
    if isinstance(v, list):
        return v[0] if v else None
    if isinstance(v, str):
        return v
    return None



# ✅ פונקציה חדשה – החדרת לוגו לשורה אם חסר
def inject_logo_to_line(line, channel_name):
    """
    מחזיר את השורה עם tvg-logo אם היה חסר ונמצא לוגו.
    שקט במקרה של כשל בטעינת DB, כולל קאש לערוצים שכבר נבדקו.
    """
    try:
        if not isinstance(line, str):
            return line
        if not line.startswith("#EXTINF:") or 'tvg-logo="' in line:
            return line

        logo = _safe_get_saved_logo(channel_name)
        if isinstance(logo, str) and logo.startswith("http"):
            return line.replace("#EXTINF:-1", f'#EXTINF:-1 tvg-logo="{logo}"', 1)

        return line
    except Exception:
        return line


