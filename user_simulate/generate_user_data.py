"""사용자별 문장 데이터 생성 스크립트"""

import random
from pathlib import Path

# 영어 사용자별 선호 단어 및 문장 패턴 정의
USER_PROFILES_EN = {
    "developer": {
        "name": "개발자",
        "preferred_words": {
            "wo": ["word", "work", "working", "workspace"],
            "co": ["code", "computer", "compile", "component"],
            "pr": ["program", "project", "process", "print"],
            "fu": ["function", "future", "full"],
            "cl": ["class", "client", "clear"],
        },
        "sentence_templates": [
            "I need to {word} on this {word2}.",
            "Let me {word} the {word2}.",
            "The {word} is not {word2}.",
            "I will {word} this {word2}.",
            "This {word} needs to be {word2}.",
        ],
    },
    "writer": {
        "name": "작가",
        "preferred_words": {
            "wo": ["world", "wonderful", "words", "wonder"],
            "st": ["story", "still", "start", "strong"],
            "be": ["beautiful", "begin", "believe", "best"],
            "ch": ["character", "change", "chapter", "chance"],
            "th": ["the", "think", "thought", "through"],
        },
        "sentence_templates": [
            "The {word} was {word2}.",
            "In this {word}, we {word2}.",
            "She {word} about the {word2}.",
            "The {word} of the {word2}.",
            "It was a {word} {word2}.",
        ],
    },
    "business": {
        "name": "비즈니스맨",
        "preferred_words": {
            "wo": ["work", "working", "works", "workplace"],
            "me": ["meeting", "member", "message", "method"],
            "pr": ["project", "present", "price", "process"],
            "cl": ["client", "close", "clear", "class"],
            "co": ["company", "complete", "contact", "cost"],
        },
        "sentence_templates": [
            "We need to {word} on this {word2}.",
            "The {word} is important for {word2}.",
            "Let's {word} the {word2}.",
            "This {word} will help {word2}.",
            "The {word} of the {word2}.",
        ],
    },
    "student": {
        "name": "학생",
        "preferred_words": {
            "st": ["study", "student", "start", "still"],
            "le": ["learn", "lesson", "level", "lecture"],
            "ho": ["homework", "hope", "home", "hour"],
            "ex": ["exam", "example", "exercise", "explain"],
            "te": ["teacher", "test", "text", "term"],
        },
        "sentence_templates": [
            "I need to {word} for the {word2}.",
            "The {word} is about {word2}.",
            "I will {word} this {word2}.",
            "This {word} helps me {word2}.",
            "The {word} of the {word2}.",
        ],
    },
    "general": {
        "name": "일반 사용자",
        "preferred_words": {},  # 기본 빈도 사용
        "sentence_templates": [],
    },
}

# 이탈리아어 사용자별 선호 단어 및 문장 패턴 정의
USER_PROFILES_IT = {
    "developer": {
        "name": "개발자",
        "preferred_words": {
            "co": ["codice", "computer", "compilare", "componente"],
            "pr": ["programma", "progetto", "processo", "procedura"],
            "fu": ["funzione", "futuro", "funzionale"],
            "cl": ["classe", "client", "chiaro"],
        },
        "sentence_templates": [
            "Devo {word} questo {word2}.",
            "Lascia che {word} il {word2}.",
            "Il {word} non è {word2}.",
            "Io {word} questo {word2}.",
        ],
    },
    "writer": {
        "name": "작가",
        "preferred_words": {
            "mo": ["mondo", "molto", "modo"],
            "st": ["storia", "stesso", "stato"],
            "be": ["bello", "bene", "bella"],
            "ch": ["casa", "chiamare", "chiamata"],
        },
        "sentence_templates": [
            "Il {word} era {word2}.",
            "In questo {word}, noi {word2}.",
            "La {word} del {word2}.",
        ],
    },
    "business": {
        "name": "비즈니스맨",
        "preferred_words": {
            "la": ["lavoro", "lavorare", "lavorato"],
            "ri": ["riunione", "riunire", "risultato"],
            "pr": ["progetto", "presentare", "prezzo"],
            "cl": ["cliente", "chiudere", "chiaro"],
            "co": ["compagnia", "completare", "contatto"],
        },
        "sentence_templates": [
            "Dobbiamo {word} su questo {word2}.",
            "Il {word} è importante per {word2}.",
            "Questo {word} aiuterà {word2}.",
        ],
    },
    "student": {
        "name": "학생",
        "preferred_words": {
            "st": ["studiare", "studente", "studio"],
            "im": ["imparare", "importante", "immagine"],
            "le": ["lezione", "legge", "leggere"],
            "es": ["esame", "esempio", "esercizio"],
        },
        "sentence_templates": [
            "Devo {word} per il {word2}.",
            "La {word} è su {word2}.",
            "Questo {word} mi aiuta {word2}.",
        ],
    },
    "general": {
        "name": "일반 사용자",
        "preferred_words": {},
        "sentence_templates": [],
    },
}

