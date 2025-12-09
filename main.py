"""단어 자동완성 추천 시스템 메인 모듈"""

import re
from pathlib import Path
from typing import Any

from src.recommender import MultiLanguageRecommender
from src.user_profile import UserProfile


def find_min_prefix_for_word(
    recommender: MultiLanguageRecommender,
    word: str,
    lang: str,
    top_n: int = 10,
    user_profile: UserProfile | None = None,
    return_details: bool = False,
) -> int | tuple[int, str, list[tuple[str, float]]]:
    """단어를 추천 목록의 첫 번째에 나타나게 하는 최소 접두사 길이를 찾습니다.
    
    Args:
        recommender: 추천 시스템 인스턴스
        word: 찾을 단어
        lang: 언어 코드
        top_n: 추천 목록 크기
        user_profile: 사용자 프로필
        return_details: True면 상세 정보도 반환
    
    Returns:
        최소 접두사 길이 또는 (접두사 길이, 접두사, 추천 목록) 튜플
    """
    word_lower = word.lower()
    
    # 접두사를 하나씩 늘려가며 테스트
    for prefix_len in range(1, len(word_lower) + 1):
        prefix = word_lower[:prefix_len]
        recommendations = recommender.recommend(
            prefix, lang=lang, top_n=top_n, user_profile=user_profile
        )
        
        # 추천 목록에서 해당 단어 찾기 (대소문자 무시)
        for rec_word, _ in recommendations:
            if rec_word.lower() == word_lower:
                if return_details:
                    return (prefix_len, prefix, recommendations[:5])  # 상위 5개만
                return prefix_len
    
    # 추천 목록에 없으면 전체 길이 반환
    if return_details:
        return (len(word_lower), word_lower, [])
    return len(word_lower)


def split_sentence_to_words(sentence: str, lang: str) -> list[str]:
    """문장을 언어에 맞게 단어로 분리합니다.
    
    Args:
        sentence: 입력 문장
        lang: 언어 코드
    
    Returns:
        단어 리스트
    """
    if lang == 'ja':
        # 일본어: 구두점(。、！？)과 조사(は、を、に、で 등)를 기준으로 분리
        # 간단한 방법: 조사와 구두점 앞에서 분리
        import unicodedata
        
        # 조사 목록
        particles = ['は', 'を', 'に', 'で', 'が', 'と', 'の', 'も', 'から', 'まで', 'へ', 'や', 'か', 'ね', 'よ', 'です', 'ます', 'だ', 'である']
        
        words = []
        current_word = ''
        
        i = 0
        while i < len(sentence):
            char = sentence[i]
            char_name = unicodedata.name(char, '')
            is_japanese = (
                'HIRAGANA' in char_name or
                'KATAKANA' in char_name or
                'CJK UNIFIED IDEOGRAPH' in char_name
            )
            
            if char in '。、！？':
                if current_word:
                    words.append(current_word)
                    current_word = ''
                i += 1
            elif is_japanese:
                # 조사 확인 (다음 1-2글자까지 확인)
                found_particle = False
                for particle in sorted(particles, key=len, reverse=True):
                    if sentence[i:].startswith(particle):
                        if current_word:
                            words.append(current_word)
                            current_word = ''
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
                    current_word = ''
                i += 1
        
        if current_word:
            words.append(current_word)
        
        return [w for w in words if w]  # 빈 문자열 제거
    else:
        # 영어, 이탈리아어 등: 공백과 구두점으로 분리
        words: list[str] = re.findall(r'\b\w+\b', sentence)
        return words


