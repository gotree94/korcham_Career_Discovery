"""
28_generative_shape.py - AI-Based Generative Shape Design
==========================================================
AI generates shapes under constraints and iteratively improves them.

- Boundary condition definition
- AI parametric shape proposals
- FreeCAD validation
- Iterative improvement

Created: 2026-07-14
"""

import math
import random
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
# Boundary Condition Definition
# ============================================================================

@dataclass
class BoundaryCondition:
    """Boundary conditions for shape generation"""
    min_volume: float = 1000.0       # mm³
    max_volume: float = 1000000.0    # mm³
    min_height: float = 10.0         # mm
    max_height: float = 500.0        # mm
    min_section: float = 20.0        # mm
    max_section: float = 300.0       # mm
    material_density: float = 7850.0  # kg/m³ (steel)
    max_load: float = 10000.0        # N
    support_points: List[Tuple[float, float, float]] = field(
        default_factory=lambda: [(0, 0, 0)]
    )
    no_go_zones: List[Dict] = field(default_factory=list)

    def volume_valid(self, volume: float) -> bool:
        """Check if volume is within valid range"""
        return self.min_volume <= volume <= self.max_volume

    def height_valid(self, height: float) -> bool:
        """Check if height is within valid range"""
        return self.min_height <= height <= self.max_height

    def section_valid(self, size: float) -> bool:
        """Check if section size is within valid range"""
        return self.min_section <= size <= self.max_section


# ============================================================================
# Parametric Shape Definition
# ============================================================================

@dataclass
class ShapeParametric:
    """Parametric data for the shape to generate"""
    shape_type: str = "box"       # box, cylinder, cone, mixed
    width: float = 50.0
    depth: float = 50.0
    height: float = 50.0
    radius: float = 25.0
    wall_thickness: float = 5.0
    fillet_radius: float = 2.0
    hole_diameter: float = 0.0
    hole_count: int = 0

    def to_dict(self) -> Dict[str, float]:
        return {
            "width": self.width, "depth": self.depth, "height": self.height,
            "radius": self.radius, "wall_thickness": self.wall_thickness,
            "fillet_radius": self.fillet_radius,
        }

    def estimate_volume(self) -> float:
        """Estimate approximate volume"""
        if self.shape_type == "box":
            outer_vol = self.width * self.depth * self.height
            inner_vol = max(0, self.width - 2 * self.wall_thickness) * \
                       max(0, self.depth - 2 * self.wall_thickness) * \
                       max(0, self.height - self.wall_thickness)
            return outer_vol - inner_vol
        elif self.shape_type == "cylinder":
            return math.pi * self.radius ** 2 * self.height
        elif self.shape_type == "cone":
            return (1.0 / 3.0) * math.pi * self.radius ** 2 * self.height
        return self.width * self.depth * self.height


# ============================================================================
# AI Shape Proposal Generator
# ============================================================================

class AIShapeProposer:
    """AI-based shape parametric proposal class"""

    def __init__(self, boundary: BoundaryCondition):
        self.boundary = boundary
        self.proposal_history: List[Dict] = []

    def initial_proposal(self) -> ShapeParametric:
        """Generate initial shape based on boundary conditions"""
        print("[AI] Generating initial shape proposal...")

        # use midpoint values within boundary
        width = (self.boundary.min_section + self.boundary.max_section) / 2
        depth = (self.boundary.min_section + self.boundary.max_section) / 2
        height = (self.boundary.min_height + self.boundary.max_height) / 2

        shape = ShapeParametric(
            shape_type="box",
            width=width,
            depth=depth,
            height=height,
            wall_thickness=5.0,
        )

        print(f"  -> Shape: {shape.shape_type}, Size: {width:.0f}x{depth:.0f}x{height:.0f}")
        return shape

    def improved_proposal(self, current_shape: ShapeParametric, feedback: Dict) -> ShapeParametric:
        """Improve shape based on feedback"""
        print(f"[AI] Improved shape proposal")

        improved = ShapeParametric(
            shape_type=current_shape.shape_type,
            width=current_shape.width,
            depth=current_shape.depth,
            height=current_shape.height,
            radius=current_shape.radius,
            wall_thickness=current_shape.wall_thickness,
            fillet_radius=current_shape.fillet_radius,
        )

        # reduce size if volume exceeds limit
        if feedback.get("volume_exceeded", False):
            scale = 0.85
            improved.width *= scale
            improved.depth *= scale
            improved.height *= scale
            print("  -> Volume exceeded: reducing size (85%)")

        # increase size if volume too low
        if feedback.get("volume_insufficient", False):
            scale = 1.15
            improved.width *= scale
            improved.depth *= scale
            improved.height *= scale
            print("  -> Volume insufficient: increasing size (115%)")

        # reduce height if too tall
        if feedback.get("height_exceeded", False):
            improved.height *= 0.9
            print("  -> Height exceeded: reducing height (90%)")

        # increase wall thickness if too thin
        if feedback.get("wall_thickness_insufficient", False):
            improved.wall_thickness = min(improved.wall_thickness * 1.2, 20.0)
            print("  -> Increasing wall thickness (120%)")

        # apply range limits
        improved.width = max(self.boundary.min_section, min(self.boundary.max_section, improved.width))
        improved.depth = max(self.boundary.min_section, min(self.boundary.max_section, improved.depth))
        improved.height = max(self.boundary.min_height, min(self.boundary.max_height, improved.height))

        return improved

    def random_mutation(self, current_shape: ShapeParametric, mutation_rate: float = 0.1) -> ShapeParametric:
        """Apply random mutation to current shape"""
        mutated = ShapeParametric(
            shape_type=current_shape.shape_type,
            width=current_shape.width * (1 + random.uniform(-mutation_rate, mutation_rate)),
            depth=current_shape.depth * (1 + random.uniform(-mutation_rate, mutation_rate)),
            height=current_shape.height * (1 + random.uniform(-mutation_rate, mutation_rate)),
            wall_thickness=max(2.0, current_shape.wall_thickness * (1 + random.uniform(-mutation_rate/2, mutation_rate/2))),
        )

        # apply range limits
        mutated.width = max(self.boundary.min_section, min(self.boundary.max_section, mutated.width))
        mutated.depth = max(self.boundary.min_section, min(self.boundary.max_section, mutated.depth))
        mutated.height = max(self.boundary.min_height, min(self.boundary.max_height, mutated.height))

        return mutated