# 일본어 사용자별 선호 단어 및 문장 패턴 정의
USER_PROFILES_JA = {
    "developer": {
        "name": "개발자",
        "preferred_words": {
            "コ": ["コード", "コンピューター", "コンパイル"],
            "プ": ["プログラム", "プロジェクト", "プロセス"],
            "フ": ["関数", "機能", "ファイル"],
            "ク": ["クラス", "クライアント", "クリア"],
        },
        "sentence_templates": [
            "この{word}を{word2}する必要があります。",
            "{word}を{word2}します。",
            "この{word}は{word2}ではありません。",
        ],
    },
    "writer": {
        "name": "작가",
        "preferred_words": {
            "世": ["世界", "世代"],
            "物": ["物語", "物"],
            "美": ["美しい", "美"],
            "変": ["変化", "変える"],
        },
        "sentence_templates": [
            "{word}は{word2}でした。",
            "この{word}で、私たちは{word2}します。",
            "{word}の{word2}。",
        ],
    },
    "business": {
        "name": "비즈니스맨",
        "preferred_words": {
            "仕": ["仕事", "仕様"],
            "会": ["会議", "会社", "会う"],
            "プ": ["プロジェクト", "プレゼント", "価格"],
            "客": ["客", "客先"],
        },
        "sentence_templates": [
            "この{word}について{word2}する必要があります。",
            "{word}は{word2}にとって重要です。",
            "この{word}は{word2}を助けます。",
        ],
    },
    "student": {
        "name": "학생",
        "preferred_words": {
            "勉": ["勉強", "勉強する"],
            "学": ["学ぶ", "学生", "学校"],
            "授": ["授業", "授ける"],
            "試": ["試験", "試す"],
        },
        "sentence_templates": [
            "{word}のために{word2}する必要があります。",
            "{word}は{word2}についてです。",
            "この{word}は{word2}を助けます。",
        ],
    },
    "general": {
        "name": "일반 사용자",
        "preferred_words": {},
        "sentence_templates": [],
    },
}

# 언어별 프로필 매핑
USER_PROFILES = {
    "en": USER_PROFILES_EN,
    "it": USER_PROFILES_IT,
    "ja": USER_PROFILES_JA,
}


