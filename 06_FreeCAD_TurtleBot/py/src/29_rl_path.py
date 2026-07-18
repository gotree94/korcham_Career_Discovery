"""
29_rl_path.py - Reinforcement Learning Path Design
====================================================
Simple reinforcement learning (RL) concepts for optimal path/structure exploration.

- State/action/reward definition
- Greedy policy optimization
- Visualization

Created: 2026-07-14
"""

import math
import random
from typing import List, Tuple, Dict, Optional

# FreeCAD environment check
FREECAD_AVAILABLE = False
try:
    import FreeCAD
    import Part
    from FreeCAD import Base
    FREECAD_AVAILABLE = True
except ImportError:
    print("[INFO] FreeCAD module not available. Running in simulation mode.")

# Visualization library check
VISUALIZE_AVAILABLE = False
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    VISUALIZE_AVAILABLE = True
except ImportError:
    print("[INFO] matplotlib not available. Using text-based visualization.")


# ============================================================================
# Grid Environment Definition
# ============================================================================

class GridEnvironment:
    """
    2D grid-based pathfinding environment.
    Agent navigates from start to goal along optimal path.
    """

    def __init__(self, width: int = 20, height: int = 15):
        self.width = width
        self.height = height
        self.start_pos = (0, 0)
        self.goal_pos = (width - 1, height - 1)
        self.obstacles: List[Tuple[int, int]] = []
        self.current_pos = self.start_pos

        # generate obstacles randomly
        self._generate_obstacles()

    def _generate_obstacles(self):
        """Generate obstacles randomly"""
        self.obstacles = []
        total_cells = self.width * self.height
        num_obstacles = int(total_cells * 0.15)  # 15% of cells

        for _ in range(num_obstacles):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if (x, y) != self.start_pos and (x, y) != self.goal_pos:
                if (x, y) not in self.obstacles:
                    self.obstacles.append((x, y))

    def reset(self):
        """Reset environment to initial state"""
        self.current_pos = self.start_pos
        return self.current_pos

    def state(self) -> Tuple[int, int]:
        """Return current state (position)"""
        return self.current_pos

    def action_valid(self, action: int) -> bool:
        """
        Check if action is valid.
        Action: 0=up, 1=down, 2=left, 3=right, 4=upleft, 5=upright, 6=downleft, 7=downright
        """
        x, y = self.current_pos
        move = {
            0: (0, 1), 1: (0, -1), 2: (-1, 0), 3: (1, 0),
            4: (-1, 1), 5: (1, 1), 6: (-1, -1), 7: (1, -1),
        }

        dx, dy = move[action]
        nx, ny = x + dx, y + dy

        # boundary check
        if nx < 0 or nx >= self.width or ny < 0 or ny >= self.height:
            return False

        # obstacle check
        if (nx, ny) in self.obstacles:
            return False

        return True

    def step(self, action: int) -> Tuple[Tuple[int, int], float, bool]:
        """
        Execute action and return (new_state, reward, done).
        """
        if not self.action_valid(action):
            return self.current_pos, -5.0, False  # wall/obstacle collision penalty

        move = {
            0: (0, 1), 1: (0, -1), 2: (-1, 0), 3: (1, 0),
            4: (-1, 1), 5: (1, 1), 6: (-1, -1), 7: (1, -1),
        }

        dx, dy = move[action]
        self.current_pos = (self.current_pos[0] + dx, self.current_pos[1] + dy)

        # reward calculation
        if self.current_pos == self.goal_pos:
            return self.current_pos, 100.0, True  # large reward for reaching goal

        # distance-based reward (closer = positive, farther = negative)
        prev_dist = abs(self.start_pos[0] - self.goal_pos[0]) + abs(self.start_pos[1] - self.goal_pos[1])
        curr_dist = abs(self.current_pos[0] - self.goal_pos[0]) + abs(self.current_pos[1] - self.goal_pos[1])
        reward = (prev_dist - curr_dist) * 0.5 - 0.1  # distance reduction reward + step penalty

        # penalty for returning to start
        if self.current_pos == self.start_pos and self.start_pos != self.start_pos:
            reward -= 2.0

        return self.current_pos, reward, False


