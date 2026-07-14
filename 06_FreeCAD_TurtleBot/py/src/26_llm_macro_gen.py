"""
26_llm_macro_gen.py - LLM으로 FreeCAD 매크로 생성
===================================================
AI가 FreeCAD 매크로 코드를 생성하고 실행하는 파이프라인.

- LLM에게 자연어 설계 요구사항 전달
- 생성된 Python 코드 추출
- 코드 안전성 검증 (import/freeCAD 관련 코드만 허용)
- FreeCAD에서 동적 실행
- 여러 설계 요청 예시

작성일: 2026-07-14
"""

import sys
import re
import textwrap
from typing import Optional, Dict, List, Tuple

# FreeCAD 환경 확인
FREECAD_AVAILABLE = False
try:
    import FreeCAD
    import Part
    from FreeCAD import Base
    FREECAD_AVAILABLE = True
except ImportError:
    print("[정보] FreeCAD 모듈을 사용할 수 없습니다. 독립 모드로 실행됩니다.")

# LLM 의존성 확인 (선택사항)
LLM_AVAILABLE = False
try:
    import openai
    LLM_AVAILABLE = True
    print("[정보] OpenAI 라이브러리가 감지되었습니다.")
except ImportError:
    print("[정보] OpenAI 라이브러리가 없습니다. 오프라인 시뮬레이션 모드로 동작합니다.")

# ============================================================================
# 코드 안전성 검증기
# ============================================================================

class 매크로안전검증기:
    """LLM이 생성한 코드의 안전성을 검증하는 클래스"""

    # 허용된 import 모듈 목록
    허용_import = {
        "FreeCAD", "Part", "MathUtils", "Base",
        "FreeCADGui", "Sketcher", "Design",
        "Spreadsheet", "TechDraw",
        "PartDesign", "Fem", "Mesh",
    }

    # 금지된 키워드 목록
    금지_키워드 = [
        "os.system", "subprocess", "shutil.rmtree",
        "eval(", "exec(", "__import__",
        "open(", "socket", "urllib",
        "import os", "import subprocess", "import socket",
        "os.remove", "os.unlink", "os.rmdir",
    ]

    # 코드에서 허용되는 FreeCAD 관련 함수 패턴
    허용_패턴 = [
        r"FreeCAD\.",
        r"Part\.",
        r"App\.",
        r"Gui\.",
        r"doc\.",
        r"obj\.",
        r"Box|Cylinder|Sphere|Cone|Torus",
        r"makeBox|makeCylinder|makeSphere",
    ]

    def __init__(self):
        self.검증_결과 = []

    def 코드_검증(self, 코드: str) -> Tuple[bool, List[str]]:
        """생성된 코드의 안전성을 검증합니다."""
        self.검증_결과 = []
        검증통과 = True

        # 1단계: 금지된 키워드 검사
        for 키워드 in self.금지_키워드:
            if 키워드 in 코드:
                self.검증_결과.append(f"[차단] 금지된 키워드 발견: {키워드}")
                검증통과 = False

        # 2단계: import 구문 검증
        import_줄 = [줄 for 줄 in 코드.split("\n") if 줄.strip().startswith("import ")]
        for 줄 in import_줄:
            모듈명 = 줄.strip().replace("import ", "").replace("from ", "").split()[0]
            if 모듈명 not in self.허용_import and not 모듈명.startswith("FreeCAD"):
                self.검증_결과.append(f"[차단] 허용되지 않은 import: {줄.strip()}")
                검증통과 = False

        # 3단계: 코드 길이 검증 (비정상적으로 긴 코드 차단)
        if len(코드) > 50000:
            self.검증_결과.append("[차단] 코드가 너무 깁니다 (50,000자 초과)")
            검증통과 = False

        # 4단계: 재귀/무한루프 패턴 검사
        if "while True" in 코드 and "break" not in 코드:
            self.검증_결과.append("[경고] 무한 루프 가능성 감지")
            검증통과 = False

        if 검증통과:
            self.검증_결과.append("[통과] 코드 안전성 검증 완료")

        return 검증통과, self.검증_결과

    def 보고서_생성(self) -> str:
        """검증 결과 보고서를 생성합니다."""
        줄 = ["=" * 50, "코드 안전성 검증 보고서", "=" * 50]
        줄.extend(self.검증_결과)
        줄.append("=" * 50)
        return "\n".join(줄)


