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

class MacroSafetyChecker:
    """LLM이 생성한 코드의 안전성을 검증하는 클래스"""

    # 허용된 import 모듈 목록
    allowed_imports = {
        "FreeCAD", "Part", "MathUtils", "Base",
        "FreeCADGui", "Sketcher", "Design",
        "Spreadsheet", "TechDraw",
        "PartDesign", "Fem", "Mesh",
    }

    # 금지된 키워드 목록
    forbidden_keywords = [
        "os.system", "subprocess", "shutil.rmtree",
        "eval(", "exec(", "__import__",
        "open(", "socket", "urllib",
        "import os", "import subprocess", "import socket",
        "os.remove", "os.unlink", "os.rmdir",
    ]

    # 코드에서 허용되는 FreeCAD 관련 함수 패턴
    allowed_patterns = [
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
        self.check_results = []

    def check_code(self, code: str) -> Tuple[bool, List[str]]:
        """생성된 코드의 안전성을 검증합니다."""
        self.check_results = []
        passed = True

        # 1단계: 금지된 키워드 검사
        for keyword in self.forbidden_keywords:
            if keyword in code:
                self.check_results.append(f"[차단] 금지된 키워드 발견: {keyword}")
                passed = False

        # 2단계: import 구문 검증
        import_lines = [line for line in code.split("\n") if line.strip().startswith("import ")]
        for line in import_lines:
            module_name = line.strip().replace("import ", "").replace("from ", "").split()[0]
            if module_name not in self.allowed_imports and not module_name.startswith("FreeCAD"):
                self.check_results.append(f"[차단] 허용되지 않은 import: {line.strip()}")
                passed = False

        # 3단계: 코드 길이 검증 (비정상적으로 긴 코드 차단)
        if len(code) > 50000:
            self.check_results.append("[차단] 코드가 너무 깁니다 (50,000자 초과)")
            passed = False

        # 4단계: 재귀/무한루프 패턴 검사
        if "while True" in code and "break" not in code:
            self.check_results.append("[경고] 무한 루프 가능성 감지")
            passed = False

        if passed:
            self.check_results.append("[통과] 코드 안전성 검증 완료")

        return passed, self.check_results

    def generate_report(self) -> str:
        """검증 결과 보고서를 생성합니다."""
        lines = ["=" * 50, "코드 안전성 검증 보고서", "=" * 50]
        lines.extend(self.check_results)
        lines.append("=" * 50)
        return "\n".join(lines)


# ============================================================================
# LLM 기반 매크로 생성기
# ============================================================================

class LLMMacroGenerator:
    """LLM을 이용하여 FreeCAD 매크로 코드를 생성하는 클래스"""

    # FreeCAD 매크로용 시스템 프롬프트
    system_prompt = textwrap.dedent("""
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
    design_templates: Dict[str, str] = {
        "상자": "크기 100x60x40mm의 상자를 만들어줘",
        "기둥": "높이 150mm, 지름 30mm의 원기둥을 만들어줘",
        "구멍": "100x100x20mm 상자 중앙에 지름 20mm 구멍을 뚫어줘",
        "브래킷": "직각 브래킷을 만들어줘. 밑변 80mm, 세로 60mm, 두께 10mm",
        "헬리컬": "나선형 구조를 만들어줘. 높이 100mm, 반지름 30mm",
        "기어": "기어 형태를 만들어줘. 톱니 수 20, 모듈 2",
    }

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        self.api_key = api_key
        self.model = model
        self.checker = MacroSafetyChecker()
        self.generation_history: List[Dict] = []

        if LLM_AVAILABLE and api_key:
            self.client = openai.OpenAI(api_key=api_key)
        else:
            self.client = None

    def process_natural_language(self, requirements: str) -> str:
        """자연어 설계 요구사항을 FreeCAD 매크로 코드로 변환합니다."""
        print(f"\n[요청] 설계 요구사항: {requirements}")

        # 템플릿 매칭 시도
        for key, val in self.design_templates.items():
            if key in requirements:
                print(f"[정보] 템플릿 '{key}' 매칭됨")
                return self._template_based_generation(requirements)

        # LLM 사용 가능한 경우
        if self.client:
            return self._llm_based_generation(requirements)

        # 오프라인 폴백: 규칙 기반 생성
        return self._rule_based_generation(requirements)

    def _llm_based_generation(self, requirements: str) -> str:
        """LLM API를 사용하여 코드를 생성합니다."""
        print("[정보] LLM API를 호출합니다...")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"FreeCAD 매크로를 만들어주세요: {requirements}"},
                ],
                temperature=0.3,
                max_tokens=2000,
            )

            raw_code = response.choices[0].message.content

            # 코드 블록 추출
            code = self._extract_code(raw_code)
            print("[정보] LLM으로부터 코드를 생성했습니다.")
            return code

        except Exception as e:
            print(f"[오류] LLM API 호출 실패: {e}")
            print("[정보] 규칙 기반 폴백으로 전환합니다.")
            return self._rule_based_generation(requirements)

    def _rule_based_generation(self, requirements: str) -> str:
        """규칙 기반으로 FreeCAD 매크로 코드를 생성합니다 (오프라인)."""
        print("[정보] 규칙 기반 코드 생성 (오프라인 모드)")

        req_lower = requirements.lower()

        # 상자 생성
        if "상자" in requirements or "box" in req_lower:
            return textwrap.dedent("""\
                import FreeCAD
                import Part

                # 상자 생성 규칙 기반 매크로
                doc = FreeCAD.newDocument("상자")

                # 기본 상자 생성
                box = Part.makeBox(100, 60, 40)
                obj = doc.addObject("Part::Feature", "상자")
                obj.Shape = box

                doc.recompute()
                print("[완료] 상자가 생성되었습니다: 100x60x40mm")
            """)

        # 기둥 생성
        if "기둥" in requirements or "원기둥" in requirements or "cylinder" in req_lower:
            return textwrap.dedent("""\
                import FreeCAD
                import Part

                # 원기둥 생성 규칙 기반 매크로
                doc = FreeCAD.newDocument("원기둥")

                # 원기둥 생성: 반지름 15mm, 높이 150mm
                pillar = Part.makeCylinder(15, 150)
                obj = doc.addObject("Part::Feature", "원기둥")
                obj.Shape = pillar

                doc.recompute()
                print("[완료] 원기둥이 생성되었습니다: 지름 30mm, 높이 150mm")
            """)

        # 구멍
        if "구멍" in requirements or "hole" in req_lower:
            return textwrap.dedent("""\
                import FreeCAD
                import Part

                # 구멍이 뚫린 상자 생성 규칙 기반 매크로
                doc = FreeCAD.newDocument("구멍상자")

                # 기본 상자
                box = Part.makeBox(100, 100, 20)
                # 구멍용 실린더
                hole = Part.makeCylinder(10, 20)
                hole.translate(FreeCAD.Base.Vector(50, 50, 0))

                # 불리언 차감으로 구멍 만들기
                result = box.cut(hole)

                obj = doc.addObject("Part::Feature", "구멍상자")
                obj.Shape = result

                doc.recompute()
                print("[완료] 구멍이 뚫린 상자가 생성되었습니다.")
            """)

        # 브래킷
        if "브래킷" in requirements or "bracket" in req_lower:
            return textwrap.dedent("""\
                import FreeCAD
                import Part

                # 직각 브래킷 생성 규칙 기반 매크로
                doc = FreeCAD.newDocument("브래킷")

                # 수평 부분
                horizontal = Part.makeBox(80, 60, 10)
                # 수직 부분
                vertical = Part.makeBox(10, 60, 60)
                vertical.translate(FreeCAD.Base.Vector(0, 0, 10))

                # 두 부분 합치기
                bracket = horizontal.fuse(vertical)

                obj = doc.addObject("Part::Feature", "브래킷")
                obj.Shape = bracket

                doc.recompute()
                print("[완료] 직각 브래킷이 생성되었습니다.")
            """)

        # 기본: 간단한 상자
        return textwrap.dedent("""\
            import FreeCAD
            import Part

            # 기본 매크로 - 100mm 상자
            doc = FreeCAD.newDocument("기본상자")
            box = Part.makeBox(100, 100, 100)
            obj = doc.addObject("Part::Feature", "기본상자")
            obj.Shape = box
            doc.recompute()
            print("[완료] 기본 상자가 생성되었습니다: 100x100x100mm")
        """)

    def _template_based_generation(self, requirements: str) -> str:
        """사전 정의된 템플릿을 사용하여 코드를 생성합니다."""
        if "상자" in requirements:
            return self._rule_based_generation("상자")
        elif "기둥" in requirements or "원기둥" in requirements:
            return self._rule_based_generation("기둥")
        elif "구멍" in requirements:
            return self._rule_based_generation("구멍")
        elif "브래킷" in requirements:
            return self._rule_based_generation("브래킷")
        else:
            return self._rule_based_generation(requirements)

    def _extract_code(self, text: str) -> str:
        """LLM 응답에서 Python 코드 블록을 추출합니다."""
        # ```python ... ``` 패턴 추출
        pattern = r"```(?:python)?\s*\n(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)
        if matches:
            return matches[0].strip()

        # 코드 블록이 없으면 전체 텍스트에서 import문 이후 부분 추출
        lines = text.split("\n")
        code_start = -1
        for i, line in enumerate(lines):
            if "import" in line or "FreeCAD" in line:
                code_start = i
                break

        if code_start >= 0:
            return "\n".join(lines[code_start:])

        return text

    def execute_code(self, code: str) -> bool:
        """생성된 코드를 안전 검증 후 FreeCAD에서 실행합니다."""
        print("\n[정보] 코드 안전 검증을 시작합니다...")

        # 안전 검증
        passed, results = self.checker.check_code(code)
        print(self.checker.generate_report())

        if not passed:
            print("[오류] 안전 검증에 통과하지 못했습니다. 실행이 차단됩니다.")
            return False

        # FreeCAD 환경 확인
        if not FREECAD_AVAILABLE:
            print("[정보] FreeCAD 환경이 아닙니다. 코드 출력만 수행합니다.")
            print("--- 생성된 코드 ---")
            print(code)
            print("--- 코드 끝 ---")
            return True

        # 실제 실행
        try:
            exec(code, {"__builtins__": __builtins__})
            print("[완료] 매크로가 성공적으로 실행되었습니다.")
            return True
        except Exception as e:
            print(f"[오류] 코드 실행 실패: {e}")
            return False

    def full_pipeline(self, requirements: str) -> Dict:
        """전체 파이프라인: 요구사항 -> 생성 -> 검증 -> 실행"""
        print("\n" + "=" * 60)
        print(f"  FreeCAD 매크로 생성 파이프라인")
        print(f"  요구사항: {requirements}")
        print("=" * 60)

        # 1단계: 코드 생성
        print("\n[1단계] 코드 생성 중...")
        gen_code = self.process_natural_language(requirements)

        # 2단계: 안전 검증
        print("\n[2단계] 안전 검증 중...")
        passed, check_results = self.checker.check_code(gen_code)

        # 3단계: 실행
        print("\n[3단계] 코드 실행 중...")
        exec_result = self.execute_code(gen_code)

        # 이력 기록
        record = {
            "requirements": requirements,
            "generated_code": gen_code,
            "check_passed": passed,
            "check_results": check_results,
            "exec_result": exec_result,
        }
        self.generation_history.append(record)

        return record


# ============================================================================
# 실행 함수
# ============================================================================

def main():
    """메인 실행 함수 - 여러 설계 요청 예시를 시연합니다."""
    print("=" * 60)
    print("  26. LLM으로 FreeCAD 매크로 생성")
    print("  AI 기반 생성 설계 파이프라인 데모")
    print("=" * 60)

    # 생성기 초기화 (API 키 없이 오프라인 모드)
    generator = LLMMacroGenerator(api_key=None)

    # 여러 설계 요청 예시
    design_request_list = [
        "크기 100x60x40mm의 상자를 만들어줘",
        "높이 150mm, 지름 30mm의 원기둥을 만들어줘",
        "100x100x20mm 상자 중앙에 지름 20mm 구멍을 뚫어줘",
        "직각 브래킷을 만들어줘. 밑변 80mm, 세로 60mm, 두께 10mm",
        "알 수 없는 요청 테스트 - 기본 상자 생성",
    ]

    for i, request in enumerate(design_request_list, 1):
        print(f"\n{'#' * 60}")
        print(f"  예시 {i}/{len(design_request_list)}")
        print(f"{'#' * 60}")

        record = generator.full_pipeline(request)

        print(f"\n  -> 검증: {'통과' if record['check_passed'] else '실패'}")
        print(f"  -> 실행: {'성공' if record['exec_result'] else '실패'}")

    # 전체 이력 요약
    print("\n\n" + "=" * 60)
    print("  전체 생성 이력 요약")
    print("=" * 60)
    for i, record in enumerate(generator.generation_history, 1):
        status = "OK" if record['check_passed'] and record['exec_result'] else "FAIL"
        print(f"  {i}. [{status}] {record['requirements'][:40]}...")

    print("\n[정보] LLM 매크로 생성 데모가 완료되었습니다.")


# FreeCAD 매크로 실행 진입점
if __name__ == "__main__" or FREECAD_AVAILABLE:
    main()