def test_sentence_autocomplete(
    recommender: MultiLanguageRecommender,
    sentence: str,
    lang: str,
    user_profile: UserProfile | None = None,
    return_word_details: bool = False,
) -> dict[str, Any] | None:
    """문장에 대해 자동완성 효율을 테스트합니다.
    
    Args:
        recommender: 추천 시스템 인스턴스
        sentence: 테스트할 문장
        lang: 언어 코드
        user_profile: 사용자 프로필
        return_word_details: True면 각 단어별 상세 정보 반환
    
    Returns:
        테스트 결과 딕셔너리
    """
    # 문장을 언어에 맞게 단어로 분리
    words: list[str] = split_sentence_to_words(sentence, lang)
    
    if not words:
        return None
    
    total_chars_without_autocomplete = 0
    total_chars_with_autocomplete = 0
    word_details: list[dict[str, Any]] = []
    
    for word in words:
        word_lower: str = word.lower()
        
        if return_word_details:
            result = find_min_prefix_for_word(
                recommender, word_lower, lang, user_profile=user_profile, return_details=True
            )
            if isinstance(result, tuple):
                prefix_len, prefix, recommendations = result
            else:
                prefix_len = result
                prefix = word_lower[:prefix_len]
                recommendations = []
            
            word_details.append({
                'word': word,
                'word_lower': word_lower,
                'full_length': len(word_lower),
                'prefix': prefix,
                'prefix_length': prefix_len,
                'chars_saved': len(word_lower) - prefix_len,
                'recommendations': [
                    {'word': rec_word, 'score': float(score)}
                    for rec_word, score in recommendations
                ]
            })
        else:
            prefix_len = find_min_prefix_for_word(
                recommender, word_lower, lang, user_profile=user_profile
            )
            if isinstance(prefix_len, tuple):
                prefix_len = prefix_len[0]
        
        total_chars_without_autocomplete += len(word_lower)
        total_chars_with_autocomplete += prefix_len
    
    result: dict[str, Any] = {
        'sentence': sentence,
        'lang': lang,
        'word_count': len(words),
        'total_chars_without': total_chars_without_autocomplete,
        'total_chars_with': total_chars_with_autocomplete,
        'chars_saved': total_chars_without_autocomplete - total_chars_with_autocomplete,
        'savings_rate': (1 - total_chars_with_autocomplete / total_chars_without_autocomplete) * 100 if total_chars_without_autocomplete > 0 else 0
    }
    
    if return_word_details:
        result['word_details'] = word_details
    
    return result


def main():
    """메인 함수 - 다국어 단어 추천 시스템 예제"""
    print("=" * 60)
    print("단어 자동완성 추천 시스템")
    print("=" * 60)
    
    # 다국어 추천 시스템 초기화 (영어, 이탈리아어, 일본어)
    print("\n시스템 초기화 중...")
    recommender = MultiLanguageRecommender(languages=["en", "it", "ja"])
    
    print("\n" + "=" * 60)
    print("추천 예제")
    print("=" * 60)
    
    # 영어 예제
    print("\n[영어] 'wo'로 시작하는 단어 추천:")
    en_recommendations = recommender.recommend("wo", lang="en", top_n=10)
    for i, (word, freq) in enumerate(en_recommendations, 1):
        print(f"  {i}. {word:15s} (빈도: {freq:.2e})")
    
    # 이탈리아어 예제
    print("\n[이탈리아어] 'ca'로 시작하는 단어 추천:")
    it_recommendations = recommender.recommend("ca", lang="it", top_n=10)
    for i, (word, freq) in enumerate(it_recommendations, 1):
        print(f"  {i}. {word:15s} (빈도: {freq:.2e})")
    
    # 일본어 예제 - 히라가나 입력
    print("\n[일본어] 'あ'로 시작하는 단어 추천:")
    ja_recommendations = recommender.recommend("あ", lang="ja", top_n=10)
    for i, (word, freq) in enumerate(ja_recommendations, 1):
        print(f"  {i}. {word:15s} (빈도: {freq:.2e})")
    
    # 일본어 예제 - 로마자 입력 (자동 변환)
    print("\n[일본어] 'a' (로마자)로 시작하는 단어 추천:")
    ja_recommendations_romaji = recommender.recommend("a", lang="ja", top_n=10)
    for i, (word, freq) in enumerate(ja_recommendations_romaji, 1):
        print(f"  {i}. {word:15s} (빈도: {freq:.2e})")
    
    print("\n" + "=" * 60)
    print("개별 단어 빈도 조회 예제")
    print("=" * 60)
    
    # 개별 단어 빈도 조회
    test_words = [
        ("en", "word"),
        ("en", "world"),
        ("it", "casa"),
        ("it", "cane"),
        ("ja", "あい"),
        ("ja", "あか"),
    ]
    
    for lang, word in test_words:
        freq = recommender.get_word_frequency(word, lang)
        print(f"  [{lang}] '{word}': {freq:.2e}")
    
    print("\n" + "=" * 60)
    print("문장 자동완성 효율 테스트")
    print("=" * 60)
    
    # 파일에서 테스트 문장 읽기
    test_sentences_from_files(recommender)
    


