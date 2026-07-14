# -*- coding: utf-8 -*-
"""
Part 7 - 37: AI 기반 설계 검토 매크로

생성된 3D 모델의 설계 품질을 자동으로 검토하는 AI 기반 분석 도구.
지오메트리 검증, 설계 규칙 검사, 최적화 제안 등을 수행.

사용법: FreeCAD에서 실행하여 설계 검토 결과를 확인.
"""

import sys
import math

try:
    import FreeCAD
    import Part
    from FreeCAD import Base
except ImportError:
    print("[오류] FreeCAD 모듈을 찾을 수 없습니다.")
    sys.exit(1)


# ============================================================
# 모델 특성 분석
# ============================================================

class ModelCharacteristics:
    """
    3D 모델의 특성을 분석하고 저장하는 클래스.
    """

    def __init__(self, shape=None):
        """
        매개변수:
            shape (Part.Shape): 분석할 형태
        """
        self.shape = shape
        self.bounding_box = None
        self.volume = 0.0
        self.area = 0.0
        self.edge_count = 0
        self.face_count = 0
        self.is_watertight = False
        self.analysis_time = 0.0

        if shape is not None:
            self.analyze()

    def analyze(self):
        """형태의 특성을 분석한다."""
        import time
        start = time.time()

        try:
            self.bounding_box = self.shape.BoundBox
            self.volume = self.shape.Volume
            self.area = self.shape.Area
            self.edge_count = len(self.shape.Edges)
            self.face_count = len(self.shape.Faces)
            self.is_watertight = self._check_watertight()
        except Exception as e:
            print(f"[경고] 특성 분석 중 오류: {e}")

        self.analysis_time = time.time() - start

    def _check_watertight(self):
        """형태가 밀폐(watertight)인지 확인한다."""
        try:
            if hasattr(self.shape, "isClosed"):
                return self.shape.isClosed
            if hasattr(self.shape, "Shapes"):
                return len(self.shape.Shapes) > 0
        except Exception:
            pass
        return False

    def get_summary(self):
        """특성 요약을 반환한다."""
        if self.bounding_box is None:
            return "형태가 분석되지 않았습니다."

        return {
            "크기": f"{self.bounding_box.XLength:.1f} x {self.bounding_box.YLength:.1f} x {self.bounding_box.ZLength:.1f} mm",
            "부피": f"{self.volume:.2f} mm³",
            "표면적": f"{self.area:.2f} mm²",
            "엣지 수": self.edge_count,
            "면 수": self.face_count,
            "밀폐 여부": "예" if self.is_watertight else "아니오",
            "분석 시간": f"{self.analysis_time:.3f}초",
        }


# ============================================================
# 설계 규칙 검사기
# ============================================================

class DesignRuleChecker:
    """
    설계 규칙을 검사하는 클래스.
    """

    def __init__(self):
        """기본 규칙 초기화"""
        self.rules = {
            "최소두께": 1.0,       # 최소 벽면 두께 (mm)
            "최대비율": 10.0,      # 최대 폭/높이 비율
            "최소모서리": 0.5,     # 최소 모서리 반지름 (mm)
            "최대부피": 1000000.0, # 최대 부피 (mm³)
            "최소구멍": 0.8,      # 최소 구멍 직경 (mm)
            "최대길이": 500.0,    # 최대 단일 치수 (mm)
        }

    def check_minimum_thickness(self, characteristics):
        """최소 두께를 검사한다."""
        if characteristics.bounding_box is None:
            return [("오류", "바운딩 박스 없음")]

        results = []
        bb = characteristics.bounding_box

        dims = [bb.XLength, bb.YLength, bb.ZLength]
        min_dim = min(dims)

        if min_dim < self.rules["최소두께"]:
            results.append(("오류", f"최소 치수({min_dim:.1f}mm)가 규격 미달입니다."))
        else:
            results.append(("통과", f"최소 치수({min_dim:.1f}mm)가 적합합니다."))

        return results

    def check_aspect_ratio(self, characteristics):
        """폭/높이 비율을 검사한다."""
        if characteristics.bounding_box is None:
            return [("오류", "바운딩 박스 없음")]

        bb = characteristics.bounding_box
        dims = sorted([bb.XLength, bb.YLength, bb.ZLength])

        if dims[0] > 0:
            ratio = dims[2] / dims[0]
            if ratio > self.rules["최대비율"]:
                return [("경고", f"비율({ratio:.1f}:1)이 너무 높습니다. 뒤틀림 위험.")]
            else:
                return [("통과", f"비율({ratio:.1f}:1)이 적합합니다.")]
        return [("경고", "비율 계산 불가")]

    def check_volume_limit(self, characteristics):
        """최대 부피를 검사한다."""
        if characteristics.volume > self.rules["최대부피"]:
            return [("경고", f"부피({characteristics.volume:.0f}mm³)가 매우 큽니다.")]
        return [("통과", f"부피({characteristics.volume:.0f}mm³)가 적합합니다.")]

    def check_dimension_limit(self, characteristics):
        """최대 단일 치수를 검사한다."""
        if characteristics.bounding_box is None:
            return [("오류", "바운딩 박스 없음")]

        bb = characteristics.bounding_box
        max_dim = max(bb.XLength, bb.YLength, bb.ZLength)

        if max_dim > self.rules["최대길이"]:
            return [("경고", f"최대 치수({max_dim:.1f}mm)가 제한을 초과합니다.")]
        return [("통과", f"최대 치수({max_dim:.1f}mm)가 적합합니다.")]

    def check_all(self, characteristics):
        """모든 규칙을 검사한다."""
        results = []
        results.extend(self.check_minimum_thickness(characteristics))
        results.extend(self.check_aspect_ratio(characteristics))
        results.extend(self.check_volume_limit(characteristics))
        results.extend(self.check_dimension_limit(characteristics))
        return results


