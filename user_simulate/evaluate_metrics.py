"""추천 시스템 평가 지표 계산 스크립트

Precision@K, Recall@K, F1 Score, MAP 등을 계산합니다.
"""

import sys
from pathlib import Path
from typing import Any

# 상위 디렉토리를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import find_min_prefix_for_word, split_sentence_to_words
from src.recommender import MultiLanguageRecommender
from user_simulate.build_profiles import load_user_sentences, main as build_profiles_main

try:
    import pykakasi
    kakasi = pykakasi.kakasi()
    kakasi.setMode("H", "a")  # 히라가나를 로마자로
    kakasi.setMode("K", "a")  # 가타카나를 로마자로
    kakasi.setMode("J", "a")  # 한자를 로마자로
    converter = kakasi.getConverter()
except ImportError:
    converter = None


def calculate_precision_at_k(
    recommended_items: list[str], relevant_items: set[str], k: int
) -> float:
    """Precision@K 계산
    
    Args:
        recommended_items: 추천된 아이템 리스트 (정렬됨)
        relevant_items: 관련 있는 아이템 집합
        k: 상위 K개
    
    Returns:
        Precision@K 값 (0.0 ~ 1.0)
    """
    top_k = recommended_items[:k]
    if not top_k:
        return 0.0
    
    relevant_in_top_k = sum(1 for item in top_k if item in relevant_items)
    return relevant_in_top_k / len(top_k)


def calculate_recall_at_k(
    recommended_items: list[str], relevant_items: set[str], k: int
) -> float:
    """Recall@K 계산
    
    Args:
        recommended_items: 추천된 아이템 리스트 (정렬됨)
        relevant_items: 관련 있는 아이템 집합
        k: 상위 K개
    
    Returns:
        Recall@K 값 (0.0 ~ 1.0)
    """
    if not relevant_items:
        return 0.0
    
    top_k = recommended_items[:k]
    relevant_in_top_k = sum(1 for item in top_k if item in relevant_items)
    return relevant_in_top_k / len(relevant_items)


def calculate_f1_score(precision: float, recall: float) -> float:
    """F1 Score 계산
    
    Args:
        precision: Precision 값
        recall: Recall 값
    
    Returns:
        F1 Score 값 (0.0 ~ 1.0)
    """
    if precision + recall == 0:
        return 0.0
    return 2 * (precision * recall) / (precision + recall)


def calculate_average_precision(
    recommended_items: list[str], relevant_items: set[str]
) -> float:
    """Average Precision (AP) 계산
    
    Args:
        recommended_items: 추천된 아이템 리스트 (정렬됨)
        relevant_items: 관련 있는 아이템 집합
    
    Returns:
        Average Precision 값 (0.0 ~ 1.0)
    """
    if not relevant_items:
        return 0.0
    
    relevant_count = 0
    precision_sum = 0.0
    
    for i, item in enumerate(recommended_items, 1):
        if item in relevant_items:
            relevant_count += 1
            precision_at_i = relevant_count / i
            precision_sum += precision_at_i
    
    if relevant_count == 0:
        return 0.0
    
    return precision_sum / len(relevant_items)


def calculate_map(recommended_lists: list[list[str]], relevant_sets: list[set[str]]) -> float:
    """Mean Average Precision (MAP) 계산
    
    Args:
        recommended_lists: 각 쿼리별 추천 아이템 리스트들
        relevant_sets: 각 쿼리별 관련 아이템 집합들
    
    Returns:
        MAP 값 (0.0 ~ 1.0)
    """
    if not recommended_lists or not relevant_sets:
        return 0.0
    
    if len(recommended_lists) != len(relevant_sets):
        raise ValueError("추천 리스트와 관련 집합의 개수가 일치하지 않습니다.")
    
    aps = []
    for recommended, relevant in zip(recommended_lists, relevant_sets):
        ap = calculate_average_precision(recommended, relevant)
        aps.append(ap)
    
    return sum(aps) / len(aps) if aps else 0.0


def japanese_to_romaji(text: str) -> str:
    """일본어 텍스트를 로마자로 변환합니다.
    
    Args:
        text: 일본어 텍스트
    
    Returns:
        로마자로 변환된 텍스트
    """
    if converter is None:
        return text
    try:
        return converter.do(text)
    except Exception:
        return text