# ============================================================================
# FreeCAD Shape Validation
# ============================================================================

class ShapeValidator:
    """Validates shapes in FreeCAD"""

    def __init__(self, boundary: BoundaryCondition):
        self.boundary = boundary

    def geometric_validation(self, shape: ShapeParametric) -> Tuple[bool, List[str]]:
        """Validate geometric properties"""
        problems = []

        volume = shape.estimate_volume()
        if not self.boundary.volume_valid(volume):
            if volume < self.boundary.min_volume:
                problems.append("volume_insufficient")
            else:
                problems.append("volume_exceeded")

        if not self.boundary.height_valid(shape.height):
            problems.append("height_exceeded")

        if not self.boundary.section_valid(shape.width) or not self.boundary.section_valid(shape.depth):
            problems.append("section_size_exceeded")

        if shape.wall_thickness < 1.0:
            problems.append("wall_thickness_insufficient")

        passed = len(problems) == 0
        return passed, problems

    def freecad_model_validation(self, shape: ShapeParametric) -> Tuple[bool, Dict]:
        """Create actual model in FreeCAD for validation"""
        if not FREECAD_AVAILABLE:
            # validate without FreeCAD
            passed, problems = self.geometric_validation(shape)
            return passed, {
                "volume": shape.estimate_volume(),
                "volume_valid": self.boundary.volume_valid(shape.estimate_volume()),
                "height_valid": self.boundary.height_valid(shape.height),
                "problems": problems,
            }

        try:
            doc = FreeCAD.newDocument("validation_model")

            if shape.shape_type == "box":
                model = Part.makeBox(shape.width, shape.depth, shape.height)
            elif shape.shape_type == "cylinder":
                model = Part.makeCylinder(shape.radius, shape.height)
            elif shape.shape_type == "cone":
                model = Part.makeCone(shape.radius, 0, shape.height)
            else:
                model = Part.makeBox(shape.width, shape.depth, shape.height)

            obj = doc.addObject("Part::Feature", "validation_model")
            obj.Shape = model
            doc.recompute()

            # get actual volume from FreeCAD
            actual_volume = model.Volume

            FreeCAD.removeDocument(doc.Name)

            passed, problems = self.geometric_validation(shape)

            return passed, {
                "volume": actual_volume,
                "volume_valid": self.boundary.volume_valid(actual_volume),
                "height_valid": self.boundary.height_valid(shape.height),
                "problems": problems,
            }

        except Exception as e:
            print(f"[ERROR] FreeCAD validation failed: {e}")
            return False, {"error": str(e), "problems": ["FreeCAD validation failed"]}


# ============================================================================
# Iterative Improvement Loop
# ============================================================================

