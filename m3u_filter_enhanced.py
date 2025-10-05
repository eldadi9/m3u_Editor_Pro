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

    def runAutomaticAdvancedFilter(self, lang='he'):
        """
        ✅ סינון מתקדם + למידה אוטומטית חכמה:
           • חוסם ערוצי Adult מוקדם (כולל היוריסטיקה לשמות כמו 'Hot Pleasure', 'Hot and Mean' וכו')
           • לומד רק ערוצים ישראליים חדשים שסווגו (חזקה/מאושרת) וללא כפילויות
           • דילמות בלבד מקפיצות שאלה; חוסר התאמה → Other בלי הודעות
           • מונה 'נוספו ל-EXTRA' מדויק (לפי החזרה מהדיאלוג)
        """
        try:
            from PyQt5.QtWidgets import QMessageBox
            import re

            # ---------- היוריסטיקה משלימה ל־Adult (בלי לשנות את הקובץ הידני) ----------
            def _adult_extra_heuristic(title: str) -> bool:
                low = (title or "").lower()
                # קודם כל – הבודק הרגיל (blocklist/whitelist)
                if self._is_adult_channel(title):
                    return True
                # תוספות שחסרו ב-blocklist: "hot ..." + מילות מין נפוצות, ועוד ביטויים שכיחים
                extra_patterns = [
                    r"\bhot\s+(?:and\s+mean|pleasure|wife\s*\b|wives\b|girls?\b|guys?\b)\b",
                    r"\b(?:fuck|hardcore|softcore)\b",
                    r"\b(?:erotic|fetish)\b",
                    r"\bxxx\b"
                ]
                return any(re.search(p, low) for p in extra_patterns)

            # ---------- ניקוד התאמה לקטגוריה ישראלית ----------
            def _score_for(name: str, cat: str, kw_map: dict) -> float:
                if not name or not cat or cat == 'Other':
                    return 0.0
                low = name.lower()
                score = 0.0

                # מילות מפתח של הקטגוריה
                hits = 0
                for w in kw_map.get(cat, []):
                    if not isinstance(w, str):
                        continue
                    wl = w.strip().lower()
                    if wl and wl in low:
                        hits += 1
                        if f' {wl} ' in f' {low} ':  # התאמה "שלמה"
                            hits += 0.5
                if hits:
                    score += min(0.75, 0.25 * hits)

                # רמזי ספקים/ז'אנרים ישראליים
                provider_hint = {
                    'Hot': [' hot', 'hot ', 'hot-', 'hot/', 'hot cinema'],
                    'Yes': [' yes', 'yes ', 'yes+', 'yes tv', 'yes sport', 'yes docu', 'wiz'],
                    'Partner': ['partner '],
                    'Cellcom': ['cellcom ', ' סלקום'],
                    'Sports': ['sport ', ' sport', 'one ', 'eurosport', 'nba', 'wwe', ' 5 ', '5+'],
                    'Kids': ['nick', 'disney', 'junior', 'baby', 'yaldut', 'yalduti', 'hop', 'luli', 'zoom'],
                    'Music': ['mtv', 'vh1', ' music'],
                    'News': ['kan ', 'knesset', 'keshet', 'reshet', 'i24', 'channel 1', 'channel 11',
                             'channel 12', 'channel 13', 'channel 14', ' ערוץ '],
                }
                for tgt_cat, needles in provider_hint.items():
                    if tgt_cat == cat and any(n in low for n in needles):
                        score = max(score, 0.75)
                if self._is_israeli_name(name):
                    score = max(score, min(0.7, score))
                return min(1.0, score)

            # ---------- שאלה רק בהתאמה חלקית ----------
            def _ask_partial_confirmation(ch_name: str, base_cat: str, score: float) -> bool:
                reply = QMessageBox.question(
                    self.parent,
                    "אישור שיוך (התאמה חלקית)",
                    f"נמצא ערוץ חדש:\n\n{ch_name}\n\n"
                    f"נראה קשור לקטגוריה: {base_cat}\n"
                    f"ניקוד התאמה: {score:.2f}\n\n"
                    f"להוסיף וללמוד ל-EXTRA?",
                    QMessageBox.Yes | QMessageBox.No
                )
                return reply == QMessageBox.Yes

            # ---------- הכנות ----------
            self._run_emojis = {}
            kw_map = self._build_category_keywords(lang)

            # ידועים (כדי לא ללמוד כפולים)
            try:
                from channel_keywords import (
                    CATEGORY_KEYWORDS_EN, CATEGORY_KEYWORDS_HE,
                    EXTRA_CATEGORY_KEYWORDS_EN, EXTRA_CATEGORY_KEYWORDS_HE
                )
            except Exception:
                CATEGORY_KEYWORDS_EN = CATEGORY_KEYWORDS_HE = {}
                EXTRA_CATEGORY_KEYWORDS_EN = EXTRA_CATEGORY_KEYWORDS_HE = {}

            manual_src = CATEGORY_KEYWORDS_HE if lang == 'he' else CATEGORY_KEYWORDS_EN
            extra_src = EXTRA_CATEGORY_KEYWORDS_HE if lang == 'he' else EXTRA_CATEGORY_KEYWORDS_EN

            known_channels = {
                w.strip().lower()
                for d in (manual_src or {}, extra_src or {})
                for _, words in d.items()
                for w in (words or [])
                if isinstance(w, str) and w.strip()
            }

            # מיכלים
            israel_cats = {self._cat_key(base, lang, True): [] for base in kw_map.keys()}
            israel_cats.setdefault(self._cat_key('Other', lang, True), [])
            world_cats = {
                self._cat_key('World Sports', lang, False): [],
                self._cat_key('World Music', lang, False): [],
                self._cat_key('World Movies', lang, False): [],
                self._cat_key('World News', lang, False): [],
                self._cat_key('World Kids', lang, False): [],
                self._cat_key('Other', lang, False): [],
            }

            to_learn = {}  # name -> base category (באנגלית)
            adult_skipped = 0
            total = 0

            # ---------- מעבר על הערוצים ----------
            for _category, channels in self.parent.categories.items():
                for entry in channels:
                    total += 1
                    name = self._extract_name(entry) or ""
                    if not name.strip():
                        continue

                    # ⛔ חסימה מוקדמת לערוצי Adult (כולל ההיוריסטיקה)
                    if _adult_extra_heuristic(name):
                        adult_skipped += 1
                        continue

                    low = name.lower()

                    # כבר קיים במילון → רק מיון, בלי למידה
                    if low in known_channels:
                        if self._is_israeli_name(name):
                            base = self._best_israel_category(name, kw_map) or 'Other'
                            israel_cats.setdefault(self._cat_key(base, lang, True), []).append(entry)
                        else:
                            base = self._world_bucket(name)
                            world_cats.setdefault(self._cat_key(base, lang, False), []).append(entry)
                        continue

                    # חדש: נסיון סיווג
                    if self._is_israeli_name(name):
                        base_guess = self._best_israel_category(name, kw_map) or 'Other'
                        score = _score_for(name, base_guess, kw_map)

                        if score >= 0.75:
                            israel_cats.setdefault(self._cat_key(base_guess, lang, True), []).append(entry)
                            to_learn[name] = base_guess
                        elif score >= 0.35:
                            if _ask_partial_confirmation(name, base_guess, score):
                                israel_cats.setdefault(self._cat_key(base_guess, lang, True), []).append(entry)
                                to_learn[name] = base_guess
                            else:
                                israel_cats[self._cat_key('Other', lang, True)].append(entry)
                        else:
                            israel_cats[self._cat_key('Other', lang, True)].append(entry)
                    else:
                        base = self._world_bucket(name)
                        world_cats.setdefault(self._cat_key(base, lang, False), []).append(entry)

            # ---------- למידה: לשמור ל-EXTRA (רק מה שאושר/חזק) ----------
            added = 0
            if to_learn and hasattr(self, "_learn_new_keywords_smart"):
                ret = self._learn_new_keywords_smart(to_learn, lang)
                if isinstance(ret, dict) and 'added' in ret:
                    added = int(ret['added'] or 0)
                elif isinstance(ret, int):
                    added = ret
                else:
                    added = 0  # דיאלוג בוטל/דלגת על הכל

            # ---------- מיזוג ועדכון UI ----------
            merged = {}
            for d in (israel_cats, world_cats):
                for k, v in d.items():
                    if v:
                        merged[k] = v
            self._update_ui_with_filtered(merged)

            # ---------- סיכום ----------
            QMessageBox.information(
                self.parent, "סינון הושלם",
                f"נמצאו {sum(len(v) for v in merged.values())} ערוצים\n"
                f"נוספו {added} ערוצים חדשים ל-EXTRA\n"
                f"🚫 סוננו {adult_skipped} ערוצי Adult"
            )

        except Exception as e:
            QMessageBox.critical(self.parent, "שגיאה", f"שגיאה בסינון המתקדם:\n{e}")

    def _learn_new_keywords_smart(self, detected_channels, lang="he"):
        """
        למידה מרוכזת עם צ'קבוקסים:
        • מקבץ ערוצים לפי קטגוריה מוצעת
        • מציג דיאלוג מרוכז (_show_bulk_learning_dialog) לבחירה מרובה
        • כותב ל-EXTRA ושומר לקובץ
        • מחזיר {'added': N} כדי שהסיכום יהיה מדויק
        """
        import os, re, json, importlib, sys
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
            return {'added': 0}

        base_key = "CATEGORY_KEYWORDS_HE" if lang == "he" else "CATEGORY_KEYWORDS_EN"
        extra_key = "EXTRA_CATEGORY_KEYWORDS_HE" if lang == "he" else "EXTRA_CATEGORY_KEYWORDS_EN"

        base = getattr(mod, base_key, {}) or {}
        extra = getattr(mod, extra_key, {}) or {}

        # מאגר כל המילים הידועות כדי למנוע כפילויות
        all_known = {k: set(v) for k, v in {**base, **extra}.items()}

        # קיבוץ לפי קטגוריה מוצעת (עם נירמול)
        grouped = {}
        for ch_name, cat in (detected_channels or {}).items():
            clean_cat = self._he_alias(self._normalize_base(cat))
            if not clean_cat or clean_cat.lower() in ("other", "אחר"):
                continue
            # דלג אם כבר קיים
            if any(ch_name.lower() == w.lower() for w in all_known.get(clean_cat, set())):
                continue
            grouped.setdefault(clean_cat, []).append(ch_name)

        if not grouped:
            return {'added': 0}

        # דיאלוג צ'קבוקסים מרוכז (הפונקציה שכבר בנינו)
        result = self._show_bulk_learning_dialog(grouped)
        if not result or not result.get("approved"):
            QMessageBox.information(self.parent, "למידה בוטלה", "לא נוספו ערוצים חדשים (דלגת על הכל או לא סימנת דבר).")
            return {'added': 0}

        approved = result["approved"]  # {cat: [names...]}

        # מיזוג לתוך EXTRA בזיכרון
        for cat, names in approved.items():
            extra.setdefault(cat, [])
            for n in names:
                if n not in extra[cat]:
                    extra[cat].append(n)

        # כתיבה חזרה לקובץ
        try:
            with open(kw_path, "r", encoding="utf-8") as f:
                src = f.read()

            new_block = (
                "\n\n# ------------------------------\n"
                "# EXTRA keywords (auto-learned)\n"
                "# אל תמחק - מתעדכן אוטומטית\n"
                f"EXTRA_CATEGORY_KEYWORDS_HE = {json.dumps(extra if lang == 'he' else getattr(mod, 'EXTRA_CATEGORY_KEYWORDS_HE', {}), ensure_ascii=False, indent=4)}\n"
                f"EXTRA_CATEGORY_KEYWORDS_EN = {json.dumps(extra if lang == 'en' else getattr(mod, 'EXTRA_CATEGORY_KEYWORDS_EN', {}), ensure_ascii=False, indent=4)}\n"
            )
            pattern = r"\n# ------------------------------\n# EXTRA keywords \(auto-learned\)[\s\S]+?(?=\Z)"
            src = re.sub(pattern, new_block, src, flags=re.MULTILINE) if re.search(pattern, src) else src + new_block

            with open(kw_path, "w", encoding="utf-8") as f:
                f.write(src)

            total_added = sum(len(v) for v in approved.values())
            QMessageBox.information(self.parent, "למידה הושלמה",
                                    f"✅ נוספו {total_added} ערוצים חדשים ל-EXTRA.\n"
                                    f"נשמר בהצלחה בקובץ channel_keywords.py")
            return {'added': total_added}

        except Exception as e:
            print(f"❌ Error writing keywords: {e}")
            return {'added': 0}

    def _show_bulk_learning_dialog(self, new_channels_by_cat):
        """
        🧠 חלון למידה קבוצתי חכם:
        ✅ מציג רשימת ערוצים חדשים לפי קטגוריה עם צ׳קבוקסים
        ✅ מסמן אוטומטית את כל הערוצים הרגילים
        ⚠️ ערוצים חשודים כמבוגרים מוצגים באפור ונחסמים מהוספה
        """
        from PyQt5.QtWidgets import (
            QDialog, QVBoxLayout, QLabel, QCheckBox,
            QScrollArea, QWidget, QPushButton, QMessageBox, QHBoxLayout
        )
        from PyQt5.QtCore import Qt
        import re
        from channel_keywords import ADULT_BLOCKLIST, ADULT_WHITELIST

        # --- פונקציית עזר פנימית לזיהוי תוכן למבוגרים ---
        def is_adult_name(name):
            low = name.lower()
            for safe in ADULT_WHITELIST:
                if safe in low:
                    return False
            for pat in ADULT_BLOCKLIST:
                if re.search(pat, low, flags=re.IGNORECASE):
                    return True
            return False

        dlg = QDialog(self.parent)
        dlg.setWindowTitle("למידת ערוצים חדשים (Bulk Learning)")
        dlg.resize(650, 550)

        layout = QVBoxLayout(dlg)

        lbl = QLabel("נמצאו ערוצים חדשים שלא קיימים במילון.\nבחר אילו מהם להוסיף לקטגוריות המוצעות:")
        lbl.setWordWrap(True)
        layout.addWidget(lbl)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        scroll_layout = QVBoxLayout(container)

        checkboxes = []
        adult_count = 0

        # --- מעבר על קטגוריות ---
        for cat, channels in new_channels_by_cat.items():
            cat_lbl = QLabel(f"📺 <b>{cat}</b> ({len(channels)} ערוצים):")
            scroll_layout.addWidget(cat_lbl)

            for ch in channels:
                if is_adult_name(ch):
                    cb = QCheckBox(f"⚠️ {ch} (Adult content - skipped)")
                    cb.setEnabled(False)
                    cb.setStyleSheet("color: gray; font-style: italic;")
                    adult_count += 1
                else:
                    cb = QCheckBox(ch)
                    cb.setChecked(True)
                scroll_layout.addWidget(cb)
                checkboxes.append((cat, ch, cb))

            scroll_layout.addSpacing(10)

        container.setLayout(scroll_layout)
        scroll.setWidget(container)
        layout.addWidget(scroll)

        # --- כפתורי פעולה ---
        btns = QHBoxLayout()
        btn_confirm = QPushButton("✅ אשר נבחרים")
        btn_skip = QPushButton("❌ דלג על הכל")
        btn_cancel = QPushButton("ביטול")
        btns.addWidget(btn_confirm)
        btns.addWidget(btn_skip)
        btns.addWidget(btn_cancel)
        layout.addLayout(btns)

        result = {"approved": {}, "declined": []}

        def on_confirm():
            for cat, ch, cb in checkboxes:
                if not cb.isEnabled():  # מבוגר
                    result["declined"].append(ch)
                    continue
                if cb.isChecked():
                    result["approved"].setdefault(cat, []).append(ch)
                else:
                    result["declined"].append(ch)
            dlg.accept()

        def on_skip():
            for _, ch, cb in checkboxes:
                result["declined"].append(ch)
            dlg.accept()

        def on_cancel():
            result["approved"].clear()
            dlg.reject()

        btn_confirm.clicked.connect(on_confirm)
        btn_skip.clicked.connect(on_skip)
        btn_cancel.clicked.connect(on_cancel)

        dlg.exec_()

        # הודעה לאחר סגירה (אם נמצאו ערוצי Adult)
        if adult_count > 0:
            QMessageBox.warning(
                self.parent,
                "ערוצים למבוגרים זוהו",
                f"⚠️ זוהו {adult_count} ערוצים עם תוכן למבוגרים.\nהם סומנו באפור ולא נלמדו."
            )

        return result

        def on_confirm():
            for cat, ch, cb in checkboxes:
                if cb.isChecked():
                    result["approved"].setdefault(cat, []).append(ch)
                else:
                    result["declined"].append(ch)
            dlg.accept()

        def on_skip():
            for cat, ch, _ in checkboxes:
                result["declined"].append(ch)
            dlg.accept()

        def on_cancel():
            result["approved"].clear()
            dlg.reject()

        btn_confirm.clicked.connect(on_confirm)
        btn_skip.clicked.connect(on_skip)
        btn_cancel.clicked.connect(on_cancel)

        dlg.exec_()
        return result

    def _calculate_match_score(self, name: str, suggested_cat: str, kw_map: dict) -> float:
        """
        ✅ מחשב ציון התאמה (0.0-1.0) בין שם ערוץ לקטגוריה מוצעת
        """
        try:
            low = name.lower()
            keywords = kw_map.get(suggested_cat, [])
            if not keywords:
                return 0.0

            matches = 0
            total_weight = 0

            for kw in keywords:
                kw_low = kw.lower().strip()
                if not kw_low:
                    continue

                total_weight += 1

                # התאמה מדויקת של מילה שלמה
                if f' {kw_low} ' in f' {low} ':
                    matches += 1.0
                # התאמה חלקית
                elif kw_low in low:
                    matches += 0.5

            return matches / total_weight if total_weight > 0 else 0.0
        except:
            return 0.0

    def _ask_category_confirmation(self, channel_name: str, suggested_cat: str, score: float) -> str:
        """
        ✅ מקפיץ חלון שאלה רק למקרים של דילמה (התאמה חלקית)
        """
        from PyQt5.QtWidgets import QMessageBox

        reply = QMessageBox.question(
            self.parent,
            "❓ אישור סיווג",
            f"<b>ערוץ חדש:</b> {channel_name}<br><br>"
            f"<b>קטגוריה מוצעת:</b> {suggested_cat}<br>"
            f"<b>רמת ביטחון:</b> {score * 100:.0f}%<br><br>"
            f"האם לסווג לקטגוריה זו?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        return "yes" if reply == QMessageBox.Yes else "no"

    def _save_to_extra_keywords(self, new_channels: dict, lang: str):
        """
        ✅ שומר ערוצים חדשים ל-EXTRA בסוף הקובץ (לא משולב למעלה)
        """
        import os, json, re

        try:
            base_dir = os.path.dirname(__file__)
            kw_path = os.path.join(base_dir, "channel_keywords.py")

            if not os.path.exists(kw_path):
                return

            # קריאת הקובץ
            with open(kw_path, "r", encoding="utf-8") as f:
                content = f.read()

            # טעינת EXTRA הקיים
            extra_key = f"EXTRA_CATEGORY_KEYWORDS_{lang.upper()}"
            try:
                match = re.search(rf"{extra_key}\s*=\s*(\{{[^}}]*\}})", content, re.DOTALL)
                if match:
                    extra_dict = eval(match.group(1))
                else:
                    extra_dict = {}
            except:
                extra_dict = {}

            # הוספת ערוצים חדשים
            for ch_name, cat in new_channels.items():
                extra_dict.setdefault(cat, [])
                if ch_name not in extra_dict[cat]:
                    extra_dict[cat].append(ch_name)

            # בניית הבלוק החדש
            new_block = (
                f"\n\n# {'=' * 60}\n"
                f"# EXTRA - ערוצים שנוספו אוטומטית (אל תמחק!)\n"
                f"# {'=' * 60}\n"
                f"{extra_key} = {json.dumps(extra_dict, ensure_ascii=False, indent=4)}\n"
            )

            # החלפה או הוספה
            pattern = rf"\n# ={'='}+\n# EXTRA.*?\n{extra_key}\s*=\s*\{{.*?\}}\n"
            if re.search(pattern, content, re.DOTALL):
                content = re.sub(pattern, new_block, content, flags=re.DOTALL)
            else:
                content += new_block

            # כתיבה חזרה
            with open(kw_path, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"✅ נשמרו {len(new_channels)} ערוצים חדשים ל-{extra_key}")
        except Exception as e:
            print(f"❌ שגיאה בשמירת EXTRA: {e}")

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
        ⚙️ טוען CATEGORY_KEYWORDS_* וממזג EXTRA_CATEGORY_KEYWORDS_* (כולל רענון אמיתי מהדיסק).
        ✅ טוען את הקובץ channel_keywords.py בכל ריצה מחדש (לא מתוך cache)
        ✅ מבצע מיזוג חכם של מפת מילות מפתח + EXTRA
        ✅ תומך בעברית ואנגלית
        ✅ מדפיס לוג צבעוני על טעינה מחדש
        """
        import importlib, importlib.util, sys, os, time

        start = time.time()
        base_dir = os.path.dirname(__file__)
        kw_path = os.path.join(base_dir, "channel_keywords.py")
        mod_name = "channel_keywords"

        # --- רענון אמיתי של המודול ---
        if mod_name in sys.modules:
            del sys.modules[mod_name]

        try:
            spec = importlib.util.spec_from_file_location(mod_name, kw_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            elapsed = time.time() - start
            print(f"\n♻️ [Reload] channel_keywords.py reloaded successfully ({elapsed:.2f}s)")
        except Exception as e:
            print(f"❌ Failed to reload channel_keywords.py: {e}")
            return {"Other": []}

        CATEGORY_KEYWORDS_EN = getattr(mod, "CATEGORY_KEYWORDS_EN", {})
        CATEGORY_KEYWORDS_HE = getattr(mod, "CATEGORY_KEYWORDS_HE", {})
        EXTRA_CATEGORY_KEYWORDS_EN = getattr(mod, "EXTRA_CATEGORY_KEYWORDS_EN", {})
        EXTRA_CATEGORY_KEYWORDS_HE = getattr(mod, "EXTRA_CATEGORY_KEYWORDS_HE", {})

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

        print(
            f"🧠 [Keywords] Loaded {len(src)} base + {len(extra_src)} extra categories → total {len(merged)} merged.\n")
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
        """
        מוצאת את הקטגוריה הישראלית המתאימה ביותר לשם הערוץ לפי מילות מפתח.
        אם לא נמצאה התאמה — משתמשת בזיהוי ספקים ישראליים (HOT, YES, Partner וכו')
        לפני שנופלת ל-Other.
        """
        try:
            low = name.lower()
            best = 'Other'
            best_score = 0

            # --- שלב 1: ננסה התאמה לפי מילות מפתח ---
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

            # --- שלב 2: fallback לפי ספקים ישראליים ---
            if best_score < 1:
                if any(x in low for x in ['hot', 'hot3', 'hot cinema']):
                    best = 'Hot'
                elif any(x in low for x in ['yes', 'yes tv', 'yes comedy', 'yes drama']):
                    best = 'Yes'
                elif 'partner' in low:
                    best = 'Partner'
                elif 'cellcom' in low:
                    best = 'Cellcom'
                elif any(x in low for x in ['keshet', '12']):
                    best = 'News'
                elif any(x in low for x in ['reshet', '13']):
                    best = 'News'
                elif any(x in low for x in ['kan', '11', 'knesset']):
                    best = 'News'
                elif any(x in low for x in ['sport', 'one']):
                    best = 'Sports'
                elif any(x in low for x in ['kids', 'hop', 'luli', 'zoom', 'disney', 'nick']):
                    best = 'Kids'

            return best
        except Exception as e:
            print(f"⚠️ _best_israel_category error: {e}")
            return 'Other'

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