import random
import re
from channel_keywords import ADULT_BLOCKLIST, ADULT_WHITELIST
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt

class M3UFilterEnhanced:
    CATEGORY_EMOJIS = {
        'News': ['📰','📺','🗞️','📻','📡','🎙️'],
        'Sports': ['⚽','🏀','🎾','🏈','⚾','🏐','🥊','🏆','⛳','🏒'],
        'Kids': ['👶','🧸','🎈','🎮','🦄','🎪','🎨','👦','👧','🍭'],
        'Movies': ['🎬','🎥','📽️','🎞️','🍿','🎭','📹','🎦'],
        'Entertainment': ['🎭','🎪','🎯','🎨','🎤','🎸','🎹','🎺'],
        'Music': ['🎵','🎶','🎼','🎧','🎤','📻','🎸','🎹','🎺','🥁'],
        'Documentaries': ['📚','🌍','🔬','🔭','🗿','🏛️','📖','🔍'],
        'Nature': ['🌳','🌲','🌴','🐾','🦁','🐘','🦒','🌺','🌻','🌿'],
        'Yes': ['📺','✨','⭐','🌟','💫'],
        'Hot': ['🔥','🌶️','💥','⚡','🎯'],
        'Partner': ['📱','📞','💻','📡','🔗'],
        'Cellcom': ['📲','📶','📳','📴','📵'],
        'Free Tv': ['🆓','📺','📡','🎥','🎬'],
        'Other': ['✨','⭐','🚀','🎯','📺','🎉','🎊','🧩'],
        'World Sports': ['🌍⚽','🏃','🏊','🚴','🤸','⛷️'],
        'World Music': ['🌎🎵','🎸','🥁','🎻','🎺','🎷'],
        'World Movies': ['🌏🎬','🎥','📽️','🎞️','🍿'],
        'World News': ['🌐📰','🗞️','📡','🎙️','📻'],
        'World Kids': ['🌍👶','🧸','🎈','🎮','🦄'],
        'World Documentaries': ['🌍📚', '🌎🔬', '🌐🧠', '📖🗿'],
        'World Nature': ['🌍🌳', '🌎🐘', '🌐🌺', '🌴🌿'],
        'World Series': ['🌍📺', '🌎🌟', '🌐✨', '📡🗺️'],
        'World UHD': ['🌍📺', '🌎4K', '🌐UHD', '💎📡'],

    }

    HE_DISPLAY = {
        'News': 'חדשות',
        'Sports': 'ספורט',
        'Kids': 'ערוצי ילדים',
        'Movies': 'סרטים',
        'Entertainment': 'בידור',
        'Music': 'מוזיקה',
        'Documentaries': 'טבע ודוקו',
        'Nature': 'טבע',
        'Yes': 'יס',
        'Hot': 'הוט',
        'Partner': 'פרטנר',
        'Cellcom': 'סלקום',
        'Free Tv': 'Free-TV',
        'World Series': 'סדרות זרות',
        'Other': 'אחר'
    }

    def __init__(self, parent):
        self.parent = parent
        # --- START: הרחבות ישראל - בלי מחיקה ---
        # מצב קיבוץ ישראל: standard / quality / language
        self.grouping_mode_israel = getattr(self, "grouping_mode_israel", "standard")

        # יומן אימותים לערוצים וסיבה
        self.validation_log = getattr(self, "validation_log", [])

        # מדיניות אימות בסיסית
        self.validation_policy = getattr(self, "validation_policy", {
            "drop_if_no_url": True,
            "drop_if_adult": True,
            "drop_if_too_short_name": True
        })

        # חוקים להמרת קטגוריה לפי Regex לפני מילות מפתח
        # tuple: (pattern, target_base)
        self.category_regex_rules = getattr(self, "category_regex_rules", [
            (r"\bViva(\+| Plus| Premium| Vintage)?\b", "Series"),
            (r"\bYes\s*TV\s*Drama\b", "Series"),
            (r"\bYes\s*TV\s*Comedy\b", "Series"),
            (r"\bHOT\s*Cinema\b", "Movies"),
            (r"\bHOT\s*3\b", "Hot"),
            (r"\bKids|Yaldut|Yalduti|HOP|Luli|ZOOM|Disney|Nick", "Kids"),
            (r"\bSport\s*5|\bONE\b|\bEurosport\b", "Sports"),
            (r"\bSting\b", "Sting"),
            (r"\bNext\b", "Next")
        ])
        # --- END: הרחבות ישראל - בלי מחיקה ---

        # emoji_history מחזיק גם ״אימוגי אחרון בכל הרצות״ וגם מפה לריצה הנוכחית
        self.emoji_history = {}
        self._run_emojis = {}  # אימוגי יציב לכל בסיס ב״ריצה״ הנוכחית
        # --- START: הרחבות לא מוחקות ---
        # מצב קיבוץ ברירת מחדל: standard / quality / language
        self.grouping_mode = getattr(self, "grouping_mode", "standard")

        # הרחבת מילונים של קטגוריות ותצוגה, בלי לפגוע בקיים
        try:
            self._extend_category_definitions()
        except Exception:
            pass

        # החלפת world bucket לגרסה מורחבת, בלי למחוק את המקור
        try:
            self._orig_world_bucket = getattr(self, "_world_bucket", None)
            self._world_bucket = self._world_bucket_plus
        except Exception:
            pass
        # --- END: הרחבות לא מוחקות ---


    # -------- Adult content guard (add-only) --------
    def _is_adult_channel(self, name: str) -> bool:
        """
        True אם שם הערוץ מצביע על תוכן למבוגרים בלבד (XXX/פורנו וכו').
        אינו מוחק ערוצים, רק מסמן/מדלג בשכבת הסינון.
        """
        try:
            import re
            low = (name or "").lower()

            # חריגים בטוחים
            for safe in ADULT_WHITELIST:
                if safe in low:
                    return False

            # חיפוש דפוסים חסומים
            for pat in ADULT_BLOCKLIST:
                if re.search(pat, low, flags=re.IGNORECASE):
                    return True

            # היוריסטיקה: אם מופיע 'adult' יחד עם מילות סקס ברורות – חסום
            if "adult" in low:
                if any(x in low for x in ["porn", "sex", "xxx", "18", "hentai", "brazzers",
                                          "playboy", "hustler", "dorcel", "prive", "venus", "red light"]):
                    return True

            return False
        except Exception:
            # אם יש תקלה בזיהוי – לא לחסום כדי להימנע מפגיעה בסינון רגיל
            return False


    # קריאה מהקובץ הראשי
    # קריאה מהקובץ הראשי
    def runAutomaticAdvancedFilter(self, lang='he'):
        """
        סינון מתקדם: ישראל + עולם.
        חידושים:
        1) הזרקת מילות מפתח נוספות דרך _augment_keyword_map.
        2) מנגנון אימות סופי לכל ערוץ.
        3) המרת קטגוריה לפי Regex לפני מילות מפתח.
        4) קיבוץ ישראל לפי איכות או לפי שפה, ללא מחיקת הקטגוריה הבסיסית.
        5) חסימת מבוגרים נשמרת כמו בקיים.
        6) 🚀 למידה אוטומטית של ערוצים חדשים מתוך Others.
        7) ⚡️ שיפור מהירות משמעותי ע"י cache והתאמות חכמות.
        """
        try:
            import time
            t0 = time.time()
            self._run_emojis = {}

            # --- שלב 1: בניית מפת מילות מפתח ---
            kw_map = self._build_category_keywords(lang)
            kw_map = self._augment_keyword_map(kw_map)  # הרחבות קיימות
            if not isinstance(kw_map, dict) or not kw_map:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self.parent, "שגיאה", "קובץ מילות המפתח ריק או לא נטען כראוי.")
                return

            cache_fast = {}

            # --- שלב 2: הכנת מיכלים ---
            israel_cats = {self._cat_key(base, lang, True): [] for base in kw_map.keys()}
            if self._cat_key('Other', lang, True) not in israel_cats:
                israel_cats[self._cat_key('Other', lang, True)] = []

            world_cats = {
                self._cat_key('World Sports', lang, False): [],
                self._cat_key('World Music', lang, False): [],
                self._cat_key('World Movies', lang, False): [],
                self._cat_key('World News', lang, False): [],
                self._cat_key('World Kids', lang, False): [],
                self._cat_key('World Documentaries', lang, False): [],
                self._cat_key('World Nature', lang, False): [],
                self._cat_key('World Series', lang, False): [],
                self._cat_key('World UHD', lang, False): [],
                self._cat_key('Other', lang, False): []
            }

            # --- שלב 3: חסימות ואימותים ---
            blocked_adults = []
            self.validation_log = []
            seen_keys = set()

            for _category, channels in self.parent.categories.items():
                for entry in channels:
                    name = self._extract_name(entry)

                    # 🔒 חסימת מבוגרים
                    if self._is_adult_channel(name):
                        if self.validation_policy.get("drop_if_adult", True):
                            blocked_adults.append(entry)
                            continue

                    # 🧩 אימות ערוץ
                    is_valid, reasons = self._validate_channel_entry(entry, seen_keys)
                    if not is_valid:
                        self.validation_log.append({"entry": entry, "reasons": reasons})
                        critical = any(r in ["no_url", "adult", "empty_name"] for r in reasons)
                        if critical:
                            continue

                    # 🇮🇱 סיווג ערוצים ישראליים
                    if self._is_israeli_name(name):
                        base0 = self._best_israel_category(name, kw_map)
                        base = self._apply_regex_category_override(name, base0, lang)

                        # קיבוץ לפי איכות/שפה
                        suffix = ""
                        if self.grouping_mode_israel == "quality":
                            q = self._detect_quality(name)
                            if q:
                                suffix = self._map_quality_suffix_he(q) if lang == "he" else f" - {q}"
                        elif self.grouping_mode_israel == "language":
                            sub = self._detect_israeli_sublanguage(name)
                            if sub:
                                suffix = self._map_lang_suffix_he(sub) if lang == "he" else f" - {sub}"

                        key = self._cat_key_with_suffix(base, lang, True, suffix)
                        israel_cats.setdefault(key, []).append(entry)
                    else:
                        # 🌍 סיווג ערוצי עולם
                        world_base = self._world_bucket(name)
                        key = self._cat_key(world_base, lang, False)
                        world_cats.setdefault(key, []).append(entry)

            # --- שלב 4: מיזוג קטגוריות ---
            merged = {}
            for d in (israel_cats, world_cats):
                for k, v in d.items():
                    if v:
                        merged[k] = v

            # --- שלב 5: שמירת חסימות ולוגים ---
            setattr(self.parent, "blocked_adults", blocked_adults)
            setattr(self.parent, "validation_log", self.validation_log)

            # --- שלב 6: זיהוי ערוצים שלא זוהו (למידה חכמה) ---
            potential_new = {}
            for cat, ch_list in merged.items():
                if "Other" in cat:
                    for entry in ch_list:
                        name = self._extract_name(entry)
                        guess = self._fast_find_category(name, kw_map, cache_fast)
                        if guess != "Other":
                            potential_new[name] = guess

            if potential_new:
                self._learn_new_keywords(potential_new, lang)

            # --- שלב 7: עדכון UI ---
            self._update_ui_with_filtered(merged)

            # --- שלב 8: לוג ביצועים ---
            t1 = time.time()
            print(f"⚡️ Advanced filter completed in {(t1 - t0):.2f}s ({len(merged)} categories)")

        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self.parent, "שגיאה", f"שגיאה בסינון המתקדם:\n{e}")

        # === 🚀 שיפור מהירות ובינה לקטגוריות חדשות ===
        def _fast_find_category(self, name, kw_map, cache):
            """
            מאתר קטגוריה במהירות ע"י השוואה מושכלת למילות מפתח קיימות.
            משתמש ב־cache למניעת חזרות ומחפש גם התאמות חלקיות.
            """
            if name in cache:
                return cache[name]

            low = name.lower()
            best_cat = "Other"
            for cat, words in kw_map.items():
                for w in words:
                    if w.lower() in low:
                        best_cat = cat
                        break
                if best_cat != "Other":
                    break

            cache[name] = best_cat
            return best_cat

    # === 🚀 שיפור מהירות ובינה לקטגוריות חדשות ===
    def _fast_find_category(self, name, kw_map, cache):
        """
        מאתר קטגוריה במהירות ע"י השוואה מושכלת למילות מפתח קיימות.
        משתמש ב־cache למניעת חזרות ומחפש גם התאמות חלקיות.
        """
        try:
            if not name:
                return "Other"

            if name in cache:
                return cache[name]

            low = name.lower()
            best_cat = "Other"

            for cat, words in kw_map.items():
                for w in words:
                    if not isinstance(w, str):
                        continue
                    if w.lower() in low:
                        best_cat = cat
                        break
                if best_cat != "Other":
                    break

            cache[name] = best_cat
            return best_cat

        except Exception as e:
            print(f"❌ _fast_find_category error: {e}")
            return "Other"

    def _learn_new_keywords(self, new_channels, lang="he"):
        """
        מוסיף מילות מפתח חדשות לקובץ channel_keywords.py בלי AST.
        - טוען את המודול עם importlib
        - ממזג ל-EXTRA_CATEGORY_KEYWORDS_HE/EN
        - כותב חזרה בבטחה
        """
        import os, re, json, importlib, importlib.util, sys
        from PyQt5.QtWidgets import QMessageBox

        base_dir = os.path.dirname(__file__)
        kw_path = os.path.join(base_dir, "channel_keywords.py")
        mod_name = "channel_keywords"
        if base_dir not in sys.path:
            sys.path.insert(0, base_dir)
        try:
            mod = importlib.import_module(mod_name)
        except Exception as e:
            print(f"❌ cannot import channel_keywords: {e}")
            return

        base_key = "CATEGORY_KEYWORDS_HE" if lang == "he" else "CATEGORY_KEYWORDS_EN"
        extra_key = "EXTRA_CATEGORY_KEYWORDS_HE" if lang == "he" else "EXTRA_CATEGORY_KEYWORDS_EN"

        try:
            base = getattr(mod, base_key, {}) or {}
            extra = getattr(mod, extra_key, {}) or {}
        except Exception as e:
            print(f"❌ Failed to load base or extra keywords: {e}")
            return

        merged = {k: list(set(v)) for k, v in {**base, **extra}.items()}

        changed = False
        for ch_name, suggested_cat in new_channels.items():
            reply = QMessageBox.question(
                self.parent,
                "Keyword Learning",
                f"נמצא ערוץ חדש ב-'Others':\n\n{ch_name}\n\nלהוסיף לקטגוריה {suggested_cat}?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                merged.setdefault(suggested_cat, [])
                if ch_name not in merged[suggested_cat]:
                    merged[suggested_cat].append(ch_name)
                    changed = True

        if not changed:
            print("ℹ️ No new keywords confirmed.")
            return

        try:
            with open(kw_path, "r", encoding="utf-8") as f:
                src = f.read()

            new_block = (
                "\n\n# ------------------------------\n"
                "# EXTRA keywords (auto-learned)\n"
                "# אל תמחק - מתעדכן אוטומטית\n"
                f"EXTRA_CATEGORY_KEYWORDS_HE = {json.dumps(merged if lang == 'he' else extra, ensure_ascii=False, indent=4)}\n"
                f"EXTRA_CATEGORY_KEYWORDS_EN = {json.dumps(merged if lang == 'en' else extra, ensure_ascii=False, indent=4)}\n"
            )

            pattern = r"\n# ------------------------------\n# EXTRA keywords \(auto-learned\)[\s\S]+?(?=\Z)"
            src = re.sub(pattern, new_block, src, flags=re.MULTILINE) if re.search(pattern, src) else src + new_block

            with open(kw_path, "w", encoding="utf-8") as f:
                f.write(src)

            QMessageBox.information(self.parent, "עודכן", "✅ הערוצים החדשים נשמרו בקובץ channel_keywords.py")
        except Exception as e:
            print(f"❌ Error writing keywords: {e}")

    # -------- עזר --------

    def chooseIsraelLanguageAndRunAdvanced(self):
        """דיאלוג מינימלי לבחירת שפה לערוצים הישראלים בלבד, ואז ריצה אוטומטית"""
        dlg = QDialog(self.parent)
        dlg.setWindowTitle("בחר שפה לערוצים הישראלים")
        dlg.setFixedSize(320, 160)
        lay = QVBoxLayout(dlg)

        lbl = QLabel("בחר שפת קטגוריות לערוצים הישראלים")
        lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(lbl)

        btn_he = QPushButton("עברית")
        btn_en = QPushButton("English")

        btn_he.setStyleSheet("background-color: black; color: white; font-weight: bold; padding: 10px;")
        btn_en.setStyleSheet("background-color: red; color: white; font-weight: bold; padding: 10px;")

        btn_he.clicked.connect(lambda: (dlg.accept(), self.runAutomaticAdvancedFilter('he')))
        btn_en.clicked.connect(lambda: (dlg.accept(), self.runAutomaticAdvancedFilter('en')))

        lay.addWidget(btn_he)
        lay.addWidget(btn_en)

        dlg.exec_()

    def _normalize_base(self, s):
        # השאר עברית ואנגלית ורווחים בלבד. מסיר אימוגי וסימנים.
        return re.sub(r'[^A-Za-z\u0590-\u05FF ]+', '', s).strip()

    def _he_alias(self, base):
        aliases = {
            # עברית
            'ספורט': 'Sports', 'ספורט ישראלי': 'Sports',
            'חדשות': 'News', 'חדשות ישראליות': 'News',
            'ילדים': 'Kids', 'ערוצי ילדים': 'Kids',
            'סרטים': 'Movies',
            'מוזיקה': 'Music',
            'בידור': 'Entertainment',
            'טבע': 'Nature', 'טבע ודוקו': 'Documentaries', 'דוקו': 'Documentaries',
            'יס': 'Yes', 'הוט': 'Hot',
            'פרטנר': 'Partner', 'סלקום': 'Cellcom',
            'חינם': 'Free Tv', 'אחר': 'Other',
            'סדרות זרות': 'World Series',
            # אנגלית מורחב
            'hot series': 'Hot', 'yes premium': 'Yes',
            'partner tv': 'Partner', 'cellcom tv': 'Cellcom',
            'free tv': 'Free Tv', 'free-tv': 'Free Tv',
            'world series': 'World Series',
            # וריאנטים
            'yes': 'Yes', 'hot': 'Hot', 'partner': 'Partner', 'cellcom': 'Cellcom',
            'series': 'Movies', 'entertainment': 'Entertainment',
            'documentaries': 'Documentaries', 'nature': 'Nature',
            'kids': 'Kids', 'news': 'News', 'sports': 'Sports', 'music': 'Music', 'movies': 'Movies'
        }
        key = base.strip()
        low = key.lower()
        return aliases.get(key, aliases.get(low, base))

    def _build_category_keywords(self, lang):
        """
        טוען CATEGORY_KEYWORDS_* וממזג EXTRA_CATEGORY_KEYWORDS_* אם קיימים.
        """
        from channel_keywords import CATEGORY_KEYWORDS_EN, CATEGORY_KEYWORDS_HE
        try:
            from channel_keywords import EXTRA_CATEGORY_KEYWORDS_EN, EXTRA_CATEGORY_KEYWORDS_HE
        except Exception:
            EXTRA_CATEGORY_KEYWORDS_EN, EXTRA_CATEGORY_KEYWORDS_HE = {}, {}

        src = CATEGORY_KEYWORDS_HE if lang == 'he' else CATEGORY_KEYWORDS_EN
        extra_src = EXTRA_CATEGORY_KEYWORDS_HE if lang == 'he' else EXTRA_CATEGORY_KEYWORDS_EN

        merged = {}
        for d in (src, extra_src):
            for raw_cat, words in (d or {}).items():
                base = self._he_alias(self._normalize_base(raw_cat)) or 'Other'
                merged.setdefault(base, [])
                for w in words:
                    if isinstance(w, str) and w.strip() and w.strip() not in merged[base]:
                        merged[base].append(w.strip())
        merged.setdefault('Other', [])
        return merged

    def _extract_name(self, entry):
        if isinstance(entry, str) and ' (' in entry and entry.endswith(')'):
            return entry.rsplit(' (', 1)[0].strip()
        return str(entry).strip()

    def _is_hebrew(self, txt):
        return any('\u0590' <= c <= '\u05EA' for c in txt)

    def _is_israeli_name(self, name):
        if self._is_hebrew(name):
            return True
        low = name.lower()
        if re.search(r'\bIL\b|\(IL\)|\bIL:|-IL-|\bISR\b|\bisrael\b', low, re.IGNORECASE):
            return True
        providers = [
            'yes','hot','partner','cellcom','sting','next',
            'kan','keshet','reshet','makan','i24','hidabroot','kabbalah',
            'sport 1','sport 2','sport 3','sport 4','sport 5','one',
            'channel 9','channel 11','channel 12','channel 13','channel 14','arutz'
        ]
        return any(p in low for p in providers)

    def _best_israel_category(self, name, kw_map):
        low = name.lower()
        best = 'Other'
        best_score = 0
        for cat, kws in kw_map.items():
            score = 0
            for k in kws:
                k = k.strip().lower()
                if not k:
                    continue
                if k in low:
                    score += 1
                    if f' {k} ' in f' {low} ':
                        score += 0.5
            if score > best_score:
                best_score = score
                best = cat
        return best if best_score >= 1 else 'Other'

    def _world_bucket(self, name):
        low = name.lower()
        sports = ['sport', 'football', 'soccer', 'basketball', 'tennis', 'golf', 'racing', 'boxing', 'ufc', 'nba',
                  'nfl', 'mlb', 'cricket', 'rugby', 'hockey', 'eurosport', 'espn', 'bein', 'sky sports', 'dazn',
                  'match', 'arena']
        music = ['music', 'mtv', 'vh1', 'vevo', 'hits', 'rock', 'pop', 'jazz', 'classical', 'country', 'rap', 'hip hop',
                 'dance', 'edm', 'radio', 'fm']
        movies = ['cinema', 'movie', 'film', 'hbo', 'showtime', 'starz', 'cinemax', 'paramount', 'universal', 'sony',
                  'fox', 'disney', 'netflix', 'amazon', 'action', 'drama', 'comedy', 'thriller', 'horror', 'sci-fi',
                  'romance']
        news = ['news', 'cnn', 'bbc', 'fox news', 'msnbc', 'cnbc', 'bloomberg', 'reuters', 'al jazeera', 'sky news',
                'euronews', 'dw', 'france 24', 'nhk', 'cctv']
        kids = ['kids', 'cartoon', 'disney', 'nickelodeon', 'nick', 'boomerang', 'cartoon network', 'baby', 'junior',
                'toons', 'animation', 'pbs kids', 'cbeebies']
        documentaries = ['documentary', 'docu', 'natgeo', 'history channel', 'biography', 'discovery', 'planet',
                         'civilization']
        nature = ['nature', 'animal', 'wildlife', 'geo', 'planet', 'forest', 'jungle', 'national geographic',
                  'animal planet']
        series = ['series', 'tv series', 'episode', 'season', 'netflix', 'hulu', 'prime', 'hbo max', 'disney+']
        uhd = ['uhd', '4k', 'hdr', 'ultra hd', '2160p']

        def any_in(lst):
            return any(k in low for k in lst)

        if any_in(sports): return 'World Sports'
        if any_in(music):  return 'World Music'
        if any_in(movies): return 'World Movies'
        if any_in(news):   return 'World News'
        if any_in(kids):   return 'World Kids'
        if any_in(documentaries): return 'World Documentaries'
        if any_in(nature): return 'World Nature'
        if any_in(series): return 'World Series'
        if any_in(uhd): return 'World UHD'

        return 'Other'

    def _get_run_emoji(self, base):
        # בוחר אימוגי יציב לבסיס בודד בריצה, ומנסה לא לחזור על האימוגי מהריצה הקודמת
        if base in self._run_emojis:
            return self._run_emojis[base]
        choices = self.CATEGORY_EMOJIS.get(base) or self.CATEGORY_EMOJIS.get('Other', ['📁'])
        prev = self.emoji_history.get(base)
        if prev in choices and len(choices) > 1:
            choices = [c for c in choices if c != prev]
        chosen = random.choice(choices)
        self._run_emojis[base] = chosen
        self.emoji_history[base] = chosen
        return chosen

    def _cat_key(self, base, lang='he', is_israeli=True):
        base_norm = self._normalize_base(base)
        base_eng = self._he_alias(base_norm)  # בסיס פנימי באנגלית
        # תצוגה: עברית לישראלי כשlang='he', אחרת אנגלית
        display = self.HE_DISPLAY.get(base_eng, base_eng) if (is_israeli and lang == 'he') else base_eng
        emoji = self._get_run_emoji(base_eng)
        return f"{display} {emoji}"

    def _update_ui_with_filtered(self, filtered_channels):
        filtered_channels = {k: v for k, v in filtered_channels.items() if v}
        self.parent.categories = filtered_channels
        self.parent.updateCategoryList()
        self.parent.regenerateM3UTextOnly()
        self.parent.categoryList.clear()
        for category, channels in filtered_channels.items():
            self.parent.categoryList.addItem(f"{category} ({len(channels)})")
        total = sum(len(v) for v in filtered_channels.values())
        QMessageBox.information(self.parent, "סינון הושלם", f"נמצאו {total} ערוצים ב-{len(filtered_channels)} קטגוריות")


    # ===========================
    # הרחבות קטגוריות ללא מחיקה
    # ===========================
    def _extend_category_definitions(self):
        """
        מוסיף קטגוריות שלא קיימות במילוני הבסיס, כולל תצוגה בעברית ואימוגי.
        לא מוחק דבר, רק מעדכן.
        """
        extra_emojis = {
            # ישראל - קטגוריות חדשות
            'Series': ['📺','⭐','✨','🎞️'],
            'Reality': ['🎤','🧩','🎯','📺'],
            'Lifestyle': ['🏠','🍽️','🧑‍🍳','✈️'],
            'Science': ['🔬','🧠','🧪','🔭'],
            'Religion': ['⭐','📖','🕯️','🕍'],
            'Business': ['💼','📈','📰'],
            'Tech': ['💻','🛰️','📡'],
            'Cooking': ['🍳','🍲','🧑‍🍳'],
            'Travel': ['✈️','🗺️','🏝️'],
            'Health': ['💪','🩺','🏃'],
            'Education': ['🎓','📚','🧠'],
            'Gaming': ['🎮','🕹️','💥'],
            'Anime': ['🗾','🎌','🎎'],
            'Radio': ['📻','🔊','🎙️'],
            '24/7': ['⏱️','🔁','🕒'],

            # ספקים בישראל
            'Sting': ['🐝','📺','✨'],
            'Next': ['➡️','📺','✨'],

            # ישראל לפי שפה

            'Israeli Russian': ['🪆','📺','❄️'],

            # עולם לפי אזור/שפה

            'World Russian': ['🪆','🌍','📺'],
            'World French': ['🇫🇷','🌍','📺'],
            'World Turkish': ['🇹🇷','🌍','📺'],
            'World Persian': ['🇮🇷','🌍','📺'],
            'World Spanish': ['🇪🇸','🌍','📺'],
            'World Portuguese': ['🇵🇹','🌍','📺'],
            'World German': ['🇩🇪','🌍','📺'],
            'World Italian': ['🇮🇹','🌍','📺'],
            'World Indian': ['🇮🇳','🌍','📺'],
            'World Chinese': ['🇨🇳','🌍','📺'],
            'World African': ['🌍','🪘','📺'],
            'World Balkans': ['🌍','🎶','📺'],
            'World Latin': ['🌎','🎶','📺'],
            'World Religion': ['📖','🌍','🕯️'],
            'World Business': ['💼','🌍','📈'],
            'World Science': ['🔬','🌍','🔭'],
            'World Gaming': ['🎮','🌍','🕹️'],
            'World Anime': ['🎎','🌍','🎌'],
            'World Radio': ['📻','🌍','🔊'],
            'World 24/7': ['⏱️','🌍','🔁'],

            # עולם לפי איכות
            'World FHD': ['📺','1080p','💎'],
            'World HD': ['📺','720p','✨'],
            'World SD': ['📺','SD','▫️'],
        }

        extra_he_display = {
            # ישראל
            'Series': 'סדרות',
            'Reality': 'ריאליטי',
            'Lifestyle': 'לייף סטייל',
            'Science': 'מדע',
            'Religion': 'דת',
            'Business': 'עסקים',
            'Tech': 'טכנולוגיה',
            'Cooking': 'בישול',
            'Travel': 'טיולים',
            'Health': 'בריאות',
            'Education': 'חינוך',
            'Gaming': 'גיימינג',
            'Anime': 'אנימה',
            'Radio': 'רדיו',
            '24/7': '24/7',
            'Sting': 'סטינג',
            'Next': 'נקסט',
            'Israeli Russian': 'ערוצים ישראליים ברוסית',

            # עולם

            'World Russian': 'עו״ל רוסית',
            'World French': 'עו״ל צרפתית',
            'World Turkish': 'עו״ל טורקית',
            'World Persian': 'עו״ל פרסית',
            'World Spanish': 'עו״ל ספרדית',
            'World Portuguese': 'עו״ל פורטוגזית',
            'World German': 'עו״ל גרמנית',
            'World Italian': 'עו״ל איטלקית',
            'World Indian': 'עו״ל הודי',
            'World Chinese': 'עו״ל סיני',
            'World African': 'עו״ל אפריקה',
            'World Balkans': 'עו״ל הבלקן',
            'World Latin': 'עו״ל לטינו',
            'World Religion': 'עו״ל דת',
            'World Business': 'עו״ל עסקים',
            'World Science': 'עו״ל מדע',
            'World Gaming': 'עו״ל גיימינג',
            'World Anime': 'עו״ל אנימה',
            'World Radio': 'עו״ל רדיו',
            'World 24/7': 'עו״ל 24/7',
            'World FHD': 'עו״ל 1080p',
            'World HD': 'עו״ל 720p',
            'World SD': 'עו״ל SD',
        }

        # עדכון מילונים קיימים בלי למחוק
        try:
            self.CATEGORY_EMOJIS.update({k: v for k, v in extra_emojis.items() if k not in self.CATEGORY_EMOJIS})
        except Exception:
            pass

        try:
            self.HE_DISPLAY.update({k: v for k, v in extra_he_display.items() if k not in self.HE_DISPLAY})
        except Exception:
            pass

    # ===========================
    # חיזוק מפת מילות מפתח
    # ===========================
    def _augment_keyword_map(self, kw_map: dict) -> dict:
        """
        מוסיף מילות מפתח לקטגוריות קיימות, ויוצר קטגוריות חדשות אם אין.
        """
        extra = {
            # ישראל - זיהוי תכנים ותתי ז׳אנרים
            'Series': ['series', 'season', 'episode', 'epis', 'mini series', 'limited series', 'sdarot', 'drama series'],
            'Reality': ['reality', 'talent', 'idol', 'survivor', 'big brother', 'beauty', 'chef', 'model', 'makeover'],
            'Lifestyle': ['lifestyle', 'home', 'design', 'style', 'travel', 'food', 'fashion'],
            'Science': ['science', 'discovery', 'nat geo', 'history', 'curiosity', 'knowledge'],
            'Religion': ['hidabroot', 'kabbalah', 'torah', 'judaism', 'kan 33', 'shalom', 'kol b\'rama'],
            'Business': ['business', 'economy', 'finance', 'market', 'money', 'stock'],
            'Tech': ['tech', 'technology', 'startup', 'innovation', 'ai', 'gadget'],
            'Cooking': ['food', 'cooking', 'chef', 'kitchen', 'recipe'],
            'Travel': ['travel', 'tourism', 'trip', 'journey'],
            'Health': ['health', 'fitness', 'wellness', 'medical'],
            'Education': ['education', 'learning', 'school', 'university'],
            'Gaming': ['gaming', 'esports', 'gameplay', 'twitch'],
            'Anime': ['anime', 'otaku', 'manga'],
            'Radio': ['radio', 'fm', 'am', 'live radio'],
            '24/7': ['24/7', '24x7', 'non stop', 'loop'],

            # ספקים בישראל
            'Sting': ['sting', 'sting tv', 'yes sting'],
            'Next': ['next', 'next tv', 'yes next'],

            # ישראל לפי שפה

            'Israeli Russian': ['il ru', 'israeli russian', '9 kana', 'israel plus'],

            # עולם לפי שפה/אזור

            'World Russian': ['russian', 'ru', 'match tv', '1tv', 'ntv', 'rtr', 'tnt', 'ctc'],
            'World French': ['french', 'fr', 'tf1', 'france tv', 'canal+', 'm6'],
            'World Turkish': ['turkish', 'tr', 'trt', 'atv', 'show tv', 'startv', 'fox tr'],
            'World Persian': ['persian', 'farsi', 'ir', 'manoto', 'irib', 'pmc'],
            'World Spanish': ['spanish', 'es', 'latino', 'mexico', 'argentina', 'azteca', 'televisa', 'movistar'],
            'World Portuguese': ['portuguese', 'pt', 'brasil', 'globo', 'sic', 'rtp'],
            'World German': ['german', 'de', 'zdf', 'ard', 'rtl', 'prosieben', 'sky de'],
            'World Italian': ['italian', 'it', 'rai', 'mediaset', 'sky it'],
            'World Indian': ['india', 'hindi', 'star plus', 'sony sab', 'zee', 'colors'],
            'World Chinese': ['chinese', 'cn', 'cctv', 'phoenix', 'tvb'],
            'World African': ['africa', 'supersport', 'sabc', 'dstv'],
            'World Balkans': ['balkan', 'serbia', 'croatia', 'bosnia', 'hrt', 'rts'],
            'World Latin': ['latin', 'latino', 'spanish latino', 'caracol', 'telemundo'],
            'World Religion': ['religion', 'faith', 'christian', 'islam', 'bible', 'church'],
            'World Business': ['business', 'economy', 'market', 'money', 'bloomberg', 'cnbc world'],
            'World Science': ['science', 'discovery', 'nat geo', 'history'],
            'World Gaming': ['gaming', 'esports', 'twitch', 'gameplay'],
            'World Anime': ['anime', 'manga'],
            'World Radio': ['radio', 'fm', 'am'],
            'World 24/7': ['24/7', '24x7', 'non stop', 'loop'],
        }

        # הזרקה למפה קיימת, בלי למחוק מפתחות קיימים
        for cat, words in extra.items():
            base = self._he_alias(self._normalize_base(cat))
            kw_map.setdefault(base, [])
            for w in words:
                if isinstance(w, str) and w.strip() and w.strip().lower() not in [x.lower() for x in kw_map[base]]:
                    kw_map[base].append(w.strip())
        return kw_map

    # ===========================
    # מצבי קיבוץ והגדרות
    # ===========================
    def setGroupingModeStandard(self):
        self.grouping_mode = 'standard'

    def setGroupingModeQuality(self):
        self.grouping_mode = 'quality'

    def setGroupingModeLanguage(self):
        self.grouping_mode = 'language'

    def chooseGroupingModeDialog(self):
        """
        דיאלוג קטן לבחירת מצב קיבוץ: רגיל, איכות, או שפה.
        """
        dlg = QDialog(self.parent)
        dlg.setWindowTitle("בחירת מצב קיבוץ לעולמי")
        dlg.setFixedSize(360, 180)
        lay = QVBoxLayout(dlg)

        lbl = QLabel("בחר אופן קיבוץ לערוצים העולמיים")
        lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(lbl)

        btn_std = QPushButton("רגיל")
        btn_qlt = QPushButton("איכות")
        btn_lang = QPushButton("שפה")

        btn_std.clicked.connect(lambda: (setattr(self, 'grouping_mode', 'standard'), dlg.accept(), self.runAutomaticAdvancedFilter('he')))
        btn_qlt.clicked.connect(lambda: (setattr(self, 'grouping_mode', 'quality'), dlg.accept(), self.runAutomaticAdvancedFilter('he')))
        btn_lang.clicked.connect(lambda: (setattr(self, 'grouping_mode', 'language'), dlg.accept(), self.runAutomaticAdvancedFilter('he')))

        lay.addWidget(btn_std)
        lay.addWidget(btn_qlt)
        lay.addWidget(btn_lang)

        dlg.exec_()

    # ===========================
    # World bucket מורחב
    # ===========================
    def _world_bucket_plus(self, name: str) -> str:
        """
        גרסת קיבוץ עולמי עם זיהוי לפי איכות, שפה/אזור, ותתי ז׳אנרים.
        מכבד group_mode, ונשען על _orig_world_bucket כברירת מחדל.
        """
        low = name.lower()
        def any_in(lst): return any(k in low for k in lst)

        # איכות
        if self.grouping_mode == 'quality':
            if any_in(['2160', 'uhd', '4k', 'ultra hd', 'hdr']): return 'World UHD'
            if any_in(['1080', 'fhd', 'full hd']): return 'World FHD'
            if any_in(['720', 'hd']): return 'World HD'
            return 'World SD'

        # שפה
        if self.grouping_mode == 'language':

            if any_in(['russian', ' ru', 'ru ', 'rus', 'match tv', '1tv', 'rtr', 'ntv']): return 'World Russian'
            if any_in(['french', ' fr', 'tf1', 'm6', 'canal+']): return 'World French'
            if any_in(['turkish', ' tr', 'trt', 'atv', 'startv']): return 'World Turkish'
            if any_in(['persian', 'farsi', ' ir', 'manoto', 'pmc']): return 'World Persian'
            if any_in(['spanish', ' es', 'latino', 'telemundo', 'azteca', 'movistar']): return 'World Spanish'
            if any_in(['portuguese', ' pt', 'brasil', 'globo', 'rtp', 'sic']): return 'World Portuguese'
            if any_in(['german', ' de', 'zdf', 'ard', 'rtl', 'sky de']): return 'World German'
            if any_in(['italian', ' it', 'rai', 'mediaset', 'sky it']): return 'World Italian'
            if any_in(['hindi', 'india', 'tamil', 'telugu', 'zee', 'star plus']): return 'World Indian'
            if any_in(['chinese', ' mandarin', ' cantonese', 'cctv', 'tvb']): return 'World Chinese'
            return 'Other'

        # רגיל - משתמש בבסיס המקורי, ואז מרחיב תתי זיהויים אם חזר Other
        base = 'Other'
        if callable(getattr(self, "_orig_world_bucket", None)):
            try:
                base = self._orig_world_bucket(name)
            except Exception:
                base = 'Other'

        if base != 'Other':
            return base

        # הרחבות רגילות
        if any_in(['radio', ' fm', ' am ', ' dab', 'webradio']): return 'World Radio'
        if any_in(['24/7', '24x7', 'non stop', 'non-stop', 'live 24']): return 'World 24/7'
        if any_in(['religion', 'christian', 'islam', 'bible', 'church']): return 'World Religion'
        if any_in(['business', 'economy', 'market', 'money', 'bloomberg', 'cnbc']): return 'World Business'
        if any_in(['science', 'discovery', 'history', 'nat geo']): return 'World Science'
        if any_in(['gaming', 'esports', 'twitch']): return 'World Gaming'
        if any_in(['anime', 'manga']): return 'World Anime'

        # אזור/שפה
        if any_in(['russian', 'match tv', '1tv', 'rtr', 'ntv', 'ctc']): return 'World Russian'
        if any_in(['french', 'tf1', 'm6', 'canal+']): return 'World French'
        if any_in(['turkish', 'trt', 'atv', 'startv']): return 'World Turkish'
        if any_in(['persian', 'farsi', 'manoto', 'pmc']): return 'World Persian'
        if any_in(['spanish', 'latino', 'movistar', 'telemundo', 'azteca']): return 'World Spanish'
        if any_in(['portuguese', 'globo', 'rtp', 'sic']): return 'World Portuguese'
        if any_in(['german', 'zdf', 'ard', 'rtl']): return 'World German'
        if any_in(['italian', 'rai', 'mediaset']): return 'World Italian'
        if any_in(['india', 'hindi', 'zee', 'star plus']): return 'World Indian'
        if any_in(['chinese', 'cctv', 'tvb']): return 'World Chinese'
        if any_in(['africa', 'supersport', 'sabc']): return 'World African'
        if any_in(['balkan', 'serbia', 'croatia', 'bosnia']): return 'World Balkans'
        if any_in(['latin', 'latino']): return 'World Latin'

        return 'Other'

    # ===========================
    # Israel grouping controls
    # ===========================

    def setIsraelGroupingModeStandard(self):
        self.grouping_mode_israel = "standard"

    def setIsraelGroupingModeQuality(self):
        self.grouping_mode_israel = "quality"

    def setIsraelGroupingModeLanguage(self):
        self.grouping_mode_israel = "language"

    def chooseIsraelGroupingModeDialog(self):
        dlg = QDialog(self.parent)
        dlg.setWindowTitle("בחירת מצב קיבוץ לישראל")
        dlg.setFixedSize(360, 180)
        lay = QVBoxLayout(dlg)
        lbl = QLabel("בחר אופן קיבוץ לערוצים בישראל")
        lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(lbl)
        btn_std = QPushButton("רגיל")
        btn_qlt = QPushButton("איכות")
        btn_lang = QPushButton("שפה")
        btn_std.clicked.connect(lambda: (setattr(self, 'grouping_mode_israel', 'standard'),
                                         dlg.accept(), self.runAutomaticAdvancedFilter('he')))
        btn_qlt.clicked.connect(lambda: (setattr(self, 'grouping_mode_israel', 'quality'),
                                         dlg.accept(), self.runAutomaticAdvancedFilter('he')))
        btn_lang.clicked.connect(lambda: (setattr(self, 'grouping_mode_israel', 'language'),
                                          dlg.accept(), self.runAutomaticAdvancedFilter('he')))
        lay.addWidget(btn_std)
        lay.addWidget(btn_qlt)
        lay.addWidget(btn_lang)
        dlg.exec_()

        # ===========================
        # Quality detection for Israel
        # ===========================

    def _detect_quality(self, name: str) -> str:
        low = (name or "").lower()
        if any(k in low for k in ["2160", "uhd", "4k", "ultra hd", "hdr"]): return "UHD"
        if any(k in low for k in ["1080", "fhd", "full hd"]): return "FHD"
        if re.search(r"\b720\b|\b720p\b|\bhd\b", low): return "HD"
        if any(k in low for k in ["sd", "480", "360"]): return "SD"
        return ""

    def _map_quality_suffix_he(self, q: str) -> str:
        if q == "UHD": return " - 4K"
        if q == "FHD": return " - 1080p"
        if q == "HD":  return " - 720p"
        if q == "SD":  return " - SD"
        return ""

        # ===========================
        # Sublanguage detection (no Arabic)
        # ===========================

    def _detect_israeli_sublanguage(self, name: str) -> str:
        low = (name or "").lower()
        if any(k in low for k in ["channel 9", "israel plus", "russian", "rus"]):
            return "Russian"
        if any(k in low for k in ["english", "eng", "i24", "24 news"]):
            return "English"
        if self._is_hebrew(name):
            return "Hebrew"
        return ""

    def _map_lang_suffix_he(self, sub: str) -> str:
        if sub == "Hebrew": return " - עברית"
        if sub == "Russian": return " - רוסית"
        if sub == "English": return " - אנגלית"
        return ""

        # ===========================
        # Category key with suffix
        # ===========================

    def _cat_key_with_suffix(self, base, lang='he', is_israeli=True, suffix_text=""):
        key = self._cat_key(base, lang, is_israeli)
        if not suffix_text:
            return key
        parts = key.rsplit(" ", 1)
        if len(parts) == 2 and len(parts[1]) <= 2:
            return f"{parts[0]}{suffix_text} {parts[1]}"
        return f"{key}{suffix_text}"

        # ===========================
        # Regex override before keyword match
        # ===========================

    def _apply_regex_category_override(self, name: str, base: str, lang: str) -> str:
        try:
            for pat, target in self.category_regex_rules:
                if re.search(pat, name, re.IGNORECASE):
                    return target
            return base
        except Exception:
            return base

        # ===========================
        # Channel validation
        # ===========================

    def _validate_channel_entry(self, entry, seen_keys: set):
        reasons = []
        try:
            name = self._extract_name(entry) or ""
            if not name.strip():
                reasons.append("empty_name")

            entry_str = str(entry)
            url = ""
            m = re.search(r"(https?://[^\s]+|rtmp://[^\s]+|rtsp://[^\s]+)", entry_str, flags=re.IGNORECASE)
            if m:
                url = m.group(1)

            if not url and self.validation_policy.get("drop_if_no_url", True):
                reasons.append("no_url")
            if self._is_adult_channel(name) and self.validation_policy.get("drop_if_adult", True):
                reasons.append("adult")

            tail = url.split("?")[0][-48:] if url else ""
            key = f"{name.strip().lower()}|{tail.lower()}"
            if key in seen_keys:
                reasons.append("duplicate")
            else:
                seen_keys.add(key)

            if len(name.strip()) < 2 and self.validation_policy.get("drop_if_too_short_name", True):
                reasons.append("too_short")

            return (len([r for r in reasons if r in ["empty_name", "no_url", "adult"]]) == 0, reasons)
        except Exception:
            return (True, reasons)

        # ===========================
        # Validation log API
        # ===========================

    def getValidationLog(self):
        return list(getattr(self, "validation_log", []))

        # ===========================
        # Add regex rule API
        # ===========================

    def addCategoryRegexRule(self, pattern: str, target_base: str):
        try:
            re.compile(pattern)
            self.category_regex_rules.append((pattern, target_base))
            return True
        except Exception:
            return False