def generate_sentences_for_user(
    user_id: str, lang: str = "en", num_sentences: int = 1000
) -> list[str]:
    """사용자별 문장을 생성합니다.
    
    Args:
        user_id: 사용자 ID
        lang: 언어 코드 ('en', 'it', 'ja')
        num_sentences: 생성할 문장 수
    
    Returns:
        생성된 문장 리스트
    """
    if lang not in USER_PROFILES:
        return []
    
    lang_profiles = USER_PROFILES[lang]
    
    if user_id not in lang_profiles:
        return []
    
    profile = lang_profiles[user_id]
    sentences = []
    
    # 언어별 기본 문장들
    common_sentences = {
        "en": [
            "The quick brown fox jumps over the lazy dog.",
            "I have a dream that one day this nation will rise up.",
            "To be or not to be, that is the question.",
            "All that glitters is not gold.",
            "Time flies like an arrow.",
            "The early bird catches the worm.",
            "A picture is worth a thousand words.",
            "Actions speak louder than words.",
            "Knowledge is power.",
            "Practice makes perfect.",
        ],
        "it": [
            "La vita è bella quando si vive con passione.",
            "Vorrei andare in vacanza al mare quest'estate.",
            "Il gatto dorme sul divano mentre il cane gioca in giardino.",
            "Mangiare la pizza italiana è sempre una buona idea.",
            "L'arte della cucina italiana è conosciuta in tutto il mondo.",
            "Sto studiando l'italiano perché mi piace la cultura italiana.",
            "Il sole splende nel cielo azzurro di una giornata estiva.",
            "La musica classica italiana è molto apprezzata.",
            "Buongiorno, come stai oggi?",
            "Roma è una città bellissima con tanta storia.",
        ],
        "ja": [
            "今日は良い天気ですね。",
            "私は日本語を勉強しています。",
            "おはようございます、元気ですか？",
            "桜の花がとても美しいです。",
            "日本の文化は興味深いです。",
            "寿司を食べるのが好きです。",
            "東京はとても大きな都市です。",
            "本を読むことは知識を増やす良い方法です。",
            "友達と一緒に映画を見に行きました。",
            "毎日運動することは健康に良いです。",
        ],
    }
    
    # 사용자별 선호 단어가 있으면 문장 생성
    if profile["preferred_words"]:
        templates = profile["sentence_templates"]
        preferred_words = profile["preferred_words"]
        
        for _ in range(num_sentences):
            # 템플릿 사용 (50%)
            if templates and random.random() < 0.5:
                template = random.choice(templates)
                # 접두사 선택
                prefix = random.choice(list(preferred_words.keys()))
                word = random.choice(preferred_words[prefix])
                
                # 두 번째 단어 선택
                if len(preferred_words) > 1:
                    prefix2 = random.choice(list(preferred_words.keys()))
                    word2 = random.choice(preferred_words[prefix2])
                else:
                    word2 = word
                
                try:
                    sentence = template.format(word=word, word2=word2)
                    sentences.append(sentence)
                except:
                    # 포맷 오류 시 단순 문장 생성
                    if lang == "en":
                        sentences.append(f"The {word} is important.")
                    elif lang == "it":
                        sentences.append(f"Il {word} è importante.")
                    else:  # ja
                        sentences.append(f"{word}は重要です。")
            else:
                # 선호 단어를 포함한 간단한 문장 생성
                prefix = random.choice(list(preferred_words.keys()))
                word = random.choice(preferred_words[prefix])
                
                # 언어별 간단한 문장 패턴
                if lang == "en":
                    patterns = [
                        f"I {word} every day.",
                        f"The {word} is important.",
                        f"We need to {word}.",
                        f"This {word} helps.",
                        f"The {word} of the day.",
                    ]
                elif lang == "it":
                    patterns = [
                        f"Il {word} è importante.",
                        f"Dobbiamo {word}.",
                        f"Questo {word} aiuta.",
                        f"La {word} del giorno.",
                    ]
                else:  # ja
                    patterns = [
                        f"{word}は重要です。",
                        f"{word}する必要があります。",
                        f"この{word}は役立ちます。",
                    ]
                
                sentence = random.choice(patterns)
                sentences.append(sentence)
    else:
        # 일반 사용자는 기본 문장들 반복
        common = common_sentences.get(lang, [])
        if common:
            for _ in range(num_sentences):
                sentences.append(random.choice(common))
    
    return sentences


def save_user_sentences(user_id: str, lang: str, sentences: list[str]) -> None:
    """사용자 문장을 파일로 저장합니다.
    
    Args:
        user_id: 사용자 ID
        lang: 언어 코드
        sentences: 저장할 문장 리스트
    """
    output_dir = Path(__file__).parent / "sentences"
    output_dir.mkdir(parents=True, exist_ok=True)  # 폴더가 없으면 생성
    output_file = output_dir / f"{user_id}_{lang}_sentences.txt"
    
    with open(output_file, "w", encoding="utf-8") as f:
        for sentence in sentences:
            f.write(sentence + "\n")
    
    print(f"[{user_id}][{lang}] {len(sentences)}개 문장 저장: {output_file}")


def main():
    """메인 함수 - 모든 사용자별 문장 생성 (모든 언어)"""
    print("=" * 60)
    print("사용자별 문장 데이터 생성 (다국어)")
    print("=" * 60)
    
    num_sentences = 2000  # 각 사용자당 생성할 문장 수
    languages = ["en", "it", "ja"]
    
    for lang in languages:
        print(f"\n{'=' * 60}")
        print(f"[{lang.upper()}] 언어 문장 생성")
        print("=" * 60)
        
        lang_profiles = USER_PROFILES[lang]
        
        for user_id in lang_profiles.keys():
            print(f"\n[{lang_profiles[user_id]['name']}] 문장 생성 중...")
            sentences = generate_sentences_for_user(user_id, lang, num_sentences)
            save_user_sentences(user_id, lang, sentences)
    
    print("\n" + "=" * 60)
    print("문장 생성 완료!")
    print("=" * 60)


if __name__ == "__main__":
    main()