class ShapeGenerationEngine:
    """AI-based iterative shape generation and improvement engine"""

    def __init__(self, boundary: BoundaryCondition, max_iterations: int = 20):
        self.boundary = boundary
        self.max_iterations = max_iterations
        self.proposer = AIShapeProposer(boundary)
        self.validator = ShapeValidator(boundary)
        self.history: List[Dict] = []

    def generate_and_improve(self) -> Tuple[ShapeParametric, List[Dict]]:
        """Generate shape and iteratively improve it"""
        print("\n" + "=" * 60)
        print("  AI-Based Shape Generation Started")
        print("=" * 60)

        # initial proposal
        current_shape = self.proposer.initial_proposal()
        best_shape = current_shape
        best_volume = current_shape.estimate_volume()
        best_score = abs(best_volume - 50000)  # target volume 50000mm³

        for iteration in range(1, self.max_iterations + 1):
            print(f"\n  [Iteration {iteration}/{self.max_iterations}]")

            # validate
            passed, val_result = self.validator.freecad_model_validation(current_shape)

            current_volume = val_result.get("volume", current_shape.estimate_volume())
            problems = val_result.get("problems", [])

            # score calculation (distance from target volume)
            score = abs(current_volume - 50000)
            print(f"    Volume: {current_volume:.0f}mm³, Score: {score:.0f}, Problems: {len(problems)}")

            # update best
            if score < best_score:
                best_score = score
                best_shape = current_shape
                print(f"    -> Best updated!")

            # record history
            self.history.append({
                "iteration": iteration,
                "volume": current_volume,
                "score": score,
                "passed": passed,
                "problems": problems,
            })

            # check convergence
            if score < 100:
                print("  [Converged] Target volume reached.")
                break

            # generate feedback
            feedback = {}
            if "volume_exceeded" in problems:
                feedback["volume_exceeded"] = True
            if "volume_insufficient" in problems:
                feedback["volume_insufficient"] = True
            if "height_exceeded" in problems:
                feedback["height_exceeded"] = True
            if "wall_thickness_insufficient" in problems:
                feedback["wall_thickness_insufficient"] = True

            # improve or mutate
            if iteration % 3 == 0:
                # every 3rd iteration: random mutation for exploration diversity
                current_shape = self.proposer.random_mutation(best_shape, mutation_rate=0.15)
                print("    -> Random mutation applied")
            else:
                current_shape = self.proposer.improved_proposal(current_shape, feedback)

        print("\n" + "=" * 60)
        print("  Shape Generation Complete")
        print(f"  Best shape: {best_shape.shape_type}")
        print(f"  Size: {best_shape.width:.1f} x {best_shape.depth:.1f} x {best_shape.height:.1f}")
        print(f"  Estimated volume: {best_shape.estimate_volume():.0f} mm³")
        print("=" * 60)

        return best_shape, self.history


# ============================================================================
# FreeCAD Final Model Generation
# ============================================================================

def freecad_final_model(shape: ShapeParametric, model_name: str = "AI_shape"):
    """Generate final shape in FreeCAD"""
    if not FREECAD_AVAILABLE:
        print("[INFO] Cannot generate final model outside FreeCAD.")
        print(f"  Shape: {shape.shape_type}, Width: {shape.width:.1f}, "
              f"Depth: {shape.depth:.1f}, Height: {shape.height:.1f}")
        return

    try:
        doc = FreeCAD.newDocument(model_name)

        if shape.shape_type == "box":
            model = Part.makeBox(shape.width, shape.depth, shape.height)
        elif shape.shape_type == "cylinder":
            model = Part.makeCylinder(shape.radius, shape.height)
        elif shape.shape_type == "cone":
            model = Part.makeCone(shape.radius, 0, shape.height)
        else:
            model = Part.makeBox(shape.width, shape.depth, shape.height)

        obj = doc.addObject("Part::Feature", model_name)
        obj.Shape = model
        doc.recompute()

        print(f"[DONE] FreeCAD model '{model_name}' created successfully")
        print(f"  Volume: {model.Volume:.1f} mm³")

    except Exception as e:
        print(f"[ERROR] Final model generation failed: {e}")


# ============================================================================
# Main Execution
# ============================================================================

def main():
    """Main execution function"""
    print("=" * 60)
    print("  28. AI-Based Generative Shape Design")
    print("  AI Generative Design - Shape Generation Demo")
    print("=" * 60)

    random.seed(42)

    # set boundary conditions
    boundary = BoundaryCondition(
        min_volume=5000,
        max_volume=500000,
        min_height=20,
        max_height=300,
        min_section=30,
        max_section=250,
    )

    print("\n  Boundary Conditions:")
    print(f"    Volume range: {boundary.min_volume} ~ {boundary.max_volume} mm³")
    print(f"    Height range: {boundary.min_height} ~ {boundary.max_height} mm")
    print(f"    Section range: {boundary.min_section} ~ {boundary.max_section} mm")

    # generate and improve shape
    engine = ShapeGenerationEngine(boundary, max_iterations=20)
    final_shape, history = engine.generate_and_improve()

    # FreeCAD final model
    freecad_final_model(final_shape, "AI_generated_shape")

    # history summary
    print("\n  Iteration History Summary:")
    print(f"  {'Iter':>4} {'Volume':>12} {'Score':>10} {'Status':>6}")
    print(f"  {'-' * 36}")
    for record in history:
        status = "OK" if record['passed'] else "FAIL"
        print(f"  {record['iteration']:>4} {record['volume']:>12.0f} {record['score']:>10.0f} {status:>6}")

    print("\n[INFO] AI shape generation demo completed.")


if __name__ == "__main__" or FREECAD_AVAILABLE:
    main()