def evaluate_recommendations(
    recommender: MultiLanguageRecommender,
    test_sentences: list[str],
    lang: str,
    k_values: list[int] = [1, 3, 5, 10],
    user_profile: Any | None = None,
) -> dict[str, Any]:
    """추천 시스템 평가
    
    각 문장의 단어들을 ground truth로 사용하고,
    해당 단어의 접두사로 추천된 결과를 평가합니다.
    
    Args:
        recommender: 추천 시스템 인스턴스
        test_sentences: 테스트 문장 리스트
        lang: 언어 코드
        k_values: 평가할 K 값들
        user_profile: 사용자 프로필 (None이면 기본 추천)
    
    Returns:
        평가 결과 딕셔너리
    """
    all_precision_at_k: dict[int, list[float]] = {k: [] for k in k_values}
    all_recall_at_k: dict[int, list[float]] = {k: [] for k in k_values}
    all_f1_at_k: dict[int, list[float]] = {k: [] for k in k_values}
    all_aps: list[float] = []
    
    total_words = 0
    total_chars_without = 0
    total_chars_with = 0
    
    # 일본어인 경우 로마자 변환 정보 저장
    word_romaji_map: dict[str, str] = {}
    
    for sentence in test_sentences:
        words = split_sentence_to_words(sentence, lang)
        
        for word in words:
            word_lower = word.lower()
            total_words += 1
            
            # 일본어인 경우 로마자 변환 저장
            if lang == "ja" and converter:
                romaji = japanese_to_romaji(word)
                word_romaji_map[word_lower] = romaji
            
            # 해당 단어가 추천 목록에 나타나기 위한 최소 접두사 길이 찾기
            min_prefix_len_result = find_min_prefix_for_word(
                recommender, word_lower, lang, top_n=max(k_values), user_profile=user_profile, return_details=False
            )
            # return_details=False이므로 항상 int 반환
            min_prefix_len = min_prefix_len_result if isinstance(min_prefix_len_result, int) else len(word_lower)
            
            # 절약율 계산을 위한 글자 수 누적
            total_chars_without += len(word_lower)
            total_chars_with += min_prefix_len
            
            # 접두사로 추천 받기
            prefix = word_lower[:min_prefix_len]
            recommendations = recommender.recommend(
                prefix, lang=lang, top_n=max(k_values), user_profile=user_profile
            )
            recommended_words = [rec_word.lower() for rec_word, _ in recommendations]
            
            # Ground truth: 해당 단어가 관련 있는 아이템
            relevant_items = {word_lower}
            
            # 각 K 값에 대해 평가
            for k in k_values:
                precision = calculate_precision_at_k(recommended_words, relevant_items, k)
                recall = calculate_recall_at_k(recommended_words, relevant_items, k)
                f1 = calculate_f1_score(precision, recall)
                
                all_precision_at_k[k].append(precision)
                all_recall_at_k[k].append(recall)
                all_f1_at_k[k].append(f1)
            
            # Average Precision 계산
            ap = calculate_average_precision(recommended_words, relevant_items)
            all_aps.append(ap)
    
    savings_rate = (
        (1 - total_chars_with / total_chars_without) * 100
        if total_chars_without > 0
        else 0.0
    )
    
    # 평균 계산
    results: dict[str, Any] = {
        "total_words": total_words,
        "precision_at_k": {},
        "recall_at_k": {},
        "f1_at_k": {},
        "map": sum(all_aps) / len(all_aps) if all_aps else 0.0,
        "total_chars_without": total_chars_without,
        "total_chars_with": total_chars_with,
        "chars_saved": total_chars_without - total_chars_with,
        "savings_rate": savings_rate,
        "word_romaji_map": word_romaji_map if lang == "ja" else {},
    }
    
    for k in k_values:
        results["precision_at_k"][k] = (
            sum(all_precision_at_k[k]) / len(all_precision_at_k[k])
            if all_precision_at_k[k]
            else 0.0
        )
        results["recall_at_k"][k] = (
            sum(all_recall_at_k[k]) / len(all_recall_at_k[k])
            if all_recall_at_k[k]
            else 0.0
        )
        results["f1_at_k"][k] = (
            sum(all_f1_at_k[k]) / len(all_f1_at_k[k]) if all_f1_at_k[k] else 0.0
        )
    
    return results


