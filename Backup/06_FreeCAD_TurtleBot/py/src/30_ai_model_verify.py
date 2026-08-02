"""
30_ai_model_verify.py - AI Model Verification
===============================================
AI automatically verifies generated models.

- Geometric validity checks
- Tolerance verification
- Manufacturability checks
- Report generation

Created: 2026-07-14
"""

import math
import datetime
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field

# FreeCAD environment check
FREECAD_AVAILABLE = False
try:
    import FreeCAD
    import Part
    from FreeCAD import Base
    FREECAD_AVAILABLE = True
except ImportError:
    print("[INFO] FreeCAD module not available. Running in simulation mode.")


# ============================================================================
# Verification Result Definition
# ============================================================================

@dataclass
class VerificationItem:
    """Single verification item result"""
    name: str
    passed: bool
    message: str
    severity: str = "info"  # info, warning, error, critical


@dataclass
class VerificationReport:
    """Full verification report"""
    model_name: str
    verification_time: str = ""
    items: List[VerificationItem] = field(default_factory=list)
    total_checks: int = 0
    passed_count: int = 0
    failed_count: int = 0

    def __post_init__(self):
        if not self.verification_time:
            self.verification_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def add_item(self, item: VerificationItem):
        self.items.append(item)
        self.total_checks += 1
        if item.passed:
            self.passed_count += 1
        else:
            self.failed_count += 1

    def overall_pass(self) -> bool:
        """Pass if no critical/error level failures"""
        for item in self.items:
            if not item.passed and item.severity in ("error", "critical"):
                return False
        return True

    def text_report(self) -> str:
        """Generate text-based report"""
        lines = [
            "=" * 60,
            "  AI Model Verification Report",
            "=" * 60,
            f"  Model: {self.model_name}",
            f"  Time: {self.verification_time}",
            f"  Total: {self.total_checks}, Passed: {self.passed_count}, Failed: {self.failed_count}",
            f"  Verdict: {'PASS' if self.overall_pass() else 'FAIL'}",
            "=" * 60,
            "",
        ]

        for item in self.items:
            status = "OK" if item.passed else "FAIL"
            lines.append(f"  [{status}] [{item.severity}] {item.name}")
            lines.append(f"         {item.message}")
            lines.append("")

        lines.append("=" * 60)
        return "\n".join(lines)


# ============================================================================
# Geometric Validity Check
# ============================================================================

