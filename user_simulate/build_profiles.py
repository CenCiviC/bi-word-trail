"""사용자 문장 파일을 읽어서 프로필을 구축하는 스크립트"""

import re
from pathlib import Path

import sys
from pathlib import Path

# 상위 디렉토리를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.recommender import MultiLanguageRecommender
from src.user_profile import UserProfile, UserProfileManager


def extract_words_from_sentence(sentence: str, lang: str) -> list[str]:
    """문장에서 단어들을 추출합니다.
    
    Args:
        sentence: 입력 문장
        lang: 언어 코드
    
    Returns:
        단어 리스트
    """
    if lang == "ja":
        # 일본어: 조사와 구두점으로 분리
        import unicodedata
        
        particles = ["は", "を", "に", "で", "が", "と", "の", "も", "から", "まで", "へ", "や", "か", "ね", "よ", "です", "ます", "だ"]
        words = []
        current_word = ""
        
        i = 0
        while i < len(sentence):
            char = sentence[i]
            char_name = unicodedata.name(char, "")
            is_japanese = (
                "HIRAGANA" in char_name or
                "KATAKANA" in char_name or
                "CJK UNIFIED IDEOGRAPH" in char_name
            )
            
            if char in "。、！？":
                if current_word:
                    words.append(current_word)
                    current_word = ""
                i += 1
            elif is_japanese:
                found_particle = False
                for particle in sorted(particles, key=len, reverse=True):
                    if sentence[i:].startswith(particle):
                        if current_word:
                            words.append(current_word)
                            current_word = ""
                        words.append(particle)
                        i += len(particle)
                        found_particle = True
                        break
                
                if not found_particle:
                    current_word += char
                    i += 1
            else:
                if current_word:
                    words.append(current_word)
                    current_word = ""
                i += 1
        
        if current_word:
            words.append(current_word)
        
        return [w for w in words if w]
    else:
        # 영어, 이탈리아어: 공백과 구두점으로 단어 분리
        words = re.findall(r"\b\w+\b", sentence.lower())
        return words


def build_user_profile_from_sentences(
    user_id: str, sentences: list[str], lang: str, recommender: MultiLanguageRecommender
) -> UserProfile:
    """문장 리스트로부터 사용자 프로필을 구축합니다.
    
    Args:
        user_id: 사용자 ID
        sentences: 사용자가 작성한 문장 리스트
        lang: 언어 코드
        recommender: 추천 시스템 (접두사 추출용)
    
    Returns:
        구축된 UserProfile
    """
    profile = UserProfile(user_id)
    
    for sentence in sentences:
        words = extract_words_from_sentence(sentence, lang)
        
        for word in words:
            # 각 단어의 접두사를 생성하여 기록
            max_prefix_len = min(len(word) + 1, 4)  # 최대 3글자 접두사
            for prefix_len in range(1, max_prefix_len):
                prefix = word[:prefix_len]
                profile.record_word_selection(word, prefix)
    
    return profile


def load_user_sentences(user_id: str, lang: str) -> list[str]:
    """사용자 문장 파일을 읽어옵니다.
    
    Args:
        user_id: 사용자 ID
        lang: 언어 코드
    
    Returns:
        문장 리스트
    """
    data_dir = Path(__file__).parent / "sentences"
    sentence_file = data_dir / f"{user_id}_{lang}_sentences.txt"
    
    if not sentence_file.exists():
        # 하위 호환성: 기존 파일명도 확인
        old_file = data_dir / f"{user_id}_sentences.txt"
        if old_file.exists():
            sentence_file = old_file
        else:
            print(f"경고: 파일을 찾을 수 없습니다: {sentence_file}")
            return []
    
    sentences = []
    with open(sentence_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                sentences.append(line)
    
    return sentences


def main():
    """메인 함수 - 모든 사용자 프로필 구축 (모든 언어)"""
    print("=" * 60)
    print("사용자 프로필 구축 (다국어)")
    print("=" * 60)
    
    languages = ["en", "it", "ja"]
    user_ids = ["developer", "writer", "business", "student", "general"]
    
    # 추천 시스템 초기화 (모든 언어)
    print("\n추천 시스템 초기화 중...")
    recommender = MultiLanguageRecommender(languages=languages)
    
    # 언어별 프로필 매니저
    profile_managers: dict[str, UserProfileManager] = {}
    
    for lang in languages:
        print(f"\n{'=' * 60}")
        print(f"[{lang.upper()}] 언어 프로필 구축")
        print("=" * 60)
        
        profile_manager = UserProfileManager()
        
        for user_id in user_ids:
            print(f"\n[{user_id}] 프로필 구축 중...")
            
            # 문장 로드
            sentences = load_user_sentences(user_id, lang)
            
            if not sentences:
                print(f"  경고: {user_id}의 {lang} 문장 데이터가 없습니다.")
                continue
            
            print(f"  문장 수: {len(sentences)}")
            
            # 프로필 구축
            profile = build_user_profile_from_sentences(user_id, sentences, lang, recommender)
            profile_manager.profiles[user_id] = profile
            
            # 통계 출력
            total_words = sum(profile.word_counts.values())
            unique_words = len(profile.word_counts)
            
            print(f"  총 단어 사용 횟수: {total_words}")
            print(f"  고유 단어 수: {unique_words}")
            
            # 가장 많이 사용한 단어 Top 5
            top_words = sorted(
                profile.word_counts.items(), key=lambda x: x[1], reverse=True
            )[:5]
            print(f"  가장 많이 사용한 단어:")
            for word, count in top_words:
                print(f"    - {word}: {count}회")
        
        profile_managers[lang] = profile_manager
    
    print("\n" + "=" * 60)
    print("프로필 구축 완료!")
    print("=" * 60)
    
    return profile_managers, recommender


if __name__ == "__main__":
    profile_managers, recommender = main()
    # 프로필 매니저와 추천 시스템을 전역 변수로 저장 (test_personalization.py에서 사용)
    import user_simulate.build_profiles as build_profiles_module
    build_profiles_module.profile_managers = profile_managers
    build_profiles_module.recommender = recommender

