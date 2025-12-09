"""단어 자동완성 추천 시스템 메인 모듈"""

from src.recommender import MultiLanguageRecommender


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


if __name__ == "__main__":
    main()
