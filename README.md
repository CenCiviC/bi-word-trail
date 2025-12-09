# Word Trail

단어 자동완성 추천 시스템

영어, 이탈리아어, 일본어 입력 시 접두사 기반으로 빈도 순 단어를 추천하는 시스템입니다.

## 기능

- 접두사 기반 단어 추천 (예: "wo" → "word", "world")
- wordfreq 라이브러리를 사용한 빈도 기반 정렬
- 다국어 지원 (영어, 이탈리아어, 일본어)

## 설치

```bash
uv sync
```

## 사용법

```bash
uv run python main.py
```

## 예제

```python
from recommender import MultiLanguageRecommender

# 다국어 추천 시스템 초기화
recommender = MultiLanguageRecommender(languages=["en", "it", "ja"])

# 영어 단어 추천
recommendations = recommender.recommend("wo", lang="en", top_n=10)
for word, freq in recommendations:
    print(f"{word}: {freq:.2e}")
```

