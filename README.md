# Word Trail

단어 자동완성 추천 시스템

영어, 이탈리아어, 일본어 입력 시 접두사 기반으로 빈도 순 단어를 추천하는 시스템입니다.

## 기능

- 접두사 기반 단어 추천 (예: "wo" → "word", "world")
- wordfreq 라이브러리를 사용한 빈도 기반 정렬
- 다국어 지원 (영어, 이탈리아어, 일본어)
- 사용자 피드백 기반 개인화 추천
- 사용자별 문장 패턴 분석 및 프로필 구축

## 설치

```bash
uv sync
```

## 사용법

### 기본 추천 시스템 실행

```bash
uv run python main.py
```

### 사용자 시뮬레이션 및 개인화 추천 테스트

**방법 1: 전체 실행 (권장)**
```bash
uv run python user_simulate/run_all.py
```

**방법 2: 단계별 실행**
```bash
# 1단계: 사용자별 문장 생성
uv run python user_simulate/generate_user_data.py

# 2단계: 프로필 구축
uv run python user_simulate/build_profiles.py

# 3단계: 개인화 추천 테스트
uv run python user_simulate/test_personalization.py
```

## 예제

```python
from src.recommender import MultiLanguageRecommender

# 다국어 추천 시스템 초기화
recommender = MultiLanguageRecommender(languages=["en", "it", "ja"])

# 영어 단어 추천
recommendations = recommender.recommend("wo", lang="en", top_n=10)
for word, freq in recommendations:
    print(f"{word}: {freq:.2e}")
```

