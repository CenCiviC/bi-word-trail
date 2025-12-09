"""단어 자동완성 추천 시스템 웹 인터페이스"""

import json
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from main import (
    find_min_prefix_for_word,
    split_sentence_to_words,
    test_sentence_autocomplete,
)
from src.recommender import MultiLanguageRecommender
from src.user_profile import UserProfile, UserProfileManager

app = Flask(__name__)

# 전역 추천 시스템 (초기화는 첫 요청 시)
recommender: MultiLanguageRecommender | None = None
profile_managers: dict[str, UserProfileManager] = {}


def get_recommender() -> MultiLanguageRecommender:
    """추천 시스템을 가져오거나 초기화합니다."""
    global recommender
    if recommender is None:
        recommender = MultiLanguageRecommender(languages=["en", "it", "ja"])
    return recommender


def load_profiles() -> dict[str, UserProfileManager]:
    """사용자 프로필을 로드합니다."""
    global profile_managers
    if not profile_managers:
        try:
            from user_simulate.build_profiles import main as build_profiles_main

            profile_managers, _ = build_profiles_main()
        except Exception as e:
            print(f"프로필 로드 실패: {e}")
            profile_managers = {}
    return profile_managers


@app.route("/")
def index():
    """메인 페이지"""
    return render_template("index.html")


@app.route("/api/recommend", methods=["POST"])
def api_recommend():
    """단어 추천 API"""
    data = request.json
    prefix = data.get("prefix", "")
    lang = data.get("lang", "en")
    top_n = data.get("top_n", 10)
    user_id = data.get("user_id", None)
    user_lang = data.get("user_lang", lang)

    if not prefix:
        return jsonify({"error": "접두사가 필요합니다"}), 400

    rec = get_recommender()
    user_profile = None

    # 사용자 프로필 로드
    if user_id:
        profiles = load_profiles()
        if user_lang in profiles:
            profile_manager = profiles[user_lang]
            if user_id in profile_manager.profiles:
                user_profile = profile_manager.profiles[user_id]

    try:
        recommendations = rec.recommend(
            prefix=prefix, lang=lang, top_n=top_n, user_profile=user_profile
        )
        return jsonify(
            {
                "success": True,
                "recommendations": [
                    {"word": word, "score": float(score)} for word, score in recommendations
                ],
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/test-sentence", methods=["POST"])
def api_test_sentence():
    """문장 자동완성 효율 테스트 API"""
    data = request.json
    sentence = data.get("sentence", "")
    lang = data.get("lang", "en")
    user_id = data.get("user_id", None)
    user_lang = data.get("user_lang", lang)

    if not sentence:
        return jsonify({"error": "문장이 필요합니다"}), 400

    rec = get_recommender()
    user_profile = None

    # 사용자 프로필 로드
    if user_id:
        profiles = load_profiles()
        if user_lang in profiles:
            profile_manager = profiles[user_lang]
            if user_id in profile_manager.profiles:
                user_profile = profile_manager.profiles[user_id]

    try:
        result = test_sentence_autocomplete(
            rec, sentence, lang, user_profile=user_profile, return_word_details=True
        )
        if result:
            return jsonify({"success": True, "result": result})
        else:
            return jsonify({"error": "문장 처리 실패"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/test-batch", methods=["POST"])
def api_test_batch():
    """여러 문장 일괄 테스트 API"""
    data = request.json
    sentences = data.get("sentences", [])
    lang = data.get("lang", "en")
    user_id = data.get("user_id", None)
    user_lang = data.get("user_lang", lang)

    if not sentences:
        return jsonify({"error": "문장 리스트가 필요합니다"}), 400

    rec = get_recommender()
    user_profile = None

    # 사용자 프로필 로드
    if user_id:
        profiles = load_profiles()
        if user_lang in profiles:
            profile_manager = profiles[user_lang]
            if user_id in profile_manager.profiles:
                user_profile = profile_manager.profiles[user_id]

    results = []
    for sentence in sentences:
        try:
            result = test_sentence_autocomplete(rec, sentence, lang, user_profile=user_profile)
            if result:
                results.append(result)
        except Exception:
            continue

    if not results:
        return jsonify({"error": "처리된 문장이 없습니다"}), 400

    # 통계 계산
    total_chars_without = sum(r["total_chars_without"] for r in results)
    total_chars_with = sum(r["total_chars_with"] for r in results)
    total_chars_saved = sum(r["chars_saved"] for r in results)
    avg_savings_rate = (
        (1 - total_chars_with / total_chars_without) * 100
        if total_chars_without > 0
        else 0
    )

    return jsonify(
        {
            "success": True,
            "results": results,
            "statistics": {
                "sentence_count": len(results),
                "total_chars_without": total_chars_without,
                "total_chars_with": total_chars_with,
                "total_chars_saved": total_chars_saved,
                "avg_savings_rate": round(avg_savings_rate, 2),
            },
        }
    )


@app.route("/api/users", methods=["GET"])
def api_users():
    """사용 가능한 사용자 프로필 목록 API"""
    profiles = load_profiles()
    users = {}
    for lang, profile_manager in profiles.items():
        users[lang] = list(profile_manager.profiles.keys())
    return jsonify({"success": True, "users": users})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)

