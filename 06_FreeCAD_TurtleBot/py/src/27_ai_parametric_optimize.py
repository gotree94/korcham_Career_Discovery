"""
27_ai_parametric_optimize.py - AI Parametric Optimization
==========================================================
AI adjusts parametric variables to explore optimal designs.

- Objective function definitions (min volume, max strength)
- Variable range settings
- AI-guided exploration vs random exploration
- Result comparison

Created: 2026-07-14
"""

import math
import random
import time
from typing import List, Dict, Tuple, Callable, Optional

# FreeCAD environment check
FREECAD_AVAILABLE = False
try:
    import FreeCAD
    import Part
    from FreeCAD import Base
    FREECAD_AVAILABLE = True
except ImportError:
    print("[INFO] FreeCAD module not available. Running in simulation mode.")

# AI optimization library check
AI_AVAILABLE = False
try:
    import numpy as np
    AI_AVAILABLE = True
except ImportError:
    print("[INFO] numpy not found. Using basic math functions.")


# ============================================================================
# Parametric Variable Definition
# ============================================================================

class ParametricVariable:
    """Represents a single parametric variable"""

    def __init__(self, name: str, min_val: float, max_val: float, init_val: float = None):
        self.name = name
        self.min_val = min_val
        self.max_val = max_val
        self.init_val = init_val if init_val is not None else (min_val + max_val) / 2

    def clamp(self, val: float) -> float:
        """Clamp value to allowed range"""
        return max(self.min_val, min(self.max_val, val))

    def __repr__(self):
        return f"ParametricVariable('{self.name}', [{self.min_val}, {self.max_val}])"


# ============================================================================
# Objective Function Definitions
# ============================================================================

class ObjectiveFunction:
    """Objective function collection for optimization"""

    @staticmethod
    def min_volume(var_values: Dict[str, float]) -> float:
        """
        Minimize box volume.
        Variables: width(x), depth(y), height(z)
        Constraint: x * y * z >= 10000 (minimum volume requirement)
        """
        x = var_values.get("width", 50)
        y = var_values.get("depth", 50)
        z = var_values.get("height", 50)

        volume = x * y * z
        violation = max(0, 10000 - volume) * 100  # penalty for constraint violation

        return volume + violation

    @staticmethod
    def max_strength(var_values: Dict[str, float]) -> float:
        """
        Maximize structural strength (negative for minimization).
        Simplified stress analysis: based on thickness and radius.
        Variables: thickness(t), radius(r), length(L)
        """
        t = var_values.get("thickness", 5)
        r = var_values.get("radius", 20)
        L = var_values.get("length", 100)

        if L <= 0 or r <= 0 or t <= 0:
            return 1e6  # invalid input penalty

        strength = (t ** 2 * r) / L
        return -strength  # negative for minimization

    @staticmethod
    def combined(var_values: Dict[str, float]) -> float:
        """
        Combined objective: minimize volume + maximize strength.
        Weighted synthesis.
        """
        x = var_values.get("width", 50)
        y = var_values.get("depth", 50)
        z = var_values.get("height", 50)
        t = var_values.get("thickness", 5)

        volume = x * y * z
        est_strength = t * (x + y) * 2  # estimated from wall thickness

        # normalization (approximate)
        norm_volume = volume / 1000000.0
        norm_strength = 1.0 / (est_strength + 0.001)

        return 0.6 * norm_volume + 0.4 * norm_strength


# ============================================================================
# Exploration Algorithms
# ============================================================================

class RandomSearch:
    """Simple random search algorithm"""

    def __init__(self, variables: List[ParametricVariable], objective: Callable):
        self.variables = variables
        self.objective = objective

    def search(self, num_iterations: int = 100) -> Dict:
        """Perform random search"""
        print(f"\n[Random Search] Starting (iterations: {num_iterations})")

        best_value = float("inf")
        best_vars = {}
        history: List[Dict] = []

        for i in range(num_iterations):
            # random variable generation
            var_values = {}
            for var in self.variables:
                var_values[var.name] = random.uniform(var.min_val, var.max_val)

            # evaluate objective
            score = self.objective(var_values)
            history.append({"iteration": i + 1, "vars": var_values.copy(), "score": score})

            # update best
            if score < best_value:
                best_value = score
                best_vars = var_values.copy()

            if (i + 1) % 20 == 0:
                print(f"  Iteration {i+1}/{num_iterations} - current best: {best_value:.4f}")

        return {
            "algorithm": "Random Search",
            "best_value": best_value,
            "best_vars": best_vars,
            "history": history,
            "num_iterations": num_iterations,
        }