def load_test_sentences(lang: str) -> list[str]:
    """테스트 문장 파일에서 문장들을 읽어옵니다.
    
    Args:
        lang: 언어 코드 ('en', 'it', 'ja')
    
    Returns:
        문장 리스트
    """
    test_file = Path(__file__).parent / "tests" / f"test_sentences_{lang}.txt"
    
    if not test_file.exists():
        print(f"경고: 테스트 파일을 찾을 수 없습니다: {test_file}")
        return []
    
    sentences = []
    with open(test_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:  # 빈 줄 제외
                sentences.append(line)
    
    return sentences


def test_sentences_from_files(recommender: MultiLanguageRecommender) -> None:
    """각 언어별 테스트 문장 파일을 읽어서 테스트합니다.
    
    Args:
        recommender: 추천 시스템 인스턴스
    """
    languages: dict[str, str] = {
        'en': '영어',
        'it': '이탈리아어',
        'ja': '일본어'
    }
    
    all_results: dict[str, list[dict[str, Any]]] = {}
    
    for lang_code, lang_name in languages.items():
        sentences = load_test_sentences(lang_code)
        
        if not sentences:
            continue
        
        lang_results: list[dict[str, Any]] = []
        
        # 진행 상황 표시 (10개마다)
        for i, sentence in enumerate(sentences, 1):
            if i % 10 == 0 or i == len(sentences):
                print(f"[{lang_name}] 처리 중: {i}/{len(sentences)} 문장...", end='\r')
            
            result = test_sentence_autocomplete(recommender, sentence, lang=lang_code)
            if result:
                lang_results.append(result)
        
        print(f"[{lang_name}] 완료: {len(sentences)} 문장 처리됨")
        all_results[lang_code] = lang_results
    
    # 전체 통계
    if all_results:
        print(f"\n{'=' * 60}")
        print("전체 언어 통계")
        print('=' * 60)
        
        for lang_code, lang_name in languages.items():
            if lang_code in all_results and all_results[lang_code]:
                results = all_results[lang_code]
                total_chars_without = sum(r['total_chars_without'] for r in results)
                total_chars_with = sum(r['total_chars_with'] for r in results)
                total_chars_saved = sum(r['chars_saved'] for r in results)
                avg_savings_rate = sum(r['savings_rate'] for r in results) / len(results)
                
                print(f"\n[{lang_name}]:")
                print(f"  문장 수: {len(results)}")
                print(f"  평균 절약률: {avg_savings_rate:.1f}%")
                print(f"  총 절약 글자: {total_chars_saved}")
        
        # 전체 합계
        all_total_without = sum(
            sum(r['total_chars_without'] for r in results)
            for results in all_results.values()
        )
        all_total_with = sum(
            sum(r['total_chars_with'] for r in results)
            for results in all_results.values()
        )
        all_total_saved = all_total_without - all_total_with
        all_avg_rate = (1 - all_total_with / all_total_without) * 100 if all_total_without > 0 else 0
        
        print(f"\n전체 합계:")
        print(f"  총 절약 글자 수: {all_total_saved}")
        print(f"  전체 평균 절약률: {all_avg_rate:.1f}%")




if __name__ == "__main__":
    main()