def main():
    """메인 함수 - 모든 언어에 대해 평가 지표 계산"""
    print("=" * 60)
    print("추천 시스템 평가 지표 계산")
    print("=" * 60)
    
    # 프로필 구축
    print("\n추천 시스템 및 프로필 초기화 중...")
    profile_managers, recommender = build_profiles_main()
    
    languages = ["en", "it", "ja"]
    user_ids = ["developer", "writer", "business", "student", "general"]
    k_values = [1, 3, 5, 10]
    
    all_results: dict[str, dict[str, Any]] = {}
    
    for lang in languages:
        print(f"\n{'=' * 60}")
        print(f"[{lang.upper()}] 언어 평가")
        print("=" * 60)
        
        # 기본 추천 평가 (프로필 없음)
        print("\n기본 추천 평가 중...")
        test_sentences = []
        for user_id in user_ids:
            sentences = load_user_sentences(user_id, lang)
            test_sentences.extend(sentences[:50])  # 각 사용자당 50개 문장
        
        if not test_sentences:
            print(f"  경고: {lang} 언어 테스트 문장이 없습니다.")
            continue
        
        general_results = evaluate_recommendations(
            recommender, test_sentences, lang, k_values=k_values, user_profile=None
        )
        
        all_results[f"{lang}_general"] = general_results
        
        print(f"  평가 단어 수: {general_results['total_words']}")
        print(f"  MAP: {general_results['map']:.4f}")
        print(f"  절약율: {general_results['savings_rate']:.2f}%")
        
        # 일본어인 경우 로마자 변환 샘플 출력
        if lang == "ja" and general_results.get("word_romaji_map"):
            print("\n  [로마자 변환 샘플]")
            romaji_map = general_results["word_romaji_map"]
            sample_words = list(romaji_map.items())[:10]  # 처음 10개만 표시
            for word, romaji in sample_words:
                print(f"    {word} -> {romaji}")
        
        for k in k_values:
            print(
                f"  Precision@{k}: {general_results['precision_at_k'][k]:.4f}, "
                f"Recall@{k}: {general_results['recall_at_k'][k]:.4f}, "
                f"F1@{k}: {general_results['f1_at_k'][k]:.4f}"
            )
        
        # 개인화 추천 평가 (각 사용자별)
        if lang in profile_managers:
            profile_manager = profile_managers[lang]
            
            for user_id in user_ids:
                if user_id not in profile_manager.profiles:
                    continue
                
                print(f"\n[{user_id}] 개인화 추천 평가 중...")
                user_sentences = load_user_sentences(user_id, lang)
                if not user_sentences:
                    continue
                
                user_profile = profile_manager.profiles[user_id]
                personalized_results = evaluate_recommendations(
                    recommender,
                    user_sentences[:100],  # 100개 문장
                    lang,
                    k_values=k_values,
                    user_profile=user_profile,
                )
                
                all_results[f"{lang}_{user_id}"] = personalized_results
                
                print(f"  평가 단어 수: {personalized_results['total_words']}")
                print(f"  MAP: {personalized_results['map']:.4f}")
                print(f"  절약율: {personalized_results['savings_rate']:.2f}%")
                
                # 일본어인 경우 로마자 변환 샘플 출력
                if lang == "ja" and personalized_results.get("word_romaji_map"):
                    print("\n  [로마자 변환 샘플]")
                    romaji_map = personalized_results["word_romaji_map"]
                    sample_words = list(romaji_map.items())[:10]  # 처음 10개만 표시
                    for word, romaji in sample_words:
                        print(f"    {word} -> {romaji}")
                
                for k in k_values:
                    print(
                        f"  Precision@{k}: {personalized_results['precision_at_k'][k]:.4f}, "
                        f"Recall@{k}: {personalized_results['recall_at_k'][k]:.4f}, "
                        f"F1@{k}: {personalized_results['f1_at_k'][k]:.4f}"
                    )
    
    # 전체 통계 요약
    print("\n" + "=" * 60)
    print("전체 통계 요약")
    print("=" * 60)
    
    # 언어별 기본 추천 평균
    print("\n언어별 기본 추천 평균:")
    for lang in languages:
        key = f"{lang}_general"
        if key in all_results:
            results = all_results[key]
            print(f"\n  [{lang.upper()}]:")
            print(f"    MAP: {results['map']:.4f}")
            print(f"    절약율: {results['savings_rate']:.2f}%")
            for k in k_values:
                print(
                    f"    Precision@{k}: {results['precision_at_k'][k]:.4f}, "
                    f"Recall@{k}: {results['recall_at_k'][k]:.4f}, "
                    f"F1@{k}: {results['f1_at_k'][k]:.4f}"
                )
    
    # 개인화 추천 평균
    print("\n개인화 추천 평균 (모든 사용자):")
    personalized_keys = [
        k for k in all_results.keys() if not k.endswith("_general")
    ]
    if personalized_keys:
        avg_map = sum(all_results[k]["map"] for k in personalized_keys) / len(
            personalized_keys
        )
        avg_precision = {
            k: sum(all_results[key]["precision_at_k"][k] for key in personalized_keys)
            / len(personalized_keys)
            for k in k_values
        }
        avg_recall = {
            k: sum(all_results[key]["recall_at_k"][k] for key in personalized_keys)
            / len(personalized_keys)
            for k in k_values
        }
        avg_f1 = {
            k: sum(all_results[key]["f1_at_k"][k] for key in personalized_keys)
            / len(personalized_keys)
            for k in k_values
        }
        avg_savings_rate = sum(all_results[key]["savings_rate"] for key in personalized_keys) / len(
            personalized_keys
        )
        
        print(f"  MAP: {avg_map:.4f}")
        print(f"  절약율: {avg_savings_rate:.2f}%")
        for k in k_values:
            print(
                f"  Precision@{k}: {avg_precision[k]:.4f}, "
                f"Recall@{k}: {avg_recall[k]:.4f}, "
                f"F1@{k}: {avg_f1[k]:.4f}"
            )
    
    print("\n" + "=" * 60)
    print("평가 완료!")
    print("=" * 60)
    
    return all_results


if __name__ == "__main__":
    results = main()

