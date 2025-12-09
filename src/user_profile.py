"""사용자 프로필 및 피드백 관리 모듈"""

from collections import defaultdict
from datetime import datetime


class UserProfile:
    """사용자별 단어 사용 히스토리를 관리하는 클래스
    
    사용자가 선택한 단어들을 기록하고, 이를 바탕으로 개인화된 추천을 제공합니다.
    """

    def __init__(self, user_id: str):
        """UserProfile 초기화
        
        Args:
            user_id: 사용자 고유 ID
        """
        self.user_id: str = user_id
        # 단어별 사용 횟수 (전체 기간)
        self.word_counts: dict[str, int] = defaultdict(int)
        # 단어별 최근 사용 시간 (시간 기반 가중치 계산용)
        self.word_timestamps: dict[str, list[datetime]] = defaultdict(list)
        # 접두사별 선택된 단어 기록
        self.prefix_selections: dict[str, list[str]] = defaultdict(list)

    def record_word_selection(self, word: str, prefix: str = "") -> None:
        """사용자가 단어를 선택했을 때 기록합니다.
        
        Args:
            word: 선택된 단어
            prefix: 입력했던 접두사 (선택사항)
        """
        word_lower = word.lower()
        self.word_counts[word_lower] += 1
        self.word_timestamps[word_lower].append(datetime.now())
        
        if prefix:
            self.prefix_selections[prefix.lower()].append(word_lower)

    def get_word_score(
        self, word: str, base_frequency: float, time_decay_factor: float = 0.95
    ) -> float:
        """단어의 개인화된 점수를 계산합니다.
        
        Args:
            word: 점수를 계산할 단어
            base_frequency: 기본 빈도 (wordfreq에서 가져온 값)
            time_decay_factor: 시간 감쇠 계수 (0~1, 기본값 0.95)
        
        Returns:
            개인화된 점수 (기본 빈도 + 사용자 가중치)
        """
        word_lower = word.lower()
        
        # 기본 빈도 점수
        base_score = base_frequency
        
        # 사용자 사용 횟수 기반 가중치
        usage_count = self.word_counts.get(word_lower, 0)
        
        if usage_count == 0:
            return base_score
        
        # 시간 기반 가중치 계산 (최근 사용일수록 높은 가중치)
        time_weight = 0.0
        now = datetime.now()
        
        for timestamp in self.word_timestamps.get(word_lower, []):
            # 시간 차이 (일 단위)
            days_ago = (now - timestamp).days
            
            # 지수 감쇠: 최근 사용일수록 높은 가중치
            decay = time_decay_factor ** days_ago
            time_weight += decay
        
        # 사용 횟수와 시간 가중치를 결합
        # 사용 횟수가 많을수록, 최근 사용일수록 높은 점수
        user_weight = usage_count * (1 + time_weight * 0.1)
        
        # 개인화 점수 = 기본 빈도 * (1 + 사용자 가중치)
        # 사용자 가중치는 기본 빈도에 비례하여 적용
        personalized_score = base_score * (1 + user_weight * 10)
        
        return personalized_score

    def get_prefix_history(self, prefix: str) -> dict[str, int]:
        """특정 접두사에 대해 사용자가 선택한 단어들의 히스토리를 반환합니다.
        
        Args:
            prefix: 접두사
        
        Returns:
            단어별 선택 횟수 딕셔너리
        """
        prefix_lower = prefix.lower()
        selections = self.prefix_selections.get(prefix_lower, [])
        
        history: dict[str, int] = defaultdict(int)
        for word in selections:
            history[word] += 1
        
        return dict(history)


class UserProfileManager:
    """여러 사용자 프로필을 관리하는 클래스"""

    def __init__(self):
        """UserProfileManager 초기화"""
        self.profiles: dict[str, UserProfile] = {}

    def get_profile(self, user_id: str) -> UserProfile:
        """사용자 프로필을 가져오거나 생성합니다.
        
        Args:
            user_id: 사용자 ID
        
        Returns:
            UserProfile 인스턴스
        """
        if user_id not in self.profiles:
            self.profiles[user_id] = UserProfile(user_id)
        return self.profiles[user_id]

    def simulate_user_behavior(
        self, user_id: str, word_selections: list[tuple[str, str]]
    ) -> None:
        """사용자 행동을 시뮬레이션합니다.
        
        Args:
            user_id: 사용자 ID
            word_selections: (접두사, 선택된_단어) 튜플 리스트
        """
        profile = self.get_profile(user_id)
        for prefix, word in word_selections:
            profile.record_word_selection(word, prefix)

