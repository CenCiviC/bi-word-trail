"""개인화 추천 시스템 테스트 스크립트"""

import sys
from pathlib import Path

# 상위 디렉토리를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from user_simulate.build_profiles import main as build_profiles_main


def test_personalization(
    profile_managers: dict[str, object], recommender: object, test_prefixes: dict[str, list[str]]
) -> None:
    """개인화 추천을 테스트합니다.
    
    Args:
        profile_managers: 언어별 프로필 매니저 딕셔너리
        recommender: 다국어 추천 시스템
        test_prefixes: 언어별 테스트 접두사 리스트
    """
    print("\n" + "=" * 60)
    print("개인화 추천 테스트")
    print("=" * 60)
    
    languages = ["en", "it", "ja"]
    user_ids = ["developer", "writer", "business", "student", "general"]
    
    for lang in languages:
        print(f"\n{'=' * 60}")
        print(f"[{lang.upper()}] 언어 개인화 추천 테스트")
        print("=" * 60)
        
        if lang not in profile_managers:
            print(f"  경고: {lang} 언어 프로필이 없습니다.")
            continue
        
        profile_manager = profile_managers[lang]
        prefixes = test_prefixes.get(lang, [])
        
        if not prefixes:
            print(f"  경고: {lang} 언어 테스트 접두사가 없습니다.")
            continue
        
        for prefix in prefixes:
            print(f"\n  접두사: '{prefix}'")
            print("-" * 40)
            
            # 각 사용자별로 개인화 추천 테스트
            for user_id in user_ids:
                if user_id not in profile_manager.profiles:
                    continue
                
                profile = profile_manager.profiles[user_id]
                
                # 개인화된 추천
                personalized = recommender.recommend(
                    prefix=prefix,
                    lang=lang,
                    top_n=5,
                    user_profile=profile,
                )
                
                # 일반 추천 (프로필 없음)
                general = recommender.recommend(
                    prefix=prefix,
                    lang=lang,
                    top_n=5,
                    user_profile=None,
                )
                
                # 개인화된 추천과 일반 추천 비교
                personalized_words = [word for word, _ in personalized]
                general_words = [word for word, _ in general]
                
                # 차이점 확인
                differences = []
                for word, score in personalized:
                    if word not in general_words[:len(personalized_words)]:
                        differences.append((word, score))
                
                if differences:
                    print(f"  [{user_id}]")
                    print(f"    일반 추천: {', '.join(general_words[:5])}")
                    print(f"    개인화 추천: {', '.join(personalized_words[:5])}")
                    print("    차이점:")
                    for word, score in differences[:3]:
                        print(f"      - {word} (점수: {score:.6f})")
                else:
                    print(f"  [{user_id}] 일반 추천과 동일")


def main():
    """메인 함수 - 프로필 구축 후 개인화 추천 테스트"""
    print("=" * 60)
    print("개인화 추천 테스트 시작")
    print("=" * 60)
    
    # 프로필 구축
    print("\n프로필 구축 중...")
    profile_managers, recommender = build_profiles_main()
    
    # 언어별 테스트 접두사
    test_prefixes = {
        "en": ["wo", "co", "pr", "fu", "cl", "st", "be", "ch", "th", "me"],
        "it": ["co", "pr", "fu", "cl", "la", "ri", "st", "im", "le", "es"],
        "ja": ["コ", "プ", "フ", "ク", "仕", "会", "勉", "学", "授", "試"],
    }
    
    # 개인화 추천 테스트
    test_personalization(profile_managers, recommender, test_prefixes)
    
    print("\n" + "=" * 60)
    print("개인화 추천 테스트 완료!")
    print("=" * 60)


if __name__ == "__main__":
    main()

