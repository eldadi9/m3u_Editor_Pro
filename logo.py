# logo.py
import os
import json
import threading

# same path logic as in your V3 script
LOGO_DB_PATH = os.path.join(os.path.dirname(__file__), "logos_db.json")

def load_logo_cache():
    """Load existing logos_db.json or return empty dict."""
    try:
        with open(LOGO_DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_logo_for_channel(channel_name, logo_url):
    """Append logo_url under channel_name if not already present."""
    try:
        with threading.Lock():
            db = load_logo_cache()
            # ensure list
            lst = db.get(channel_name, [])
            if isinstance(lst, str):
                lst = [lst]
            if logo_url not in lst:
                lst.append(logo_url)
                db[channel_name] = lst
                # atomic write
                tmp = LOGO_DB_PATH + ".tmp"
                with open(tmp, "w", encoding="utf-8") as f:
                    json.dump(db, f, indent=2, ensure_ascii=False)
                os.replace(tmp, LOGO_DB_PATH)
    except Exception as e:
        print(f"[logo.py] error saving logo: {e}")

def is_israeli_channel(category, name):
    """Return True if channel/category contains Hebrew/Israeli keywords."""
    keywords = [
        'ישראל','israel','ערוץ','עברי','hot','yes','kan','keshet','reshet',
        'i24','channel 9','iptv israel'
    ]
    text = f"{category} {name}".lower()
    return any(kw in text for kw in keywords)

def get_saved_logo(channel_name):
    """Return first saved logo URL or None."""
    db = load_logo_cache()
    v = db.get(channel_name)
    if isinstance(v, list):
        return v[0] if v else None
    if isinstance(v, str):
        return v
    return None
