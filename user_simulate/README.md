# 사용자 시뮬레이션 및 개인화 추천 테스트

이 폴더는 사용자별 문장 데이터를 생성하고, 개인화된 추천 시스템을 테스트하는 스크립트들을 포함합니다.

## 실행 순서

### 1단계: 사용자별 문장 데이터 생성

각 사용자(개발자, 작가, 비즈니스맨, 학생, 일반 사용자)별로 2000개의 문장을 생성합니다.

```bash
uv run python user_simulate/generate_user_data.py
```

생성되는 파일:
- `developer_sentences.txt` - 개발자 문장 2000개
- `writer_sentences.txt` - 작가 문장 2000개
- `business_sentences.txt` - 비즈니스맨 문장 2000개
- `student_sentences.txt` - 학생 문장 2000개
- `general_sentences.txt` - 일반 사용자 문장 2000개

### 2단계: 사용자 프로필 구축

생성된 문장 데이터를 분석하여 각 사용자의 단어 사용 패턴을 추출하고 프로필을 구축합니다.

```bash
uv run python user_simulate/build_profiles.py
```

출력 정보:
- 각 사용자별 총 단어 사용 횟수
- 고유 단어 수
- 가장 많이 사용한 단어 Top 5

### 3단계: 개인화 추천 효율성 테스트

구축된 프로필을 기반으로 개인화된 추천이 얼마나 더 효율적인지 비교합니다.

```bash
uv run python user_simulate/test_personalization.py
```

테스트 내용:
- 기본 추천 vs 개인화 추천의 입력 글자 수 비교
- 사용자별 개선률 및 절약 글자 수 측정
- 개선된 단어 사례 분석
- 전체 통계 요약

## 전체 실행 (한 번에)

```bash
# 1. 문장 생성
uv run python user_simulate/generate_user_data.py

# 2. 프로필 구축
uv run python user_simulate/build_profiles.py

# 3. 테스트 실행
uv run python user_simulate/test_personalization.py
```

## 예상 결과

개인화 추천은 기본 추천보다 평균 **45% 정도 더 효율적**입니다.

### 효율성 개선 예시

- **개발자**: 평균 48.61% 개선 (예: "code" 3글자 → 1글자)
- **작가**: 평균 43.08% 개선 (예: "story" 2글자 → 1글자)
- **비즈니스맨**: 평균 45.71% 개선 (예: "company" 3글자 → 1글자)
- **학생**: 평균 43.75% 개선 (예: "study" 2글자 → 1글자)

### 주요 개선 사례

- 자주 사용하는 단어들이 더 빠르게 추천됨
- 접두사 입력이 줄어들어 타이핑 속도 향상
- 사용자별 맞춤 추천으로 만족도 증가