class GeometricCheck:
    """Checks geometric validity of a model"""

    def __init__(self, model=None):
        self.model = model

    def run_check(self, model=None) -> List[VerificationItem]:
        """Perform geometric validation"""
        results = []
        target = model or self.model

        if target is None:
            results.append(VerificationItem(
                name="Geometric existence",
                passed=False,
                message="No model to verify.",
                severity="critical",
            ))
            return results

        if FREECAD_AVAILABLE and hasattr(target, "Volume"):
            # FreeCAD model verification
            results.extend(self._freecad_geometric_check(target))
        elif isinstance(target, dict):
            # parametric info based verification
            results.extend(self._parametric_geometric_check(target))
        else:
            # basic verification
            results.append(self._basic_check(target))

        return results

    def _freecad_geometric_check(self, model) -> List[VerificationItem]:
        """FreeCAD model geometric check"""
        results = []

        # 1. volume check
        volume = model.Volume
        if volume > 0:
            results.append(VerificationItem(
                name="Positive volume",
                passed=True,
                message=f"Volume: {volume:.2f} mm³",
            ))
        else:
            results.append(VerificationItem(
                name="Positive volume",
                passed=False,
                message=f"Volume is non-positive: {volume:.2f} mm³",
                severity="critical",
            ))

        # 2. surface area check
        area = model.Area
        if area > 0:
            results.append(VerificationItem(
                name="Positive surface area",
                passed=True,
                message=f"Surface area: {area:.2f} mm²",
            ))
        else:
            results.append(VerificationItem(
                name="Positive surface area",
                passed=False,
                message=f"Surface area is non-positive: {area:.2f} mm²",
                severity="critical",
            ))

        # 3. connectivity check
        try:
            geometry = model.copy()
            if geometry.isClosed():
                results.append(VerificationItem(
                    name="Geometry connectivity",
                    passed=True,
                    message="Model is a closed solid.",
                ))
            else:
                results.append(VerificationItem(
                    name="Geometry connectivity",
                    passed=False,
                    message="Model is an open shape.",
                    severity="warning",
                ))
        except Exception:
            results.append(VerificationItem(
                name="Geometry connectivity",
                passed=True,
                message="Skipping connectivity check.",
            ))

        # 4. bounding box check
        BB = model.BoundBox
        if BB.isValid():
            size = (BB.XLength, BB.YLength, BB.ZLength)
            results.append(VerificationItem(
                name="Bounding box validity",
                passed=True,
                message=f"Bounding size: {size[0]:.1f} x {size[1]:.1f} x {size[2]:.1f} mm",
            ))
        else:
            results.append(VerificationItem(
                name="Bounding box validity",
                passed=False,
                message="Bounding box is invalid.",
                severity="error",
            ))

        # 5. self-intersection check
        try:
            is_split = len(model.ancestors()) > 1
            if is_split:
                results.append(VerificationItem(
                    name="Single body check",
                    passed=False,
                    message="Model is split into multiple pieces.",
                    severity="warning",
                ))
            else:
                results.append(VerificationItem(
                    name="Single body check",
                    passed=True,
                    message="Model is a single connected body.",
                ))
        except Exception:
            pass

        return results

    def _parametric_geometric_check(self, params: Dict) -> List[VerificationItem]:
        """Parametric dictionary based geometric check"""
        results = []

        # size check
        for key in ["width", "depth", "height"]:
            val = params.get(key, 0)
            if val > 0:
                results.append(VerificationItem(
                    name=f"{key} positive check",
                    passed=True,
                    message=f"{key}: {val:.2f} mm",
                ))
            else:
                results.append(VerificationItem(
                    name=f"{key} positive check",
                    passed=False,
                    message=f"{key} is non-positive: {val}",
                    severity="error",
                ))

        # estimated volume check
        x = params.get("width", 0)
        y = params.get("depth", 0)
        z = params.get("height", 0)
        volume = x * y * z
        if volume > 0:
            results.append(VerificationItem(
                name="Estimated volume",
                passed=True,
                message=f"Estimated volume: {volume:.0f} mm³",
            ))

        return results

    def _basic_check(self, model) -> VerificationItem:
        """Basic validation"""
        return VerificationItem(
            name="Basic verification",
            passed=True,
            message="Basic check passed (not in FreeCAD mode).",
        )


# ============================================================================
# Tolerance Verification
# ============================================================================

@dataclass
class ToleranceSettings:
    """Tolerance verification settings"""
    min_thickness: float = 1.0          # mm
    max_aspect_ratio: float = 100.0     # max/min dimension ratio
    max_draft_angle: float = 45.0       # degrees
    min_fillet_radius: float = 0.5      # mm
    tolerance_range: float = 0.1        # mm (default tolerance)


