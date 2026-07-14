"""
29_rl_path.py - 강화학습 경로 설계
====================================
간단한 강화학습(RL) 개념으로 최적 경로/구조를 탐색합니다.

- 상태/행동/보상 정의
- 탐욕 정책 기반 최적화
- 시각화

작성일: 2026-07-14
"""

import math
import random
from typing import List, Tuple, Dict, Optional

# FreeCAD 환경 확인
FREECAD_AVAILABLE = False
try:
    import FreeCAD
    import Part
    from FreeCAD import Base
    FREECAD_AVAILABLE = True
except ImportError:
    print("[정보] FreeCAD 모듈을 사용할 수 없습니다. 시뮬레이션 모드로 동작합니다.")

# 시각화 라이브러리 확인
VISUALIZE_AVAILABLE = False
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    VISUALIZE_AVAILABLE = True
except ImportError:
    print("[정보] matplotlib이 없습니다. 텍스트 기반 시각화를 사용합니다.")


# ============================================================================
# 격자 환경 정의
# ============================================================================

class 격자환경:
    """
    2D 격자 기반 경로 탐색 환경.
    에이전트가 시작점에서 목표점까지 최적 경로를 탐색합니다.
    """

    def __init__(self, 가로: int = 20, 세로: int = 15):
        self.가로 = 가로
        self.세로 = 세로
        self.시작점 = (0, 0)
        self.목표점 = (가로 - 1,세로 - 1)
        self.장애물: List[Tuple[int, int]] = []
        self.현재위치 = self.시작점

        # 장애물 자동 생성
        self._장애물_생성()

    def _장애물_생성(self):
        """장애물을 무작위로 생성합니다."""
        self.장애물 = []
        전체셀 = self.가로 * self.세로
        장애물_수 = int(전체셀 * 0.15)  # 전체 셀의 15%

        for _ in range(장애물_수):
            x = random.randint(0, self.가로 - 1)
            y = random.randint(0, self.세로 - 1)
            if (x, y) != self.시작점 and (x, y) != self.목표점:
                if (x, y) not in self.장애물:
                    self.장애물.append((x, y))

    def 초기화(self):
        """환경을 초기 상태로 리셋합니다."""
        self.현재위치 = self.시작점
        return self.현재위치

    def 상태(self) -> Tuple[int, int]:
        """현재 상태(위치)를 반환합니다."""
        return self.현재위치

    def 행동_가능(self, 행동: int) -> bool:
        """
        행동이 가능한지 확인합니다.
        행동: 0=상, 1=하, 2=좌, 3=우, 4=좌상, 5=우상, 6=좌하, 7=우하
        """
        x, y = self.현재위치
        이동 = {
            0: (0, 1), 1: (0, -1), 2: (-1, 0), 3: (1, 0),
            4: (-1, 1), 5: (1, 1), 6: (-1, -1), 7: (1, -1),
        }

        dx, dy = 이동[행동]
        nx, ny = x + dx, y + dy

        # 경계 확인
        if nx < 0 or nx >= self.가로 or ny < 0 or ny >= self.세로:
            return False

        # 장애물 확인
        if (nx, ny) in self.장애물:
            return False

        return True

    def 행동(self, 행동: int) -> Tuple[Tuple[int, int], float, bool]:
        """
        행동을 수행하고 (새 상태, 보상, 종료 여부)를 반환합니다.
        """
        if not self.행동_가능(행동):
            return self.현재위치, -5.0, False  # 벽/장애물 충돌 페널티

        이동 = {
            0: (0, 1), 1: (0, -1), 2: (-1, 0), 3: (1, 0),
            4: (-1, 1), 5: (1, 1), 6: (-1, -1), 7: (1, -1),
        }

        dx, dy = 이동[행동]
        self.현재위치 = (self.현재위치[0] + dx, self.현재위치[1] + dy)

        # 보상 계산
        if self.현재위치 == self.목표점:
            return self.현재위치, 100.0, True  # 목표 도달 큰 보상

        # 목표와의 거리 기반 보상 (가까워지면 양수, 멀어지면 음수)
        이전거리 = abs(self.시작점[0] - self.목표점[0]) + abs(self.시작점[1] - self.목표점[1])
        현재거리 = abs(self.현재위치[0] - self.목표점[0]) + abs(self.현재위치[1] - self.목표점[1])
        보상 = (이전거리 - 현재거리) * 0.5 - 0.1  # 거리 단축 보상 + 스텝 페널티

        # 시작점으로 돌아가는 페널티
        if self.현재위치 == self.시작점 and self.시작점 != self.시작점:
            보상 -= 2.0

        return self.현재위치, 보상, False


# ============================================================================
# Q-러닝 에이전트
# ============================================================================