# ============================================================================
# Q-Learning Agent
# ============================================================================

class QLearningAgent:
    """Greedy policy-based Q-Learning agent"""

    def __init__(self, num_actions: int = 8, learning_rate: int = 0.1, discount_factor: float = 0.95,
                 exploration_rate: float = 0.3):
        self.num_actions = num_actions
        # Q-table: {(state_x, state_y): [Q_value_action0, Q_value_action1, ...]}
        self.Q: Dict[Tuple[int, int], List[float]] = {}
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate

    def get_q_value(self, state: Tuple[int, int]) -> List[float]:
        """Return Q-values for a given state; initialize if not found"""
        if state not in self.Q:
            self.Q[state] = [0.0] * self.num_actions
        return self.Q[state]

    def select_action(self, state: Tuple[int, int], env: GridEnvironment) -> int:
        """Select action using epsilon-greedy policy"""
        if random.random() < self.exploration_rate:
            # exploration: random among valid actions
            valid_actions = [a for a in range(self.num_actions) if env.action_valid(a)]
            if not valid_actions:
                return 0
            return random.choice(valid_actions)

        # exploitation: select highest Q-value action
        q_vals = self.get_q_value(state)
        valid_actions = [a for a in range(self.num_actions) if env.action_valid(a)]

        if not valid_actions:
            return 0

        best_action = max(valid_actions, key=lambda a: q_vals[a])
        return best_action

    def learn(self, state: Tuple[int, int], action: int, reward: float,
              next_state: Tuple[int, int], done: bool):
        """Update Q-value"""
        q_vals = self.get_q_value(state)
        next_q_vals = self.get_q_value(next_state)

        if done:
            target = reward
        else:
            target = reward + self.discount_factor * max(next_q_vals)

        q_vals[action] += self.learning_rate * (target - q_vals[action])

    def decay_exploration(self, min_exploration: float = 0.05):
        """Gradually reduce exploration rate"""
        self.exploration_rate = max(min_exploration, self.exploration_rate * 0.995)


# ============================================================================
# Training Loop
# ============================================================================

class RLPathLearner:
    """Reinforcement learning based path learner"""

    def __init__(self, env: GridEnvironment, agent: QLearningAgent):
        self.env = env
        self.agent = agent
        self.training_history: List[Dict] = []

    def train(self, num_episodes: int = 200, max_steps: int = 100) -> List[Dict]:
        """Perform episode-based training"""
        print(f"\n[Training Started] Episodes: {num_episodes}, Max steps: {max_steps}")

        for episode in range(1, num_episodes + 1):
            state = self.env.reset()
            total_reward = 0
            path: List[Tuple[int, int]] = [state]

            for step in range(max_steps):
                # select action
                action = self.agent.select_action(state, self.env)

                # execute action
                next_state, reward, done = self.env.step(action)

                # learn
                self.agent.learn(state, action, reward, next_state, done)

                total_reward += reward
                path.append(next_state)
                state = next_state

                if done:
                    break

            # decay exploration
            self.agent.decay_exploration()

            # record history
            reached = self.env.current_pos == self.env.goal_pos
            record = {
                "episode": episode,
                "total_reward": total_reward,
                "steps": len(path),
                "reached": reached,
                "path": path,
                "exploration_rate": self.agent.exploration_rate,
            }
            self.training_history.append(record)

            if episode % 20 == 0 or reached:
                status = "reached" if reached else "failed"
                print(f"  Episode {episode:>4d} | "
                      f"Reward: {total_reward:>7.1f} | "
                      f"Steps: {len(path):>3d} | "
                      f"{status} | "
                      f"Exploration: {self.agent.exploration_rate:.3f}")

        print("[Training Complete]")
        return self.training_history

    def greedy_path(self) -> List[Tuple[int, int]]:
        """Return greedy path using learned policy"""
        self.env.reset()
        path = [self.env.state()]

        for _ in range(200):
            state = self.env.state()
            q_vals = self.agent.get_q_value(state)
            valid_actions = [a for a in range(self.agent.num_actions) if self.env.action_valid(a)]

            if not valid_actions:
                break

            action = max(valid_actions, key=lambda a: q_vals[a])
            next_state, reward, done = self.env.step(action)
            path.append(next_state)

            if done:
                break

        return path