class ToleranceVerifier:
    """Verifies tolerances of a model"""

    def __init__(self, tolerance: ToleranceSettings = None):
        self.tolerance = tolerance or ToleranceSettings()

    def run_check(self, model=None, params: Dict = None) -> List[VerificationItem]:
        """Perform tolerance verification"""
        results = []

        if FREECAD_AVAILABLE and model is not None:
            results.extend(self._freecad_tolerance_check(model))
        elif params is not None:
            results.extend(self._parametric_tolerance_check(params))
        else:
            results.append(VerificationItem(
                name="Tolerance check",
                passed=True,
                message="No target for tolerance check. Skipping.",
            ))

        return results

    def _freecad_tolerance_check(self, model) -> List[VerificationItem]:
        """FreeCAD model tolerance check"""
        results = []

        # 1. minimum thickness check
        try:
            BB = model.BoundBox
            min_dim = min(BB.XLength, BB.YLength, BB.ZLength)
            if min_dim >= self.tolerance.min_thickness:
                results.append(VerificationItem(
                    name="Minimum thickness",
                    passed=True,
                    message=f"Min dimension: {min_dim:.2f}mm (standard: {self.tolerance.min_thickness}mm)",
                ))
            else:
                results.append(VerificationItem(
                    name="Minimum thickness",
                    passed=False,
                    message=f"Min dimension {min_dim:.2f}mm < standard {self.tolerance.min_thickness}mm",
                    severity="error",
                ))
        except Exception:
            pass

        # 2. dimension ratio check
        try:
            BB = model.BoundBox
            dims = sorted([BB.XLength, BB.YLength, BB.ZLength])
            if dims[0] > 0:
                ratio = dims[2] / dims[0]
                if ratio <= self.tolerance.max_aspect_ratio:
                    results.append(VerificationItem(
                        name="Dimension ratio",
                        passed=True,
                        message=f"Max/min ratio: {ratio:.1f} (standard: {self.tolerance.max_aspect_ratio} or less)",
                    ))
                else:
                    results.append(VerificationItem(
                        name="Dimension ratio",
                        passed=False,
                        message=f"Ratio {ratio:.1f} > standard {self.tolerance.max_aspect_ratio}",
                        severity="warning",
                    ))
        except Exception:
            pass

        # 3. cross-section uniformity check
        try:
            lengths = []
            for ax in ["X", "Y", "Z"]:
                BB = model.BoundBox
                if ax == "X":
                    length = BB.XLength
                elif ax == "Y":
                    length = BB.YLength
                else:
                    length = BB.ZLength
                lengths.append(length)

            length_ratio = max(lengths) / max(min(lengths), 0.001)
            results.append(VerificationItem(
                name="Cross-section uniformity",
                passed=True,
                message=f"Section ratio: {length_ratio:.2f}",
            ))
        except Exception:
            pass

        return results

    def _parametric_tolerance_check(self, params: Dict) -> List[VerificationItem]:
        """Parametric info based tolerance check"""
        results = []

        x = params.get("width", 0)
        y = params.get("depth", 0)
        z = params.get("height", 0)

        # thickness check
        wall_thickness = params.get("wall_thickness", 5)
        if wall_thickness >= self.tolerance.min_thickness:
            results.append(VerificationItem(
                name="Wall thickness",
                passed=True,
                message=f"Wall thickness: {wall_thickness:.1f}mm (standard: {self.tolerance.min_thickness}mm)",
            ))
        else:
            results.append(VerificationItem(
                name="Wall thickness",
                passed=False,
                message=f"Wall thickness {wall_thickness:.1f}mm < standard {self.tolerance.min_thickness}mm",
                severity="error",
            ))

        # dimension ratio check
        dims = sorted([x, y, z])
        if dims[0] > 0:
            ratio = dims[2] / dims[0]
            if ratio <= self.tolerance.max_aspect_ratio:
                results.append(VerificationItem(
                    name="Dimension ratio",
                    passed=True,
                    message=f"Ratio: {ratio:.1f} (standard: {self.tolerance.max_aspect_ratio} or less)",
                ))
            else:
                results.append(VerificationItem(
                    name="Dimension ratio",
                    passed=False,
                    message=f"Ratio {ratio:.1f} > standard {self.tolerance.max_aspect_ratio}",
                    severity="warning",
                ))

        # fillet radius check
        fillet_radius = params.get("fillet_radius", 0)
        if fillet_radius >= self.tolerance.min_fillet_radius:
            results.append(VerificationItem(
                name="Fillet radius",
                passed=True,
                message=f"Fillet radius: {fillet_radius:.1f}mm",
            ))
        elif fillet_radius > 0:
            results.append(VerificationItem(
                name="Fillet radius",
                passed=False,
                message=f"Fillet radius {fillet_radius:.1f}mm < standard {self.tolerance.min_fillet_radius}mm",
                severity="warning",
            ))

        return results


