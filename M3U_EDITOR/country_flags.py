# country_flags.py

def country_code_to_emoji(country_code):
    OFFSET = 127397
    try:
        return chr(ord(country_code[0].upper()) + OFFSET) + chr(ord(country_code[1].upper()) + OFFSET)
    except:
        return ""

COUNTRY_NAME_MAP = {
    "AD": "Andorra",
    "AE": "United Arab Emirates",
    "AF": "Afghanistan",
    "AL": "Albania",
    "AM": "Armenia",
    "AR": "Argentina",
    "AT": "Austria",
    "AU": "Australia",
    "AZ": "Azerbaijan",
    "BE": "Belgium",
    "BG": "Bulgaria",
    "BR": "Brazil",
    "BY": "Belarus",
    "CA": "Canada",
    "CH": "Switzerland",
    "CN": "China",
    "CY": "Cyprus",
    "CZ": "Czech Republic",
    "DE": "Germany",
    "DK": "Denmark",
    "DZ": "Algeria",
    "EG": "Egypt",
    "ES": "Spain",
    "FI": "Finland",
    "FR": "France",
    "GB": "United Kingdom",
    "GE": "Georgia",
    "GR": "Greece",
    "HR": "Croatia",
    "HU": "Hungary",
    "IL": "Israel",
    "IN": "India",
    "IQ": "Iraq",
    "IR": "Iran",
    "IS": "Iceland",
    "IT": "Italy",
    "JO": "Jordan",
    "JP": "Japan",
    "KZ": "Kazakhstan",
    "LT": "Lithuania",
    "LV": "Latvia",
    "MD": "Moldova",
    "MK": "North Macedonia",
    "MT": "Malta",
    "MX": "Mexico",
    "NL": "Netherlands",
    "NO": "Norway",
    "PL": "Poland",
    "PT": "Portugal",
    "RO": "Romania",
    "RU": "Russia",
    "SA": "Saudi Arabia",
    "SE": "Sweden",
    "SI": "Slovenia",
    "SK": "Slovakia",
    "SY": "Syria",
    "TR": "Turkey",
    "UA": "Ukraine",
    "US": "United States",
    "UZ": "Uzbekistan",
    # תוכל להוסיף עוד מדינות לפי הצורך
}

def format_category_with_flag(category_name):
    for code, name in COUNTRY_NAME_MAP.items():
        # בדיקה רגישה לשם המדינה (אם קיים בחלק מהשם)
        if name.lower() in category_name.lower():
            emoji_flag = country_code_to_emoji(code)
            display_text = f"{emoji_flag} {name}"  # לא מוסיף את קוד המדינה
            return display_text, code
    return category_name, None
