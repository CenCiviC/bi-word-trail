"""모든 사용자 시뮬레이션 단계를 순차적으로 실행하는 스크립트"""

import subprocess
import sys
from pathlib import Path


def run_script(script_name: str, description: str) -> bool:
    """스크립트를 실행합니다.
    
    Args:
        script_name: 실행할 스크립트 이름
        description: 스크립트 설명
    
    Returns:
        성공 여부
    """
    print("\n" + "=" * 60)
    print(f"{description}")
    print("=" * 60)
    
    script_path = Path(__file__).parent / script_name
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=Path(__file__).parent.parent,
            check=True,
            capture_output=False,
        )
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"오류 발생: {e}")
        return False
    except Exception as e:
        print(f"예상치 못한 오류: {e}")
        return False


def main():
    """메인 함수 - 모든 단계를 순차적으로 실행"""
    print("=" * 60)
    print("사용자 시뮬레이션 전체 실행")
    print("=" * 60)
    
    steps = [
        ("generate_user_data.py", "1단계: 사용자별 문장 데이터 생성"),
        ("build_profiles.py", "2단계: 사용자 프로필 구축"),
        ("test_personalization.py", "3단계: 개인화 추천 테스트"),
        ("compare_savings_rate.py", "4단계: 개인화 추천 절약율 비교"),
    ]
    
    for script_name, description in steps:
        success = run_script(script_name, description)
        
        if not success:
            print(f"\n오류: {description} 단계에서 실패했습니다.")
            sys.exit(1)
    
    print("\n" + "=" * 60)
    print("모든 단계 완료!")
    print("=" * 60)


if __name__ == "__main__":
    main()