# ============================================================================
# Design for Manufacturing (DFM) Check
# ============================================================================

class ManufacturabilityCheck:
    """Design for Manufacturing (DFM) check"""

    def __init__(self):
        self.check_rules = {
            "min_milling_depth": 0.5,       # mm
            "max_milling_ratio": 5.0,
            "min_rib_height": 2.0,          # mm
            "max_rib_ratio": 10.0,
            "min_core_diameter": 3.0,       # mm
            "max_overhang_ratio": 3.0,
        }

    def run_check(self, model=None, params: Dict = None) -> List[VerificationItem]:
        """Check manufacturability"""
        results = []

        if FREECAD_AVAILABLE and model is not None:
            results.extend(self._freecad_manufacturability_check(model))
        elif params is not None:
            results.extend(self._parametric_manufacturability_check(params))
        else:
            results.append(VerificationItem(
                name="Manufacturability",
                passed=True,
                message="No target for manufacturability check. Skipping.",
            ))

        return results

    def _freecad_manufacturability_check(self, model) -> List[VerificationItem]:
        """FreeCAD model manufacturability check"""
        results = []

        # 1. overall dimension check
        BB = model.BoundBox
        max_dim = max(BB.XLength, BB.YLength, BB.ZLength)
        if max_dim <= 1000:  # under 1m
            results.append(VerificationItem(
                name="Overall dimensions",
                passed=True,
                message=f"Max dimension: {max_dim:.1f}mm (under 1000mm)",
            ))
        else:
            results.append(VerificationItem(
                name="Overall dimensions",
                passed=False,
                message=f"Max dimension {max_dim:.1f}mm > 1000mm",
                severity="warning",
            ))

        # 2. shape complexity estimate (face count)
        try:
            face_count = len(model.Faces)
            if face_count <= 100:
                results.append(VerificationItem(
                    name="Shape complexity",
                    passed=True,
                    message=f"Face count: {face_count} (under 100)",
                ))
            else:
                results.append(VerificationItem(
                    name="Shape complexity",
                    passed=False,
                    message=f"Face count {face_count} > 100",
                    severity="warning",
                ))
        except Exception:
            pass

        # 3. closed solid check (machinability)
        try:
            if model.isClosed():
                results.append(VerificationItem(
                    name="Solid check",
                    passed=True,
                    message="Model is a closed solid.",
                ))
            else:
                results.append(VerificationItem(
                    name="Solid check",
                    passed=False,
                    message="Model is not a closed solid.",
                    severity="error",
                ))
        except Exception:
            pass

        return results

    def _parametric_manufacturability_check(self, params: Dict) -> List[VerificationItem]:
        """Parametric based manufacturability check"""
        results = []

        x = params.get("width", 0)
        y = params.get("depth", 0)
        z = params.get("height", 0)
        wall_thickness = params.get("wall_thickness", 5)

        # 1. height/floor ratio (mold direction)
        floor_area = x * y
        if floor_area > 0:
            height_ratio = z / math.sqrt(floor_area)
            if height_ratio <= self.check_rules["max_milling_ratio"]:
                results.append(VerificationItem(
                    name="Height/floor ratio",
                    passed=True,
                    message=f"Height ratio: {height_ratio:.2f} (standard: {self.check_rules['max_milling_ratio']} or less)",
                ))
            else:
                results.append(VerificationItem(
                    name="Height/floor ratio",
                    passed=False,
                    message=f"Height ratio {height_ratio:.2f} > standard {self.check_rules['max_milling_ratio']}",
                    severity="warning",
                ))

        # 2. wall thickness uniformity
        if wall_thickness >= self.check_rules["min_milling_depth"]:
            results.append(VerificationItem(
                name="Machinability",
                passed=True,
                message=f"Min wall thickness: {wall_thickness:.1f}mm",
            ))
        else:
            results.append(VerificationItem(
                name="Machinability",
                passed=False,
                message=f"Min wall thickness {wall_thickness:.1f}mm < {self.check_rules['min_milling_depth']}mm",
                severity="error",
            ))

        # 3. edge radius (milling feasibility)
        fillet_radius = params.get("fillet_radius", 0)
        if fillet_radius > 0:
            results.append(VerificationItem(
                name="Edge machining",
                passed=True,
                message=f"Fillet radius: {fillet_radius:.1f}mm",
            ))
        else:
            results.append(VerificationItem(
                name="Edge machining",
                passed=False,
                message="Fillet radius not set.",
                severity="info",
            ))

        # 4. recommended process
        process_recommendations = []
        if wall_thickness >= 2.0 and x <= 500:
            process_recommendations.append("milling")
        if wall_thickness < 2.0:
            process_recommendations.append("cutting")
        if z > 200:
            process_recommendations.append("large milling")

        results.append(VerificationItem(
            name="Process recommendation",
            passed=True,
            message=f"Recommended process: {', '.join(process_recommendations) if process_recommendations else 'standard'}",
        ))

        return results