# ============================================================
# 최적화 제안기
# ============================================================

class OptimizationAdvisor:
    """
    설계 최적화 제안을 생성하는 클래스.
    """

    def __init__(self):
        """기본 제안 규칙 초기화"""
        self.suggestions = []

    def analyze_and_suggest(self, characteristics):
        """특성을 분석하여 최적화 제안을 생성한다."""
        self.suggestions = []

        if characteristics.bounding_box is None:
            return self.suggestions

        bb = characteristics.bounding_box
        volume = characteristics.volume
        area = characteristics.area

        # 부피 대비 표면적 비율 (SA/V)
        if volume > 0:
            sa_v_ratio = area / volume
            if sa_v_ratio > 10:
                self.suggestions.append({
                    "유형": "경량화",
                    "설명": f"SA/V 비율({sa_v_ratio:.2f})이 높습니다. 내부 캐비티 추가를 고려하세요.",
                    "중요도": "보통",
                })

        # 크기 관련 제안
        max_dim = max(bb.XLength, bb.YLength, bb.ZLength)
        if max_dim > 200:
            self.suggestions.append({
                "유형": "제작",
                "설명": f"최대 치수({max_dim:.1f}mm)가 큽니다. 분할 제작을 고려하세요.",
                "중요도": "높음",
            })

        # 밀폐 관련
        if not characteristics.is_watertight:
            self.suggestions.append({
                "유형": "밀폐",
                "설명": "형태가 밀폐되지 않았습니다. 3D 프린팅 시 지지체가 필요할 수 있습니다.",
                "중요도": "보통",
            })

        # 모서리 관련 (엣지 수가 많으면 복잡)
        if characteristics.edge_count > 1000:
            self.suggestions.append({
                "유형": "단순화",
                "설명": f"엣지 수({characteristics.edge_count})가 많습니다. 모델 단순화를 고려하세요.",
                "중요도": "낮음",
            })

        return self.suggestions


# ============================================================
# 설계 검토 보고서 생성
# ============================================================