class Q러닝에이전트:
    """탐욕(greedy) 정책 기반 Q-러닝 에이전트"""

    def __init__(self, 행동수: int = 8, 학습률: int = 0.1, 감가율: float = 0.95,
                 탐험률: float = 0.3):
        self.행동수 = 행동수
        # Q-테이블: {(상태_x, 상태_y): [Q값_행동0, Q값_행동1, ...]}
        self.Q: Dict[Tuple[int, int], List[float]] = {}
        self.학습률 = 학습률
        self.감가율 = 감가율
        self.탐험률 = 탐험률

    def Q값_가져오기(self, 상태: Tuple[int, int]) -> List[float]:
        """특정 상태의 Q값을 반환합니다. 없으면 초기화합니다."""
        if 상태 not in self.Q:
            self.Q[상태] = [0.0] * self.행동수
        return self.Q[상태]

    def 행동_선택(self, 상태: Tuple[int, int], 환경: 격자환경) -> int:
        """ε-탐욕 정책으로 행동을 선택합니다."""
        if random.random() < self.탐험률:
            # 탐험: 가능한 행동 중 무작위 선택
            가능한행동 = [a for a in range(self.행동수) if 환경.행동_가능(a)]
            if not 가능한행동:
                return 0
            return random.choice(가능한행동)

        # 활용: Q값이 가장 높은 행동 선택
        Q값 = self.Q값_가져오기(상태)
        가능한행동 = [a for a in range(self.행동수) if 환경.행동_가능(a)]

        if not 가능한행동:
            return 0

        최적행동 = max(가능한행동, key=lambda a: Q값[a])
        return 최적행동

    def 학습(self, 상태: Tuple[int, int], 행동: int, 보상: float,
             다음상태: Tuple[int, int], 종료: bool):
        """Q값을 업데이트합니다."""
        Q값 = self.Q값_가져오기(상태)
        다음Q값 = self.Q값_가져오기(다음상태)

        if 종료:
            목표값 = 보상
        else:
            목표값 = 보상 + self.감가율 * max(다음Q값)

        Q값[행동] += self.학습률 * (목표값 - Q값[행동])

    def 탐험률_감소(self, 최소탐험률: float = 0.05):
        """탐험률을 점진적으로 감소시킵니다."""
        self.탐험률 = max(최소탐험률, self.탐험률 * 0.995)


# ============================================================================
# 학습 루프
# ============================================================================

class RL경로학습기:
    """강화학습 기반 경로 학습기"""

    def __init__(self, 환경: 격자환경, 에이전트: Q러닝에이전트):
        self.환경 = 환경
        self.에이전트 = 에이전트
        self.학습이력: List[Dict] = []

    def 학습(self, 에피소드수: int = 200, 최대스텝: int = 100) -> List[Dict]:
        """에피소드 기반 학습을 수행합니다."""
        print(f"\n[학습 시작] 에피소드: {에피소드수}회, 최대 스텝: {최대스텝}회")

        for 에피소드 in range(1, 에피소드수 + 1):
            상태 = self.환경.초기화()
            총보상 = 0
            경로: List[Tuple[int, int]] = [상태]

            for 스텝 in range(최대스텝):
                # 행동 선택
                행동 = self.에이전트.행동_선택(상태, self.환경)

                # 행동 수행
                다음상태, 보상, 종료 = self.환경.행동(행동)

                # 학습
                self.에이전트.학습(상태, 행동, 보상, 다음상태, 종료)

                총보상 += 보상
                경로.append(다음상태)
                상태 = 다음상태

                if 종료:
                    break

            # 탐험률 감소
            self.에이전트.탐험률_감소()

            # 이력 기록
            도달여부 = self.환경.현재위치 == self.환경.목표점
            기록 = {
                "에피소드": 에피소드,
                "총보상": 총보상,
                "스텝수": len(경로),
                "도달": 도달여부,
                "경로": 경로,
                "탐험률": self.에이전트.탐험률,
            }
            self.학습이력.append(기록)

            if 에피소드 % 20 == 0 or 도달여부:
                상태_표시 = "도달" if 도달여부 else "실패"
                print(f"  에피소드 {에피소드:>4d} | "
                      f"보상: {총보상:>7.1f} | "
                      f"스텝: {len(경로):>3d} | "
                      f"{상태_표시} | "
                      f"탐험: {self.에이전트.탐험률:.3f}")

        print("[학습 완료]")
        return self.학습이력

    def 탐욕_경로_획득(self) -> List[Tuple[int, int]]:
        """학습된 정책으로 탐욕 경로를 반환합니다."""
        self.환경.초기화()
        경로 = [self.환경.상태()]

        for _ in range(200):
            상태 = self.환경.상태()
            Q값 = self.에이전트.Q값_가져오기(상태)
            가능한행동 = [a for a in range(self.에이전트.행동수) if self.환경.행동_가능(a)]

            if not 가능한행동:
                break

            행동 = max(가능한행동, key=lambda a: Q값[a])
            다음상태, 보상, 종료 = self.환경.행동(행동)
            경로.append(다음상태)

            if 종료:
                break

        return 경로


