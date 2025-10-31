from sokoban import SokobanProblem, SokobanState
from mathutils import Direction, Point, manhattan_distance
from helpers.utils import NotImplemented
import itertools


# This heuristic returns the distance between the player and the nearest crate as an estimate for the path cost
# While it is consistent, it does a bad job at estimating the actual cost thus the search will explore a lot of nodes before finding a goal
def weak_heuristic(problem: SokobanProblem, state: SokobanState):
    return min(manhattan_distance(state.player, crate) for crate in state.crates) - 1

#TODO: Import any modules and write any functions you want to use


from collections import deque

def bfs(start: Point, goal: Point, state) -> float:
        
    if start == goal:
        return 0
    
    frontier = deque([(start, 0)])
    explored = set([start])
    
    while len(frontier) != 0:
        current, dist = frontier.popleft()

        for dir in [Direction.LEFT, Direction.RIGHT, Direction.UP, Direction.DOWN]:
            
            neighbor = current + dir.to_vector()
            push = current - dir.to_vector()

            # To push the crate, the player must be in the opposite direction of the push
            # so the tile in the reverse direction must be walkable
            # don't check if it a crate becausse it makes the heuristic incosnsistent 
            if push not in state.layout.walkable:
                continue

            if neighbor == goal:
                return dist + 1
            
            if neighbor in state.layout.walkable and neighbor not in explored:
                explored.add(neighbor)
                frontier.append((neighbor, dist + 1))    

    # Large number to denote that the goal is unreachable
    return 1000


def strong_heuristic(problem: SokobanProblem, state: SokobanState) -> float:


    n = len(state.crates)

    # distances[i][j] have the distance from crate i to goal j
    distances = [[0 for _ in range(n)] for _ in range(n)]
    
    for i, crate in enumerate(state.crates):
        for j, goal in enumerate(state.layout.goals):
    
            key = (crate, goal)
    
            if key in problem.cache():
                distance = problem.cache()[key]
            else:
                # Manhattan distance underestimated the cost to move a crate to a goal
                # So we use BFS to find a better estimate with taking the walls into account
                # We cache the bfs results to avoid recomputing them multiple times
                distance = bfs(crate, goal, state)
                problem.cache()[key] = distance
    
            distances[i][j] = distance

    # We go over all the permuations of cratesxgoals to find the optimal assignment
    best_h = float('inf')
    for perm in itertools.permutations(range(n), n):  
        total_cost = sum(distances[i][perm[i]] for i in range(n))
        best_h = min(best_h, total_cost)

    return best_h