# ============================================================================
# Visualization
# ============================================================================

class PathVisualizer:
    """Visualizes training results and paths"""

    @staticmethod
    def text_visualization(env: GridEnvironment, path: List[Tuple[int, int]]):
        """Text-based grid visualization"""
        grid = [["." for _ in range(env.width)] for _ in range(env.height)]

        # mark obstacles
        for x, y in env.obstacles:
            grid[y][x] = "X"

        # mark path
        for i, (x, y) in enumerate(path):
            if 0 <= y < env.height and 0 <= x < env.width:
                if grid[y][x] != "X":
                    grid[y][x] = "*"

        # mark start/goal
        sx, sy = env.start_pos
        gx, gy = env.goal_pos
        grid[sy][sx] = "S"
        grid[gy][gx] = "G"

        print("\n  Grid Visualization (S=Start, G=Goal, X=Obstacle, *=Path):")
        print("  +" + "-" * (env.width * 2 + 1) + "+")
        for row in reversed(grid):
            print("  | " + " ".join(row) + " |")
        print("  +" + "-" * (env.width * 2 + 1) + "+")

    @staticmethod
    def learning_curve_visualization(history: List[Dict], save_path: str = None):
        """Visualize learning curves"""
        if not VISUALIZE_AVAILABLE:
            print("\n  [INFO] matplotlib unavailable. Showing text-based learning curve.")
            print(f"  {'Episode':>8} {'Total Reward':>10} {'Reached':>6}")
            print(f"  {'-' * 28}")
            for record in history[::max(1, len(history) // 10)]:
                reached = "O" if record['reached'] else "X"
                print(f"  {record['episode']:>8d} {record['total_reward']:>10.1f} {reached:>6}")
            return

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

        episodes = [record["episode"] for record in history]
        rewards = [record["total_reward"] for record in history]
        steps = [record["steps"] for record in history]

        # total reward curve
        ax1.plot(episodes, rewards, "b-", alpha=0.3, label="Total Reward")
        # moving average
        if len(rewards) >= 10:
            moving_avg = [sum(rewards[max(0, i-9):i+1]) / min(10, i+1) for i in range(len(rewards))]
            ax1.plot(episodes, moving_avg, "r-", linewidth=2, label="Moving Avg (10)")
        ax1.set_xlabel("Episode")
        ax1.set_ylabel("Total Reward")
        ax1.set_title("RL Reward Curve")
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # steps curve
        ax2.plot(episodes, steps, "g-", alpha=0.3, label="Steps")
        ax2.set_xlabel("Episode")
        ax2.set_ylabel("Steps")
        ax2.set_title("Steps per Episode")
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=100)
            print(f"[INFO] Learning curve image saved: {save_path}")
        else:
            plt.savefig("C:\\Users\\Administrator\\Downloads\\py\\src\\29_rl_learning_curve.png",
                        dpi=100)
            print("[INFO] Learning curve image saved: 29_rl_learning_curve.png")

        plt.close()

    @staticmethod
    def final_path_visualization(env: GridEnvironment, path: List[Tuple[int, int]],
                       save_path: str = None):
        """Visualize the final path"""
        if not VISUALIZE_AVAILABLE:
            return

        fig, ax = plt.subplots(1, 1, figsize=(12, 8))

        # grid background
        for x in range(env.width):
            for y in range(env.height):
                if (x, y) in env.obstacles:
                    rect = mpatches.Rectangle((x - 0.5, y - 0.5), 1, 1,
                                              facecolor="gray", edgecolor="black")
                    ax.add_patch(rect)

        # draw path
        if path:
            xs = [p[0] for p in path]
            ys = [p[1] for p in path]
            ax.plot(xs, ys, "b-o", markersize=4, linewidth=2, label="Path")

        # start/goal points
        ax.plot(env.start_pos[0], env.start_pos[1], "go", markersize=15, label="Start")
        ax.plot(env.goal_pos[0], env.goal_pos[1], "r*", markersize=20, label="Goal")

        ax.set_xlim(-1, env.width)
        ax.set_ylim(-1, env.height)
        ax.set_aspect("equal")
        ax.set_title("RL-Based Optimal Path")
        ax.legend()
        ax.grid(True, alpha=0.3)

        if save_path:
            plt.savefig(save_path, dpi=100)
        else:
            plt.savefig("C:\\Users\\Administrator\\Downloads\\py\\src\\29_rl_final_path.png",
                        dpi=100)
            print("[INFO] Final path image saved: 29_rl_final_path.png")

        plt.close()


# ============================================================================
# FreeCAD Path Simulation
# ============================================================================

def freecad_path_simulation(path: List[Tuple[int, int]], scale: float = 5.0):
    """Simulate learned path in FreeCAD in 3D"""
    if not FREECAD_AVAILABLE:
        print("[INFO] Cannot simulate path in FreeCAD.")
        print(f"  Path length: {len(path)} points")
        return

    try:
        doc = FreeCAD.newDocument("RLPathSimulation")

        # create wire connecting path points
        wire_points = []
        for x, y in path:
            wire_points.append(Base.Vector(x * scale, y * scale, 0))

        if len(wire_points) >= 2:
            wire = Part.makePolygon(wire_points)
            obj = doc.addObject("Part::Feature", "path")
            obj.Shape = wire

        # spheres at start and goal
        start_sphere = Part.makeSphere(2.0, Base.Vector(path[0][0] * scale,
                                                   path[0][1] * scale, 0))
        obj_s = doc.addObject("Part::Feature", "start_point")
        obj_s.Shape = start_sphere

        goal_sphere = Part.makeSphere(2.0, Base.Vector(path[-1][0] * scale,
                                                path[-1][1] * scale, 0))
        obj_g = doc.addObject("Part::Feature", "goal_point")
        obj_g.Shape = goal_sphere

        doc.recompute()
        print(f"[DONE] FreeCAD path simulation created (path length: {len(path)} points)")

    except Exception as e:
        print(f"[ERROR] FreeCAD path simulation failed: {e}")


# ============================================================================
# Main Execution
# ============================================================================

def main():
    """Main execution function"""
    print("=" * 60)
    print("  29. Reinforcement Learning Path Design")
    print("  AI Generative Design - RL Pathfinding Demo")
    print("=" * 60)

    random.seed(42)

    # initialize environment and agent
    env = GridEnvironment(width=20, height=15)
    agent = QLearningAgent(
        num_actions=8,
        learning_rate=0.1,
        discount_factor=0.95,
        exploration_rate=0.3,
    )

    print(f"\n  Grid size: {env.width} x {env.height}")
    print(f"  Obstacles: {len(env.obstacles)}")
    print(f"  Start: {env.start_pos}")
    print(f"  Goal: {env.goal_pos}")

    # perform training
    learner = RLPathLearner(env, agent)
    history = learner.train(num_episodes=200, max_steps=100)

    # training statistics
    reached_episodes = [record for record in history if record['reached']]
    print(f"\n  Training Statistics:")
    print(f"    Total episodes: {len(history)}")
    print(f"    Goal reached: {len(reached_episodes)} times "
          f"({len(reached_episodes)/len(history)*100:.1f}%)")

    if reached_episodes:
        min_steps = min(record['steps'] for record in reached_episodes)
        print(f"    Shortest path: {min_steps} steps")

    # get greedy path
    print("\n[INFO] Computing learned greedy path...")
    optimal_path = learner.greedy_path()
    print(f"  Greedy path length: {len(optimal_path)} points")
    print(f"  Path start: {optimal_path[0]}")
    print(f"  Path end: {optimal_path[-1]}")

    # visualization
    print("\n[INFO] Performing visualization...")
    PathVisualizer.text_visualization(env, optimal_path)

    if VISUALIZE_AVAILABLE:
        PathVisualizer.learning_curve_visualization(history)
        PathVisualizer.final_path_visualization(env, optimal_path)

    # FreeCAD simulation
    freecad_path_simulation(optimal_path)

    print("\n[INFO] RL path design demo completed.")


if __name__ == "__main__" or FREECAD_AVAILABLE:
    main()