class AIRecommendationSearch:
    """AI-guided search algorithm (greedy + directional exploration)"""

    def __init__(self, variables: List[ParametricVariable], objective: Callable):
        self.variables = variables
        self.objective = objective

    def _recommend_vars(self, current_vals: Dict[str, float], current_score: float,
                        explore_rate: float = 0.1) -> Dict[str, float]:
        """Recommend improved variable values based on current score"""
        recommended = current_vals.copy()

        for var in self.variables:
            name = var.name
            current = current_vals[name]
            var_range = var.max_val - var.min_val

            # perturb each variable slightly to find improvement direction
            delta = var_range * explore_rate * random.choice([-1, 1])
            candidate = var.clamp(current + delta)

            # check if improved
            candidate_vals = recommended.copy()
            candidate_vals[name] = candidate
            candidate_score = self.objective(candidate_vals)

            if candidate_score < current_score:
                recommended[name] = candidate

        return recommended

    def search(self, num_iterations: int = 100) -> Dict:
        """Perform AI-guided search"""
        print(f"\n[AI Recommendation Search] Starting (iterations: {num_iterations})")

        # initialize to starting values
        current_vars = {}
        for var in self.variables:
            current_vars[var.name] = var.init_val

        current_score = self.objective(current_vars)
        best_value = current_score
        best_vars = current_vars.copy()
        history: List[Dict] = []

        for i in range(num_iterations):
            # exploration rate decays over time (finer search)
            explore_rate = 0.3 * math.exp(-i / (num_iterations * 0.3))

            # AI-guided variable update
            recommended_vars = self._recommend_vars(current_vars, current_score, explore_rate)
            recommended_score = self.objective(recommended_vars)

            if recommended_score < current_score:
                current_vars = recommended_vars
                current_score = recommended_score
            else:
                # improvement failed, random restart
                for var in self.variables:
                    current_vars[var.name] = random.uniform(var.min_val, var.max_val)
                current_score = self.objective(current_vars)

            # update best
            if current_score < best_value:
                best_value = current_score
                best_vars = current_vars.copy()

            history.append({"iteration": i + 1, "vars": current_vars.copy(), "score": current_score})

            if (i + 1) % 20 == 0:
                print(f"  Iteration {i+1}/{num_iterations} - current best: {best_value:.4f}")

        return {
            "algorithm": "AI Recommendation Search",
            "best_value": best_value,
            "best_vars": best_vars,
            "history": history,
            "num_iterations": num_iterations,
        }


# ============================================================================
# FreeCAD Model Generation
# ============================================================================

def freecad_model_generation(best_vars: Dict[str, float], model_name: str = "optimal_design") -> bool:
    """Generate FreeCAD model using optimized variables"""
    if not FREECAD_AVAILABLE:
        print("[INFO] Cannot generate model outside FreeCAD environment.")
        print(f"  Best variables: {best_vars}")
        return False

    try:
        doc = FreeCAD.newDocument(model_name)

        x = best_vars.get("width", 50)
        y = best_vars.get("depth", 50)
        z = best_vars.get("height", 50)

        box = Part.makeBox(x, y, z)
        obj = doc.addObject("Part::Feature", model_name)
        obj.Shape = box
        doc.recompute()

        print(f"[DONE] FreeCAD model '{model_name}' created successfully")
        print(f"  Size: {x:.1f} x {y:.1f} x {z:.1f} mm")
        return True

    except Exception as e:
        print(f"[ERROR] Model generation failed: {e}")
        return False


# ============================================================================
# Result Comparison
# ============================================================================

