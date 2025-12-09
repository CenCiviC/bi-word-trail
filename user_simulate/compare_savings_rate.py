"""개인화 추천과 기본 추천의 절약율 비교 스크립트"""

import sys
from pathlib import Path
from typing import Any

# 상위 디렉토리를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import find_min_prefix_for_word, split_sentence_to_words
from src.recommender import MultiLanguageRecommender
from user_simulate.build_profiles import load_user_sentences, main as build_profiles_main


def calculate_savings_rate(
    recommender: MultiLanguageRecommender,
    sentences: list[str],
    lang: str,
    user_profile: Any | None = None,
) -> dict[str, float]:
    """문장 리스트에 대해 절약율을 계산합니다.
    
    Args:
        recommender: 추천 시스템 인스턴스
        sentences: 테스트할 문장 리스트
        lang: 언어 코드
        user_profile: 사용자 프로필 (None이면 기본 추천)
    
    Returns:
        절약율 통계 딕셔너리
    """
    total_chars_without = 0
    total_chars_with = 0
    
    for sentence in sentences:
        words = split_sentence_to_words(sentence, lang)
        
        for word in words:
            word_lower = word.lower()
            min_prefix_len = find_min_prefix_for_word(
                recommender, word_lower, lang, user_profile=user_profile
            )
            
            total_chars_without += len(word_lower)
            total_chars_with += min_prefix_len
    
    if total_chars_without == 0:
        return {
            "total_chars_without": 0,
            "total_chars_with": 0,
            "chars_saved": 0,
            "savings_rate": 0.0,
        }
    
    chars_saved = total_chars_without - total_chars_with
    savings_rate = (1 - total_chars_with / total_chars_without) * 100
    
    return {
        "total_chars_without": total_chars_without,
        "total_chars_with": total_chars_with,
        "chars_saved": chars_saved,
        "savings_rate": savings_rate,
    }


def compare_savings_rates(
    profile_managers: dict[str, Any],
    recommender: MultiLanguageRecommender,
    num_sentences: int = 100,
) -> None:
    """개인화 추천과 기본 추천의 절약율을 비교합니다.
    
    Args:
        profile_managers: 언어별 프로필 매니저 딕셔너리
        recommender: 다국어 추천 시스템
        num_sentences: 각 사용자당 테스트할 문장 수
    """
    print("\n" + "=" * 60)
    print("개인화 추천 vs 기본 추천 절약율 비교")
    print("=" * 60)
    
    languages = ["en", "it", "ja"]
    user_ids = ["developer", "writer", "business", "student", "general"]
    
    all_results = []
    
    for lang in languages:
        print(f"\n{'=' * 60}")
        print(f"[{lang.upper()}] 언어 절약율 비교")
        print("=" * 60)
        
        if lang not in profile_managers:
            print(f"  경고: {lang} 언어 프로필이 없습니다.")
            continue
        
        profile_manager = profile_managers[lang]
        
        for user_id in user_ids:
            if user_id not in profile_manager.profiles:
                continue
            
            # 사용자 문장 로드
            sentences = load_user_sentences(user_id, lang)
            if not sentences:
                continue
            
            # 테스트할 문장 수 제한
            test_sentences = sentences[:num_sentences]
            
            profile = profile_manager.profiles[user_id]
            
            # 개인화 추천 절약율 계산
            personalized_stats = calculate_savings_rate(
                recommender, test_sentences, lang, user_profile=profile
            )
            
            # 기본 추천 절약율 계산
            general_stats = calculate_savings_rate(
                recommender, test_sentences, lang, user_profile=None
            )
            
            # 비교 결과
            improvement = (
                personalized_stats["savings_rate"] - general_stats["savings_rate"]
            )
            improvement_percent = (
                improvement / general_stats["savings_rate"] * 100
                if general_stats["savings_rate"] > 0
                else 0
            )
            
            print(f"\n  [{user_id}]")
            print(f"    테스트 문장 수: {len(test_sentences)}")
            print(f"    기본 추천 절약율: {general_stats['savings_rate']:.2f}%")
            print(f"    개인화 추천 절약율: {personalized_stats['savings_rate']:.2f}%")
            print(f"    절약율 개선: {improvement:+.2f}%p")
            print(f"    개선률: {improvement_percent:+.2f}%")
            print(
                f"    절약 글자 수 차이: {personalized_stats['chars_saved'] - general_stats['chars_saved']:+d}자"
            )
            
            all_results.append(
                {
                    "lang": lang,
                    "user_id": user_id,
                    "general_rate": general_stats["savings_rate"],
                    "personalized_rate": personalized_stats["savings_rate"],
                    "improvement": improvement,
                    "improvement_percent": improvement_percent,
                }
            )
    
    # 전체 통계
    if all_results:
        print("\n" + "=" * 60)
        print("전체 통계 요약")
        print("=" * 60)
        
        avg_general = sum(r["general_rate"] for r in all_results) / len(all_results)
        avg_personalized = sum(r["personalized_rate"] for r in all_results) / len(
            all_results
        )
        avg_improvement = sum(r["improvement"] for r in all_results) / len(all_results)
        avg_improvement_percent = sum(r["improvement_percent"] for r in all_results) / len(
            all_results
        )
        
        print(f"\n평균 기본 추천 절약율: {avg_general:.2f}%")
        print(f"평균 개인화 추천 절약율: {avg_personalized:.2f}%")
        print(f"평균 절약율 개선: {avg_improvement:+.2f}%p")
        print(f"평균 개선률: {avg_improvement_percent:+.2f}%")
        
        # 언어별 통계
        print("\n언어별 평균 절약율 개선:")
        for lang in languages:
            lang_results = [r for r in all_results if r["lang"] == lang]
            if lang_results:
                lang_avg_improvement = sum(r["improvement"] for r in lang_results) / len(
                    lang_results
                )
                print(f"  [{lang.upper()}]: {lang_avg_improvement:+.2f}%p")
        
        # 사용자별 통계
        print("\n사용자별 평균 절약율 개선:")
        for user_id in user_ids:
            user_results = [r for r in all_results if r["user_id"] == user_id]
            if user_results:
                user_avg_improvement = sum(r["improvement"] for r in user_results) / len(
                    user_results
                )
                print(f"  [{user_id}]: {user_avg_improvement:+.2f}%p")


def main():
    """메인 함수 - 프로필 구축 후 절약율 비교"""
    print("=" * 60)
    print("개인화 추천 절약율 비교 시작")
    print("=" * 60)
    
    # 프로필 구축
    print("\n프로필 구축 중...")
    profile_managers, recommender = build_profiles_main()
    
    # 절약율 비교
    compare_savings_rates(profile_managers, recommender, num_sentences=100)
    
    print("\n" + "=" * 60)
    print("절약율 비교 완료!")
    print("=" * 60)


if __name__ == "__main__":
    main()