# ============================================================================
# LLM 기반 매크로 생성기
# ============================================================================

class LLM매크로생성기:
    """LLM을 이용하여 FreeCAD 매크로 코드를 생성하는 클래스"""

    # FreeCAD 매크로용 시스템 프롬프트
    시스템_프롬프트 = textwrap.dedent("""
    당신은 FreeCAD Python 매크로 전문가입니다.
    사용자의 자연어 설계 요구사항을 받아 FreeCAD 매크로 코드를 생성합니다.

    규칙:
    1. 반드시 `import FreeCAD`와 `import Part`를 포함하세요.
    2. 도형은 Part 모듈의 메서드를 사용하세요.
    3. 생성된 도형은 FreeCAD.activeDocument().addObject()로 추가하세요.
    4. 코드는 실행 가능한 Python 문법이어야 합니다.
    5. 주석은 한국어로 작성하세요.
    6. 불필요한 외부 라이브러리를 import하지 마세요.
    7. 모든 코드는 FreeCAD 매크로 환경에서 실행 가능해야 합니다.

    응답 형식:
    ```python
    # FreeCAD 매크로 코드
    ```
    """).strip()

    # 사전 정의된 설계 요청 템플릿
    설계_템플릿: Dict[str, str] = {
        "상자": "크기 100x60x40mm의 상자를 만들어줘",
        "기둥": "높이 150mm, 지름 30mm의 원기둥을 만들어줘",
        "구멍": "100x100x20mm 상자 중앙에 지름 20mm 구멍을 뚫어줘",
        "브래킷": "직각 브래킷을 만들어줘. 밑변 80mm, 세로 60mm, 두께 10mm",
        "헬리컬": "나선형 구조를 만들어줘. 높이 100mm, 반지름 30mm",
        "기어": "기어 형태를 만들어줘. 톱니 수 20, 모듈 2",
    }

    def __init__(self, api_key: Optional[str] = None, 모델: str = "gpt-4"):
        self.api_key = api_key
        self.모델 = 모델
        self.검증기 = 매크로안전검증기()
        self.생성_이력: List[Dict] = []

        if LLM_AVAILABLE and api_key:
            self.클라이언트 = openai.OpenAI(api_key=api_key)
        else:
            self.클라이언트 = None

    def 자연어_요구사항_처리(self, 요구사항: str) -> str:
        """자연어 설계 요구사항을 FreeCAD 매크로 코드로 변환합니다."""
        print(f"\n[요청] 설계 요구사항: {요구사항}")

        # 템플릿 매칭 시도
        for 키, 값 in self.설계_템플릿.items():
            if 키 in 요구사항:
                print(f"[정보] 템플릿 '{키}' 매칭됨")
                return self._템플릿_기반_생성(요구사항)

        # LLM 사용 가능한 경우
        if self.클라이언트:
            return self._LLM_기반_생성(요구사항)

        # 오프라인 폴백: 규칙 기반 생성
        return self._규칙_기반_생성(요구사항)

    def _LLM_기반_생성(self, 요구사항: str) -> str:
        """LLM API를 사용하여 코드를 생성합니다."""
        print("[정보] LLM API를 호출합니다...")

        try:
            응답 = self.클라이언트.chat.completions.create(
                model=self.모델,
                messages=[
                    {"role": "system", "content": self.시스템_프롬프트},
                    {"role": "user", "content": f"FreeCAD 매크로를 만들어주세요: {요구사항}"},
                ],
                temperature=0.3,
                max_tokens=2000,
            )

            생성코드 = 응답.choices[0].message.content

            # 코드 블록 추출
            코드 = self._코드_추출(생성코드)
            print("[정보] LLM으로부터 코드를 생성했습니다.")
            return 코드

        except Exception as e:
            print(f"[오류] LLM API 호출 실패: {e}")
            print("[정보] 규칙 기반 폴백으로 전환합니다.")
            return self._규칙_기반_생성(요구사항)

    def _규칙_기반_생성(self, 요구사항: str) -> str:
        """규칙 기반으로 FreeCAD 매크로 코드를 생성합니다 (오프라인)."""
        print("[정보] 규칙 기반 코드 생성 (오프라인 모드)")

        요구사항_소문자 = 요구사항.lower()

        # 상자 생성
        if "상자" in 요구사항 or "box" in 요구사항_소문자:
            return textwrap.dedent("""\
                import FreeCAD
                import Part

                # 상자 생성 규칙 기반 매크로
                doc = FreeCAD.newDocument("상자")

                # 기본 상자 생성
                상자 = Part.makeBox(100, 60, 40)
                obj = doc.addObject("Part::Feature", "상자")
                obj.Shape = 상자

                doc.recompute()
                print("[완료] 상자가 생성되었습니다: 100x60x40mm")
            """)

        # 기둥 생성
        if "기둥" in 요구사항 or "원기둥" in 요구사항 or "cylinder" in 요구사항_소문자:
            return textwrap.dedent("""\
                import FreeCAD
                import Part

                # 원기둥 생성 규칙 기반 매크로
                doc = FreeCAD.newDocument("원기둥")

                # 원기둥 생성: 반지름 15mm, 높이 150mm
                기둥 = Part.makeCylinder(15, 150)
                obj = doc.addObject("Part::Feature", "원기둥")
                obj.Shape = 기둥

                doc.recompute()
                print("[완료] 원기둥이 생성되었습니다: 지름 30mm, 높이 150mm")
            """)

        # 구멍
        if "구멍" in 요구사항 or "hole" in 요구사항_소문자:
            return textwrap.dedent("""\
                import FreeCAD
                import Part

                # 구멍이 뚫린 상자 생성 규칙 기반 매크로
                doc = FreeCAD.newDocument("구멍상자")

                # 기본 상자
                상자 = Part.makeBox(100, 100, 20)
                # 구멍용 실린더
                구멍 = Part.makeCylinder(10, 20)
                구멍.translate(FreeCAD.Base.Vector(50, 50, 0))

                # 불리언 차감으로 구멍 만들기
                결과 = 상자.cut(구멍)

                obj = doc.addObject("Part::Feature", "구멍상자")
                obj.Shape = 결과

                doc.recompute()
                print("[완료] 구멍이 뚫린 상자가 생성되었습니다.")
            """)

        # 브래킷
        if "브래킷" in 요구사항 or "bracket" in 요구사항_소문자:
            return textwrap.dedent("""\
                import FreeCAD
                import Part

                # 직각 브래킷 생성 규칙 기반 매크로
                doc = FreeCAD.newDocument("브래킷")

                # 수평 부분
                수평 = Part.makeBox(80, 60, 10)
                # 수직 부분
                수직 = Part.makeBox(10, 60, 60)
                수직.translate(FreeCAD.Base.Vector(0, 0, 10))

                # 두 부분 합치기
                브래킷 = 수평.fuse(수직)

                obj = doc.addObject("Part::Feature", "브래킷")
                obj.Shape = 브래킷

                doc.recompute()
                print("[완료] 직각 브래킷이 생성되었습니다.")
            """)

        # 기본: 간단한 상자
        return textwrap.dedent("""\
            import FreeCAD
            import Part

            # 기본 매크로 - 100mm 상자
            doc = FreeCAD.newDocument("기본상자")
            상자 = Part.makeBox(100, 100, 100)
            obj = doc.addObject("Part::Feature", "기본상자")
            obj.Shape = 상자
            doc.recompute()
            print("[완료] 기본 상자가 생성되었습니다: 100x100x100mm")
        """)

    def _템플릿_기반_생성(self, 요구사항: str) -> str:
        """사전 정의된 템플릿을 사용하여 코드를 생성합니다."""
        if "상자" in 요구사항:
            return self._규칙_기반_생성("상자")
        elif "기둥" in 요구사항 or "원기둥" in 요구사항:
            return self._규칙_기반_생성("기둥")
        elif "구멍" in 요구사항:
            return self._규칙_기반_생성("구멍")
        elif "브래킷" in 요구사항:
            return self._규칙_기반_생성("브래킷")
        else:
            return self._규칙_기반_생성(요구사항)

    def _코드_추출(self, 텍스트: str) -> str:
        """LLM 응답에서 Python 코드 블록을 추출합니다."""
        # ```python ... ``` 패턴 추출
        패턴 = r"```(?:python)?\s*\n(.*?)```"
        매치 = re.findall(패턴, 텍스트, re.DOTALL)
        if 매치:
            return 매치[0].strip()

        # 코드 블록이 없으면 전체 텍스트에서 import문 이후 부분 추출
        줄들 = 텍스트.split("\n")
        코드_시작 = -1
        for i, 줄 in enumerate(줄들):
            if "import" in 줄 or "FreeCAD" in 줄:
                코드_시작 = i
                break

        if 코드_시작 >= 0:
            return "\n".join(줄들[코드_시작:])

        return 텍스트

    def 코드_실행(self, 코드: str) -> bool:
        """생성된 코드를 안전 검증 후 FreeCAD에서 실행합니다."""
        print("\n[정보] 코드 안전 검증을 시작합니다...")

        # 안전 검증
        통과, 결과 = self.검증기.코드_검증(코드)
        print(self.검증기.보고서_생성())

        if not 통과:
            print("[오류] 안전 검증에 통과하지 못했습니다. 실행이 차단됩니다.")
            return False

        # FreeCAD 환경 확인
        if not FREECAD_AVAILABLE:
            print("[정보] FreeCAD 환경이 아닙니다. 코드 출력만 수행합니다.")
            print("--- 생성된 코드 ---")
            print(코드)
            print("--- 코드 끝 ---")
            return True

        # 실제 실행
        try:
            exec(코드, {"__builtins__": __builtins__})
            print("[완료] 매크로가 성공적으로 실행되었습니다.")
            return True
        except Exception as e:
            print(f"[오류] 코드 실행 실패: {e}")
            return False

    def 전체_파이프라인(self, 요구사항: str) -> Dict:
        """전체 파이프라인: 요구사항 -> 생성 -> 검증 -> 실행"""
        print("\n" + "=" * 60)
        print(f"  FreeCAD 매크로 생성 파이프라인")
        print(f"  요구사항: {요구사항}")
        print("=" * 60)

        # 1단계: 코드 생성
        print("\n[1단계] 코드 생성 중...")
        생성코드 = self.자연어_요구사항_처리(요구사항)

        # 2단계: 안전 검증
        print("\n[2단계] 안전 검증 중...")
        통과, 검증결과 = self.검증기.코드_검증(생성코드)

        # 3단계: 실행
        print("\n[3단계] 코드 실행 중...")
        실행결과 = self.코드_실행(생성코드)

        # 이력 기록
        기록 = {
            "요구사항": 요구사항,
            "생성코드": 생성코드,
            "검증통과": 통과,
            "검증결과": 검증결과,
            "실행결과": 실행결과,
        }
        self.생성_이력.append(기록)

        return 기록