class DesignReviewReport:
    """
    설계 검토 결과를 보고서로 생성하는 클래스.
    """

    def __init__(self):
        """보고서 초기화"""
        self.characteristics = None
        self.rule_results = []
        self.optimization_suggestions = []
        self.overall_score = 0
        self.overall_grade = ""

    def generate(self, shape):
        """
        형태에 대한 전체 검토 보고서를 생성한다.

        매개변수:
            shape (Part.Shape): 검토할 형태

        반환값:
            dict: 검토 결과
        """
        print("\n" + "=" * 50)
        print("  설계 검토 보고서 생성 중...")
        print("=" * 50)

        # 1. 특성 분석
        print("\n[단계 1] 모델 특성 분석")
        self.characteristics = ModelCharacteristics(shape)

        summary = self.characteristics.get_summary()
        if isinstance(summary, dict):
            for key, value in summary.items():
                print(f"  {key}: {value}")

        # 2. 규칙 검사
        print("\n[단계 2] 설계 규칙 검사")
        checker = DesignRuleChecker()
        self.rule_results = checker.check_all(self.characteristics)

        for status, message in self.rule_results:
            icon = "✓" if status == "통과" else "⚠" if status == "경고" else "✗"
            print(f"  [{icon}] {message}")

        # 3. 최적화 제안
        print("\n[단계 3] 최적화 제안")
        advisor = OptimizationAdvisor()
        self.optimization_suggestions = advisor.analyze_and_suggest(self.characteristics)

        if self.optimization_suggestions:
            for suggestion in self.optimization_suggestions:
                print(f"  [{suggestion['중요도']}] {suggestion['유형']}: {suggestion['설명']}")
        else:
            print("  특별한 제안이 없습니다.")

        # 4. 종합 점수 계산
        print("\n[단계 4] 종합 평가")
        self._calculate_score()

        report = {
            "특성": summary,
            "규칙검사": self.rule_results,
            "최적화제안": self.optimization_suggestions,
            "종합점수": self.overall_score,
            "종합등급": self.overall_grade,
        }

        print(f"\n{'=' * 50}")
        print(f"  종합 점수: {self.overall_score}/100 ({self.overall_grade})")
        print(f"{'=' * 50}")

        return report

    def _calculate_score(self):
        """종합 점수를 계산한다."""
        score = 100

        # 규칙 검사 결과에 따라 감점
        for status, message in self.rule_results:
            if status == "오류":
                score -= 20
            elif status == "경고":
                score -= 10

        # 최적화 제안에 따라 감점
        for suggestion in self.optimization_suggestions:
            if suggestion["중요도"] == "높음":
                score -= 15
            elif suggestion["중요도"] == "보통":
                score -= 5
            else:
                score -= 2

        self.overall_score = max(0, min(100, score))

        if self.overall_score >= 90:
            self.overall_grade = "우수"
        elif self.overall_score >= 70:
            self.overall_grade = "양호"
        elif self.overall_score >= 50:
            self.overall_grade = "보통"
        else:
            self.overall_grade = "개선 필요"


# ============================================================
# FreeCAD 통합 함수
# ============================================================

def add_to_freecad_document(shape, name):
    """
    형태를 FreeCAD 활성 도큐먼트에 추가한다.
    """
    try:
        doc = FreeCAD.ActiveDocument
        if doc is None:
            doc = FreeCAD.newDocument("설계검토")

        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shape
        doc.recompute()
        print(f"[정보] 도큐먼트에 '{name}' 추가 완료")
        return obj
    except Exception as e:
        print(f"[오류] 도큐먼트 추가 실패: {e}")
        return None


def export_stl(shape, filename):
    """
    형태를 STL 파일로 내보낸다.
    """
    try:
        mesh = Part.Mesh()
        if hasattr(shape, "Shapes"):
            for s in shape.Shapes:
                mesh.addMesh(s.tessellate(0.5))
        else:
            mesh.addMesh(shape.tessellate(0.5))
        mesh.write(filename)
        print(f"[정보] STL 파일 저장 완료: {filename}")
        return filename
    except Exception as e:
        print(f"[오류] STL 내보내기 실패: {e}")
        return None


# ============================================================
# 메인 실행 함수
# ============================================================

def run():
    """
    메인 실행 함수.
    예제 모델에 대한 설계 검토를 수행한다.
    """
    print("=" * 60)
    print("  AI 기반 설계 검토 매크로 시작")
    print("=" * 60)

    # 예제 모델 생성
    print("\n[정보] 검토할 예제 모델 생성 중...")

    # 1. 기본 상자
    box = Part.makeBox(100, 80, 30)

    print("\n[검토 1] 기본 상자")
    report1 = DesignReviewReport()
    report1.generate(box)

    # 2. 복잡한 형태
    cylinder = Part.makeCylinder(25, 80)
    sphere = Part.makeSphere(20, Base.Vector(0, 0, 80))
    complex_shape = cylinder.fuse(sphere)

    print("\n[검토 2] 복합 형태")
    report2 = DesignReviewReport()
    report2.generate(complex_shape)

    # 3. 얇은 판
    thin_plate = Part.makeBox(200, 150, 1.5)
    print("\n[검토 3] 얇은 판")
    report3 = DesignReviewReport()
    report3.generate(thin_plate)

    print(f"\n{'=' * 60}")
    print("  AI 기반 설계 검토 완료!")
    print(f"{'=' * 60}")


# 스크립트 직접 실행 시 자동 실행
if __name__ == "__main__":
    run()
else:
    run()