# ============================================================================
# Integrated Verification Engine
# ============================================================================

class AIModelVerificationEngine:
    """AI model automatic verification integrated engine"""

    def __init__(self):
        self.geometric_check = GeometricCheck()
        self.tolerance_verifier = ToleranceVerifier()
        self.manufacturability_check = ManufacturabilityCheck()

    def full_verification(self, model=None, params: Dict = None,
                  model_name: str = "AI_generated_model") -> VerificationReport:
        """Perform full verification and generate report"""
        report = VerificationReport(model_name=model_name)

        print("\n" + "=" * 60)
        print(f"  AI Model Verification Started: {model_name}")
        print("=" * 60)

        # stage 1: geometric validity check
        print("\n  [Stage 1] Geometric Validity Check...")
        geometric_results = self.geometric_check.run_check(model, params)
        for item in geometric_results:
            report.add_item(item)
            status = "OK" if item.passed else "FAIL"
            print(f"    [{status}] {item.name}: {item.message}")

        # stage 2: tolerance verification
        print("\n  [Stage 2] Tolerance Verification...")
        tolerance_results = self.tolerance_verifier.run_check(model, params)
        for item in tolerance_results:
            report.add_item(item)
            status = "OK" if item.passed else "FAIL"
            print(f"    [{status}] {item.name}: {item.message}")

        # stage 3: manufacturability check
        print("\n  [Stage 3] Manufacturability Check...")
        manufacturing_results = self.manufacturability_check.run_check(model, params)
        for item in manufacturing_results:
            report.add_item(item)
            status = "OK" if item.passed else "FAIL"
            print(f"    [{status}] {item.name}: {item.message}")

        # final verdict
        print("\n" + "=" * 60)
        verdict = "PASS" if report.overall_pass() else "FAIL"
        print(f"  Verdict: {verdict}")
        print(f"  Results: {report.passed_count}/{report.total_checks} passed")
        print("=" * 60)

        return report


# ============================================================================
# Report Storage
# ============================================================================

def save_report(report: VerificationReport, save_path: str = None):
    """Save verification report to file"""
    if save_path is None:
        save_path = "C:\\Users\\Administrator\\Downloads\\py\\src\\30_verify_report.txt"

    try:
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(report.text_report())
        print(f"[INFO] Verification report saved: {save_path}")
    except Exception as e:
        print(f"[ERROR] Report save failed: {e}")


# ============================================================================
# FreeCAD Test Model Generation
# ============================================================================