# ============================================================================
# 실행 함수
# ============================================================================

def 메인_실행():
    """메인 실행 함수 - 여러 설계 요청 예시를 시연합니다."""
    print("=" * 60)
    print("  26. LLM으로 FreeCAD 매크로 생성")
    print("  AI 기반 생성 설계 파이프라인 데모")
    print("=" * 60)

    # 생성기 초기화 (API 키 없이 오프라인 모드)
    생성기 = LLM매크로생성기(api_key=None)

    # 여러 설계 요청 예시
    설계_요청사항_목록 = [
        "크기 100x60x40mm의 상자를 만들어줘",
        "높이 150mm, 지름 30mm의 원기둥을 만들어줘",
        "100x100x20mm 상자 중앙에 지름 20mm 구멍을 뚫어줘",
        "직각 브래킷을 만들어줘. 밑변 80mm, 세로 60mm, 두께 10mm",
        "알 수 없는 요청 테스트 - 기본 상자 생성",
    ]

    for i, 요청 in enumerate(설계_요청사항_목록, 1):
        print(f"\n{'#' * 60}")
        print(f"  예시 {i}/{len(설계_요청사항_목록)}")
        print(f"{'#' * 60}")

        결과 = 생성기.전체_파이프라인(요청)

        print(f"\n  -> 검증: {'통과' if 결과['검증통과'] else '실패'}")
        print(f"  -> 실행: {'성공' if 결과['실행결과'] else '실패'}")

    # 전체 이력 요약
    print("\n\n" + "=" * 60)
    print("  전체 생성 이력 요약")
    print("=" * 60)
    for i, 기록 in enumerate(생성기.생성_이력, 1):
        상태 = "OK" if 기록['검증통과'] and 기록['실행결과'] else "FAIL"
        print(f"  {i}. [{상태}] {기록['요구사항'][:40]}...")

    print("\n[정보] LLM 매크로 생성 데모가 완료되었습니다.")


# FreeCAD 매크로 실행 진입점
if __name__ == "__main__" or FREECAD_AVAILABLE:
    메인_실행()
