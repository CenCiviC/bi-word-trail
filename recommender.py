"""단어 자동완성 추천 시스템 모듈"""

from collections import defaultdict

from romaji_to_hiragana import normalize_japanese_input
from wordfreq_local import get_frequency_dict, word_frequency


class WordRecommender:
    """접두사 기반 단어 추천 클래스
    
    wordfreq 라이브러리를 사용하여 빈도 기반으로 단어를 추천합니다.
    접두사로 시작하는 단어들을 빈도 순으로 정렬하여 반환합니다.
    """

    def __init__(self, lang: str = "en", wordlist: str = "best"):
        """WordRecommender 초기화
        
        Args:
            lang: 언어 코드 (예: 'en', 'it', 'ja')
            wordlist: wordfreq의 wordlist 옵션 ('best', 'small', 'large')
        """
        self.lang: str = lang
        self.wordlist: str = wordlist
        self.prefix_index: dict[str, list[tuple[str, float]]] = defaultdict(list)
        self._build_prefix_index()

    def _build_prefix_index(self) -> None:
        """접두사별 인덱스 구축
        
        모든 단어에 대해 가능한 접두사들을 생성하고,
        각 접두사에 대해 (단어, 빈도) 튜플을 저장합니다.
        """
        print(f"[{self.lang}] 접두사 인덱스 구축 중...")
        
        # 전체 단어-빈도 딕셔너리 가져오기
        freq_dict = get_frequency_dict(self.lang, self.wordlist)
        
        # 각 단어에 대해 접두사 인덱스 구축
        for word, frequency in freq_dict.items():
            word_lower = word.lower()
            # 단어의 모든 접두사 생성 (최소 1글자부터)
            for i in range(1, len(word_lower) + 1):
                prefix = word_lower[:i]
                self.prefix_index[prefix].append((word, frequency))
        
        # 각 접두사별로 빈도 순으로 정렬 (높은 빈도가 먼저)
        for prefix in self.prefix_index:
            self.prefix_index[prefix].sort(key=lambda x: x[1], reverse=True)
        
        print(f"[{self.lang}] 인덱스 구축 완료: {len(self.prefix_index)}개 접두사")

    def recommend(
        self, prefix: str, top_n: int = 10, min_frequency: float | None = None
    ) -> list[tuple[str, float]]:
        """접두사로 시작하는 단어들을 빈도 순으로 추천
        
        Args:
            prefix: 검색할 접두사 (예: "wo")
            top_n: 반환할 최대 단어 개수
            min_frequency: 최소 빈도 임계값 (None이면 제한 없음)
        
        Returns:
            (단어, 빈도) 튜플의 리스트, 빈도 순으로 정렬됨
        """
        prefix_lower = prefix.lower()
        
        # 접두사로 시작하는 단어들 가져오기
        candidates = self.prefix_index.get(prefix_lower, [])
        
        # 최소 빈도 필터링
        if min_frequency is not None:
            candidates = [(word, freq) for word, freq in candidates if freq >= min_frequency]
        
        # 상위 N개 반환
        return candidates[:top_n]

    def get_word_frequency(self, word: str) -> float:
        """특정 단어의 빈도 조회
        
        Args:
            word: 조회할 단어
        
        Returns:
            단어의 빈도 (0.0 ~ 1.0 사이의 값)
        """
        return word_frequency(word, self.lang, self.wordlist)


class MultiLanguageRecommender:
    """다국어 단어 추천 시스템
    
    여러 언어를 동시에 지원하는 추천 시스템입니다.
    """

    def __init__(self, languages: list[str] | None = None, wordlist: str = "best"):
        """MultiLanguageRecommender 초기화
        
        Args:
            languages: 지원할 언어 코드 리스트 (기본값: ['en', 'it', 'ja'])
            wordlist: wordfreq의 wordlist 옵션
        """
        if languages is None:
            languages = ["en", "it", "ja"]
        
        self.languages: list[str] = languages
        self.wordlist: str = wordlist
        self.recommenders: dict[str, WordRecommender] = {}
        
        # 각 언어별로 Recommender 생성
        for lang in languages:
            print(f"\n언어 '{lang}' 초기화 중...")
            self.recommenders[lang] = WordRecommender(lang, wordlist)

    def recommend(
        self,
        prefix: str,
        lang: str,
        top_n: int = 10,
        min_frequency: float | None = None,
    ) -> list[tuple[str, float]]:
        """특정 언어에 대해 단어 추천
        
        Args:
            prefix: 검색할 접두사
            lang: 언어 코드
            top_n: 반환할 최대 단어 개수
            min_frequency: 최소 빈도 임계값
        
        Returns:
            (단어, 빈도) 튜플의 리스트
        """
        if lang not in self.recommenders:
            raise ValueError(f"지원하지 않는 언어: {lang}. 지원 언어: {self.languages}")
        
        # 일본어인 경우 로마자 입력을 히라가나로 변환
        if lang == "ja":
            prefix = normalize_japanese_input(prefix)
        
        return self.recommenders[lang].recommend(prefix, top_n, min_frequency)

    def get_word_frequency(self, word: str, lang: str) -> float:
        """특정 언어에서 단어의 빈도 조회
        
        Args:
            word: 조회할 단어
            lang: 언어 코드
        
        Returns:
            단어의 빈도
        """
        if lang not in self.recommenders:
            raise ValueError(f"지원하지 않는 언어: {lang}")
        
        return self.recommenders[lang].get_word_frequency(word)