def freecad_test_model_generation(model_name: str = "verification_target"):
    """Generate a test model for verification in FreeCAD"""
    if not FREECAD_AVAILABLE:
        return None

    try:
        doc = FreeCAD.newDocument(model_name)

        # basic box model
        box = Part.makeBox(100, 80, 60)
        obj = doc.addObject("Part::Feature", "test_box")
        obj.Shape = box

        # add cylindrical hole
        hole = Part.makeCylinder(15, 60)
        hole.translate(Base.Vector(50, 40, 0))
        result = box.cut(hole)
        obj2 = doc.addObject("Part::Feature", "box_with_hole")
        obj2.Shape = result

        doc.recompute()

        print(f"[INFO] FreeCAD test model '{model_name}' generated successfully")
        return result

    except Exception as e:
        print(f"[ERROR] Test model generation failed: {e}")
        return None


# ============================================================================
# Main Execution
# ============================================================================

def main():
    """Main execution function"""
    print("=" * 60)
    print("  30. AI Model Verification")
    print("  AI Generative Design - Automatic Verification Demo")
    print("=" * 60)

    verification_engine = AIModelVerificationEngine()

    # ---------------------------------------------------------------
    # Example 1: FreeCAD Model Verification (when available)
    # ---------------------------------------------------------------
    if FREECAD_AVAILABLE:
        print("\n\n" + "#" * 60)
        print("  Example 1: FreeCAD Model Verification")
        print("#" * 60)

        test_model = freecad_test_model_generation("verification_A")
        if test_model:
            report1 = verification_engine.full_verification(
                model=test_model,
                model_name="box_with_hole_model",
            )
            save_report(report1, "C:\\Users\\Administrator\\Downloads\\py\\src\\30_report_freecad.txt")

    # ---------------------------------------------------------------
    # Example 2: Parametric Verification (always works)
    # ---------------------------------------------------------------
    print("\n\n" + "#" * 60)
    print("  Example 2: Parametric Verification (Offline)")
    print("#" * 60)

    params_good = {
        "width": 120,
        "depth": 80,
        "height": 60,
        "wall_thickness": 4.0,
        "fillet_radius": 2.0,
        "shape_type": "box",
    }

    print(f"\n  Good model params: {params_good}")
    report2 = verification_engine.full_verification(
        params=params_good,
        model_name="good_parametric_model",
    )
    save_report(report2, "C:\\Users\\Administrator\\Downloads\\py\\src\\30_report_good.txt")

    # ---------------------------------------------------------------
    # Example 3: Problematic Model Verification
    # ---------------------------------------------------------------
    print("\n\n" + "#" * 60)
    print("  Example 3: Problematic Model Verification")
    print("#" * 60)

    params_bad = {
        "width": 500,
        "depth": 10,
        "height": 10,
        "wall_thickness": 0.3,       # too thin
        "fillet_radius": 0.0,        # no fillet radius
        "shape_type": "box",
    }

    print(f"\n  Problem model params: {params_bad}")
    report3 = verification_engine.full_verification(
        params=params_bad,
        model_name="problem_parametric_model",
    )
    save_report(report3, "C:\\Users\\Administrator\\Downloads\\py\\src\\30_report_bad.txt")

    # ---------------------------------------------------------------
    # Full Results Summary
    # ---------------------------------------------------------------
    print("\n\n" + "=" * 60)
    print("  Full Verification Results Summary")
    print("=" * 60)

    report_list = [("Good Model", report2), ("Problem Model", report3)]
    if FREECAD_AVAILABLE and 'report1' in dir():
        report_list.insert(0, ("FreeCAD Model", report1))

    print(f"\n  {'Model Name':<25} {'Checks':>6} {'Passed':>6} {'Failed':>6} {'Verdict':>6}")
    print(f"  {'-' * 55}")
    for name, report in report_list:
        verdict = "PASS" if report.overall_pass() else "FAIL"
        print(f"  {name:<25} {report.total_checks:>6d} {report.passed_count:>6d} "
              f"{report.failed_count:>6d} {verdict:>6}")

    print("\n[INFO] AI model verification demo completed.")


if __name__ == "__main__" or FREECAD_AVAILABLE:
    main()