def compare_results(random_result: Dict, ai_result: Dict):
    """Compare two exploration algorithms' results"""
    print("\n" + "=" * 60)
    print("  Algorithm Result Comparison")
    print("=" * 60)

    print(f"\n  {'Item':<20} {'Random Search':>15} {'AI Search':>15}")
    print(f"  {'-'*50}")
    print(f"  {'Best objective':<20} {random_result['best_value']:>15.4f} {ai_result['best_value']:>15.4f}")

    improvement = 0
    if random_result['best_value'] != 0:
        improvement = (random_result['best_value'] - ai_result['best_value']) / abs(random_result['best_value']) * 100

    print(f"  {'AI improvement %':<20} {'-':>15} {improvement:>14.1f}%")

    print(f"\n  Best variable values comparison:")
    for var_name in ai_result['best_vars']:
        random_val = random_result['best_vars'].get(var_name, 0)
        ai_val = ai_result['best_vars'].get(var_name, 0)
        print(f"    {var_name}: random={random_val:.2f}, AI={ai_val:.2f}")

    print("=" * 60)


# ============================================================================
# Main Execution
# ============================================================================

def main():
    """Main execution function"""
    print("=" * 60)
    print("  27. AI Parametric Optimization")
    print("  AI Generative Design - Optimization Demo")
    print("=" * 60)

    random.seed(42)  # reproducible results

    # Variable definitions: box design optimization
    variables = [
        ParametricVariable("width", 20, 200, 100),
        ParametricVariable("depth", 20, 200, 100),
        ParametricVariable("height", 20, 200, 100),
    ]

    print("\n  Design variables:")
    for var in variables:
        print(f"    {var}")

    # ---------------------------------------------------------------
    # Example 1: Minimum Volume Optimization
    # ---------------------------------------------------------------
    print("\n\n" + "#" * 60)
    print("  Example 1: Minimum Volume Optimization")
    print("#" * 60)

    random_searcher = RandomSearch(variables, ObjectiveFunction.min_volume)
    random_result = random_searcher.search(num_iterations=80)

    random.seed(42)
    ai_searcher = AIRecommendationSearch(variables, ObjectiveFunction.min_volume)
    ai_result = ai_searcher.search(num_iterations=80)

    compare_results(random_result, ai_result)

    # FreeCAD model generation
    freecad_model_generation(ai_result['best_vars'], "min_volume_optimal")

    # ---------------------------------------------------------------
    # Example 2: Combined Optimization
    # ---------------------------------------------------------------
    print("\n\n" + "#" * 60)
    print("  Example 2: Combined Optimization (Volume + Strength)")
    print("#" * 60)

    combined_vars = [
        ParametricVariable("width", 30, 150, 80),
        ParametricVariable("depth", 30, 150, 80),
        ParametricVariable("height", 30, 150, 80),
        ParametricVariable("thickness", 2, 20, 5),
    ]

    random.seed(123)
    random_searcher2 = RandomSearch(combined_vars, ObjectiveFunction.combined)
    random_result2 = random_searcher2.search(num_iterations=80)

    random.seed(123)
    ai_searcher2 = AIRecommendationSearch(combined_vars, ObjectiveFunction.combined)
    ai_result2 = ai_searcher2.search(num_iterations=80)

    compare_results(random_result2, ai_result2)

    freecad_model_generation(ai_result2['best_vars'], "combined_optimal")

    # ---------------------------------------------------------------
    # Final Summary
    # ---------------------------------------------------------------
    print("\n\n" + "=" * 60)
    print("  Final Summary")
    print("=" * 60)
    print(f"  Example 1 (min volume): AI improvement = "
          f"{(random_result['best_value'] - ai_result['best_value'])/abs(random_result['best_value'])*100:.1f}%")
    print(f"  Example 2 (combined): AI improvement = "
          f"{(random_result2['best_value'] - ai_result2['best_value'])/abs(random_result2['best_value'])*100:.1f}%")
    print("\n[INFO] AI parametric optimization demo completed.")


if __name__ == "__main__" or FREECAD_AVAILABLE:
    main()
