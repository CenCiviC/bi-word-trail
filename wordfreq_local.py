"""wordfreq 라이브러리의 핵심 함수들을 로컬에서 사용하기 위한 모듈"""

from __future__ import annotations

import gzip
from functools import lru_cache
from pathlib import Path
from typing import Iterator

import msgpack

# word-trail 폴더 내의 데이터 경로 설정
WORDFREQ_DATA_PATH = Path(__file__).parent / "data"


def read_cBpack(filename: str) -> list[list[str]]:
    """
    cBpack 형식의 파일을 읽어옵니다.
    
    cBpack 형식은 wordfreq에서 사용하는 압축된 단어 빈도 데이터 형식입니다.
    """
    with gzip.open(filename, "rb") as infile:
        data = msgpack.load(infile, raw=False)
    header = data[0]
    if not isinstance(header, dict) or header.get("format") != "cB" or header.get("version") != 1:
        raise ValueError("Unexpected header: %r" % header)
    return data[1:]


def available_languages(wordlist: str = "best") -> dict[str, str]:
    """
    주어진 wordlist에 대해 사용 가능한 언어 코드와 파일 경로를 반환합니다.
    
    Args:
        wordlist: 'best', 'small', 'large' 중 하나
    
    Returns:
        언어 코드를 키로 하고 파일 경로를 값으로 하는 딕셔너리
    """
    if wordlist == "best":
        available = available_languages("small")
        available.update(available_languages("large"))
        return available
    elif wordlist == "combined":
        wordlist = "small"

    available = {}
    for path in WORDFREQ_DATA_PATH.glob("*.msgpack.gz"):
        if not path.name.startswith("_"):
            list_name = path.name.split(".")[0]
            name, lang = list_name.split("_")
            if name == wordlist:
                available[lang] = str(path)
    return available


@lru_cache(maxsize=None)
def get_frequency_list(
    lang: str, wordlist: str = "best", match_cutoff: None = None
) -> list[list[str]]:
    """
    wordlist 파일에서 원시 데이터를 읽어옵니다.
    
    Args:
        lang: 언어 코드 (예: 'en', 'it', 'ja')
        wordlist: 'best', 'small', 'large' 중 하나
        match_cutoff: 사용되지 않음 (하위 호환성)
    
    Returns:
        단어 리스트의 리스트 (각 내부 리스트는 같은 빈도를 가진 단어들)
    """
    if match_cutoff is not None:
        pass  # 무시
    
    available = available_languages(wordlist)
    
    # 간단한 언어 매칭 (langcodes 없이)
    if lang in available:
        best = lang
    else:
        # 대소문자 무시 매칭
        lang_lower = lang.lower()
        best = None
        for available_lang in available:
            if available_lang.lower() == lang_lower:
                best = available_lang
                break
        
        if best is None:
            raise LookupError(f"No wordlist {wordlist!r} available for language {lang!r}")
    
    return read_cBpack(available[best])


def cB_to_freq(cB: int) -> float:
    """
    centibel 단위의 빈도를 0~1 사이의 비율로 변환합니다.
    
    centibel은 wordfreq에서 사용하는 로그 스케일입니다.
    0 cB는 최대 빈도 1.0을 나타내고, -100 cB는 10번 중 1번을 나타냅니다.
    """
    if cB > 0:
        raise ValueError("A frequency cannot be a positive number of centibels.")
    return 10 ** (cB / 100)


@lru_cache(maxsize=None)
def get_frequency_dict(
    lang: str, wordlist: str = "best", match_cutoff: None = None
) -> dict[str, float]:
    """
    wordlist를 딕셔너리 형태로 가져옵니다.
    
    Args:
        lang: 언어 코드
        wordlist: 'best', 'small', 'large' 중 하나
        match_cutoff: 사용되지 않음
    
    Returns:
        단어를 키로 하고 빈도를 값으로 하는 딕셔너리
    """
    if match_cutoff is not None:
        pass  # 무시
    
    freqs = {}
    pack = get_frequency_list(lang, wordlist)
    for index, bucket in enumerate(pack):
        freq = cB_to_freq(-index)
        for word in bucket:
            freqs[word] = freq
    return freqs


def iter_wordlist(lang: str, wordlist: str = "best") -> Iterator[str]:
    """
    wordlist의 단어들을 빈도 순으로 반환합니다.
    
    Args:
        lang: 언어 코드
        wordlist: 'best', 'small', 'large' 중 하나
    
    Yields:
        단어 문자열들 (빈도 순)
    """
    import itertools
    return itertools.chain(*get_frequency_list(lang, wordlist))


def word_frequency(word: str, lang: str, wordlist: str = "best", minimum: float = 0.0) -> float:
    """
    특정 단어의 빈도를 조회합니다.
    
    Args:
        word: 조회할 단어
        lang: 언어 코드
        wordlist: 'best', 'small', 'large' 중 하나
        minimum: 최소 빈도값 (기본값: 0.0)
    
    Returns:
        단어의 빈도 (0.0 ~ 1.0 사이의 값)
    """
    freq_dict = get_frequency_dict(lang, wordlist)
    word_lower = word.lower()
    
    # 단순화된 버전: 정확히 일치하는 단어만 찾기
    # 원래 wordfreq는 토크나이징을 하지만, 여기서는 단순화
    if word_lower in freq_dict:
        return max(freq_dict[word_lower], minimum)
    
    # 원본 단어도 시도
    if word in freq_dict:
        return max(freq_dict[word], minimum)
    
    return minimum