# ============================================================================
# 시각화
# ============================================================================

class 경로시각화:
    """학습 결과와 경로를 시각화하는 클래스"""

    @staticmethod
    def 텍스트_시각화(환경: 격자환경, 경로: List[Tuple[int, int]]):
        """텍스트 기반 격자 시각화"""
        격자 = [["." for _ in range(환경.가로)] for _ in range(환경.세로)]

        # 장애물 표시
        for x, y in 환경.장애물:
            격자[y][x] = "X"

        # 경로 표시
        for i, (x, y) in enumerate(경로):
            if 0 <= y < 환경.세로 and 0 <= x < 환경.가로:
                if 격자[y][x] != "X":
                    격자[y][x] = "*"

        # 시작/목표 표시
        sx, sy = 환경.시작점
        gx, gy = 환경.목표점
        격자[sy][sx] = "S"
        격자[gy][gx] = "G"

        print("\n  격자 시각화 (S=시작, G=목표, X=장애물, *=경로):")
        print("  +" + "-" * (환경.가로 * 2 + 1) + "+")
        for row in reversed(격자):
            print("  | " + " ".join(row) + " |")
        print("  +" + "-" * (환경.가로 * 2 + 1) + "+")

    @staticmethod
    def 학습곡선_시각화(이력: List[Dict], 저장경로: str = None):
        """학습 곡선을 시각화합니다."""
        if not VISUALIZE_AVAILABLE:
            print("\n  [정보] matplotlib이 없어 텍스트 학습 곡선을 표시합니다.")
            print(f"  {'에피소드':>8} {'총보상':>10} {'도달':>6}")
            print(f"  {'-' * 28}")
            for 기록 in 이력[::max(1, len(이력) // 10)]:
                도달 = "O" if 기록['도달'] else "X"
                print(f"  {기록['에피소드']:>8d} {기록['총보상']:>10.1f} {도달:>6}")
            return

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

        에피소드 = [기록["에피소드"] for 기록 in 이력]
        보상 = [기록["총보상"] for 기록 in 이력]
        스텝 = [기록["스텝수"] for 기록 in 이력]

        # 총보상 곡선
        ax1.plot(에피소드, 보상, "b-", alpha=0.3, label="총보상")
        # 이동평균
        if len(보상) >= 10:
            이동평균 = [sum(보상[max(0, i-9):i+1]) / min(10, i+1) for i in range(len(보상))]
            ax1.plot(에피소드, 이동평균, "r-", linewidth=2, label="이동평균(10)")
        ax1.set_xlabel("에피소드")
        ax1.set_ylabel("총보상")
        ax1.set_title("강화학습 보상 곡선")
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # 스텝 수 곡선
        ax2.plot(에피소드, 스텝, "g-", alpha=0.3, label="스텝 수")
        ax2.set_xlabel("에피소드")
        ax2.set_ylabel("스텝 수")
        ax2.set_title("에피소드별 스텝 수")
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()

        if 저장경로:
            plt.savefig(저장경로, dpi=100)
            print(f"[정보] 학습 곡선 이미지 저장: {저장경로}")
        else:
            plt.savefig("C:\\Users\\Administrator\\Downloads\\py\\src\\29_rl_learning_curve.png",
                        dpi=100)
            print("[정보] 학습 곡선 이미지 저장: 29_rl_learning_curve.png")

        plt.close()

    @staticmethod
    def 최종경로_시각화(환경: 격자환경, 경로: List[Tuple[int, int]],
                       저장경로: str = None):
        """최종 경로를 시각화합니다."""
        if not VISUALIZE_AVAILABLE:
            return

        fig, ax = plt.subplots(1, 1, figsize=(12, 8))

        # 격자 배경
        for x in range(환경.가로):
            for y in range(환경.세로):
                if (x, y) in 환경.장애물:
                    rect = mpatches.Rectangle((x - 0.5, y - 0.5), 1, 1,
                                              facecolor="gray", edgecolor="black")
                    ax.add_patch(rect)

        # 경로 그리기
        if 경로:
            xs = [p[0] for p in 경로]
            ys = [p[1] for p in 경로]
            ax.plot(xs, ys, "b-o", markersize=4, linewidth=2, label="경로")

        # 시작/목표점
        ax.plot(환경.시작점[0], 환경.시작점[1], "go", markersize=15, label="시작")
        ax.plot(환경.목표점[0], 환경.목표점[1], "r*", markersize=20, label="목표")

        ax.set_xlim(-1, 환경.가로)
        ax.set_ylim(-1, 환경.세로)
        ax.set_aspect("equal")
        ax.set_title("강화학습 기반 최적 경로")
        ax.legend()
        ax.grid(True, alpha=0.3)

        if 저장경로:
            plt.savefig(저장경로, dpi=100)
        else:
            plt.savefig("C:\\Users\\Administrator\\Downloads\\py\\src\\29_rl_final_path.png",
                        dpi=100)
            print("[정보] 최종 경로 이미지 저장: 29_rl_final_path.png")

        plt.close()


# ============================================================================
# FreeCAD 경로 시뮬레이션
# ============================================================================

def FreeCAD_경로_시뮬레이션(경로: List[Tuple[int, int]], 스케일: float = 5.0):
    """학습된 경로를 FreeCAD에서 3D로 시뮬레이션합니다."""
    if not FREECAD_AVAILABLE:
        print("[정보] FreeCAD에서 경로 시뮬레이션을 수행할 수 없습니다.")
        print(f"  경로 길이: {len(경로)}개 포인트")
        return

    try:
        doc = FreeCAD.newDocument("RL경로시뮬레이션")

        # 경로 포인트를 연결하는 와이어 생성
        와이어_포인트 = []
        for x, y in 경로:
            와이어_포인트.append(Base.Vector(x * 스케일, y * 스케일, 0))

        if len(와이어_포인트) >= 2:
            와이어 = Part.makePolygon(와이어_포인트)
            obj = doc.addObject("Part::Feature", "경로")
            obj.Shape = 와이어

        # 시작점과 목표점에 구체 표시
        시작구 = Part.makeSphere(2.0, Base.Vector(경로[0][0] * 스케일,
                                                   경로[0][1] * 스케일, 0))
        obj_s = doc.addObject("Part::Feature", "시작점")
        obj_s.Shape = 시작구

        끝구 = Part.makeSphere(2.0, Base.Vector(경로[-1][0] * 스케일,
                                                 경로[-1][1] * 스케일, 0))
        obj_g = doc.addObject("Part::Feature", "목표점")
        obj_g.Shape = 끝구

        doc.recompute()
        print(f"[완료] FreeCAD 경로 시뮬레이션 생성 완료 (경로 길이: {len(경로)} 포인트)")

    except Exception as e:
        print(f"[오류] FreeCAD 경로 시뮬레이션 실패: {e}")


# ============================================================================
# 메인 실행
# ============================================================================

def 메인_실행():
    """메인 실행 함수"""
    print("=" * 60)
    print("  29. 강화학습 경로 설계")
    print("  AI 기반 생성 설계 - RL 경로 탐색 데모")
    print("=" * 60)

    random.seed(42)

    # 환경 및 에이전트 초기화
    환경 = 격자환경(가로=20,세로=15)
    에이전트 = Q러닝에이전트(
        행동수=8,
        학습률=0.1,
        감가율=0.95,
        탐험률=0.3,
    )

    print(f"\n  격자 크기: {환경.가로} x {환경.세로}")
    print(f"  장애물 수: {len(환경.장애물)}개")
    print(f"  시작점: {환경.시작점}")
    print(f"  목표점: {환경.목표점}")

    # 학습 수행
    학습기 = RL경로학습기(환경, 에이전트)
    이력 = 학습기.학습(에피소드수=200, 최대스텝=100)

    # 학습 결과 통계
    도달에피소드 = [기록 for 기록 in 이력 if 기록['도달']]
    print(f"\n  학습 통계:")
    print(f"    총 에피소드: {len(이력)}")
    print(f"    목표 도달: {len(도달에피소드)}회 "
          f"({len(도달에피소드)/len(이력)*100:.1f}%)")

    if 도달에피소드:
        최소스텝 = min(기록['스텝수'] for 기록 in 도달에피소드)
        print(f"    최단 경로: {최소스텝} 스텝")

    # 탐욕 경로 획득
    print("\n[정보] 학습된 탐욕 경로를 계산합니다...")
    최적경로 = 학습기.탐욕_경로_획득()
    print(f"  탐욕 경로 길이: {len(최적경로)} 포인트")
    print(f"  경로 시작: {최적경로[0]}")
    print(f"  경로 끝: {최적경로[-1]}")

    # 시각화
    print("\n[정보] 시각화를 수행합니다...")
    경로시각화.텍스트_시각화(환경, 최적경로)

    if VISUALIZE_AVAILABLE:
        경로시각화.학습곡선_시각화(이력)
        경로시각화.최종경로_시각화(환경, 최적경로)

    # FreeCAD 시뮬레이션
    FreeCAD_경로_시뮬레이션(최적경로)

    print("\n[정보] 강화학습 경로 설계 데모가 완료되었습니다.")


if __name__ == "__main__" or FREECAD_AVAILABLE:
    메인_실행()
