import random
import re
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
        # emoji_history מחזיק גם ״אימוגי אחרון בכל הרצות״ וגם מפה לריצה הנוכחית
        self.emoji_history = {}
        self._run_emojis = {}  # אימוגי יציב לכל בסיס ב״ריצה״ הנוכחית

    # קריאה מהקובץ הראשי
    def runAutomaticAdvancedFilter(self, lang='he'):
        try:
            self._run_emojis = {}

            kw_map = self._build_category_keywords(lang)  # בסיסים באנגלית

            # מיכלים לישראל (תצוגה בעברית אם lang='he') ולעולם (תמיד אנגלית)
            israel_cats = {self._cat_key(base, lang, True): [] for base in kw_map.keys()}
            if self._cat_key('Other', lang, True) not in israel_cats:
                israel_cats[self._cat_key('Other', lang, True)] = []

            world_cats = {
                self._cat_key('World Sports', lang, False): [],
                self._cat_key('World Music', lang, False): [],
                self._cat_key('World Movies', lang, False): [],
                self._cat_key('World News', lang, False): [],
                self._cat_key('World Kids', lang, False): [],
                self._cat_key('Other', lang, False): []
            }

            # מעבר על כל הערוצים
            for _category, channels in self.parent.categories.items():
                for entry in channels:
                    name = self._extract_name(entry)
                    if self._is_israeli_name(name):
                        base = self._best_israel_category(name, kw_map)  # בסיס אנגלי
                        key = self._cat_key(base, lang, True)
                        israel_cats.setdefault(key, []).append(entry)
                    else:
                        world_base = self._world_bucket(name)  # החזר 'World Sports'/'World Music'/.../'Other'
                        key = self._cat_key(world_base, lang, False)  # ← כאן נכנסת השורה ששאלת עליה
                        world_cats.setdefault(key, []).append(entry)

            # מיזוג וסינון ריקות
            merged = {}
            for d in (israel_cats, world_cats):
                for k, v in d.items():
                    if v:
                        merged[k] = v

            self._update_ui_with_filtered(merged)

        except Exception as e:
            QMessageBox.critical(self.parent, "שגיאה", f"שגיאה בסינון המתקדם:\n{e}")

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
        from channel_keywords import CATEGORY_KEYWORDS_EN, CATEGORY_KEYWORDS_HE
        src = CATEGORY_KEYWORDS_HE if lang == 'he' else CATEGORY_KEYWORDS_EN

        agg = {}
        for raw_cat, words in src.items():
            base = self._normalize_base(raw_cat)
            base = self._he_alias(base)
            if not base:
                base = 'Other'
            agg.setdefault(base, [])
            for w in words:
                if isinstance(w, str) and w.strip():
                    agg[base].append(w.strip())
        agg.setdefault('Other', [])
        return agg

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

        def any_in(lst):
            return any(k in low for k in lst)

        if any_in(sports): return 'World Sports'
        if any_in(music):  return 'World Music'
        if any_in(movies): return 'World Movies'
        if any_in(news):   return 'World News'
        if any_in(kids):   return 'World Kids'
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
