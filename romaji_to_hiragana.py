"""로마자를 히라가나로 변환하는 모듈"""

# 기본 로마자 → 히라가나 매핑 테이블
ROMAJI_TO_HIRAGANA = {
    # 단일 문자
    "a": "あ", "i": "い", "u": "う", "e": "え", "o": "お",
    "ka": "か", "ki": "き", "ku": "く", "ke": "け", "ko": "こ",
    "sa": "さ", "shi": "し", "su": "す", "se": "せ", "so": "そ",
    "ta": "た", "chi": "ち", "tsu": "つ", "te": "て", "to": "と",
    "na": "な", "ni": "に", "nu": "ぬ", "ne": "ね", "no": "の",
    "ha": "は", "hi": "ひ", "fu": "ふ", "he": "へ", "ho": "ほ",
    "ma": "ま", "mi": "み", "mu": "む", "me": "め", "mo": "も",
    "ya": "や", "yu": "ゆ", "yo": "よ",
    "ra": "ら", "ri": "り", "ru": "る", "re": "れ", "ro": "ろ",
    "wa": "わ", "wo": "を", "n": "ん",
    "ga": "が", "gi": "ぎ", "gu": "ぐ", "ge": "げ", "go": "ご",
    "za": "ざ", "ji": "じ", "zu": "ず", "ze": "ぜ", "zo": "ぞ",
    "da": "だ", "di": "ぢ", "du": "づ", "de": "で", "do": "ど",
    "ba": "ば", "bi": "び", "bu": "ぶ", "be": "べ", "bo": "ぼ",
    "pa": "ぱ", "pi": "ぴ", "pu": "ぷ", "pe": "ぺ", "po": "ぽ",
    "kya": "きゃ", "kyu": "きゅ", "kyo": "きょ",
    "sha": "しゃ", "shu": "しゅ", "sho": "しょ",
    "cha": "ちゃ", "chu": "ちゅ", "cho": "ちょ",
    "nya": "にゃ", "nyu": "にゅ", "nyo": "にょ",
    "hya": "ひゃ", "hyu": "ひゅ", "hyo": "ひょ",
    "mya": "みゃ", "myu": "みゅ", "myo": "みょ",
    "rya": "りゃ", "ryu": "りゅ", "ryo": "りょ",
    "gya": "ぎゃ", "gyu": "ぎゅ", "gyo": "ぎょ",
    "ja": "じゃ", "ju": "じゅ", "jo": "じょ",
    "bya": "びゃ", "byu": "びゅ", "byo": "びょ",
    "pya": "ぴゃ", "pyu": "ぴゅ", "pyo": "ぴょ",
    # 촉음 (작은 つ)
    "tta": "った", "tte": "って", "tto": "っと",
    # 장음
    "aa": "ああ", "ii": "いい", "uu": "うう", "ee": "ええ", "oo": "おお",
    # 특수 케이스
    "wa": "わ", "wo": "を", "he": "へ", "e": "え",
}


def romaji_to_hiragana(romaji: str) -> str:
    """
    로마자를 히라가나로 변환합니다.
    
    접두사 매칭을 지원합니다. 예: "a" -> "あ", "ka" -> "か"
    복잡한 케이스는 처리하지 않습니다.
    
    Args:
        romaji: 로마자 문자열 (예: "a", "ka", "shi")
    
    Returns:
        히라가나 문자열 (변환할 수 없으면 원본 반환)
    """
    if not romaji:
        return romaji
    
    romaji_lower = romaji.lower().strip()
    
    # 정확히 일치하는 경우
    if romaji_lower in ROMAJI_TO_HIRAGANA:
        return ROMAJI_TO_HIRAGANA[romaji_lower]
    
    # 접두사 매칭: 입력이 어떤 로마자로 시작하는지 확인
    # 가장 긴 매칭을 찾기 위해 길이 순으로 정렬
    sorted_keys = sorted(ROMAJI_TO_HIRAGANA.keys(), key=len, reverse=True)
    
    # 접두사로 시작하는 가장 긴 매칭 찾기
    for key in sorted_keys:
        if romaji_lower.startswith(key):
            # 매칭된 부분만 변환하고 나머지는 그대로 유지
            return ROMAJI_TO_HIRAGANA[key] + romaji_lower[len(key):]
    
    # 매칭되지 않으면 원본 반환
    return romaji


def is_romaji(text: str) -> bool:
    """
    텍스트가 로마자(영어 알파벳)로만 구성되어 있는지 확인합니다.
    
    Args:
        text: 확인할 텍스트
    
    Returns:
        로마자로만 구성되어 있으면 True
    """
    if not text:
        return False
    
    # 일본어 문자나 한글이 포함되어 있으면 False
    for char in text:
        if not char.isascii() or not (char.isalpha() or char in " '-"):
            return False
    
    return True


def normalize_japanese_input(text: str) -> str:
    """
    일본어 입력을 정규화합니다.
    로마자 입력이면 히라가나로 변환하고, 이미 일본어 문자면 그대로 반환합니다.
    
    Args:
        text: 입력 텍스트
    
    Returns:
        정규화된 텍스트
    """
    if not text:
        return text
    
    # 로마자로만 구성되어 있으면 히라가나로 변환
    if is_romaji(text):
        return romaji_to_hiragana(text)
    
    # 이미 일본어 문자면 그대로 반환
    return text

