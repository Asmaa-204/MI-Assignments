from sokoban import SokobanProblem, SokobanState
from mathutils import Direction, Point, manhattan_distance
from helpers.utils import NotImplemented

# This heuristic returns the distance between the player and the nearest crate as an estimate for the path cost
# While it is consistent, it does a bad job at estimating the actual cost thus the search will explore a lot of nodes before finding a goal
def weak_heuristic(problem: SokobanProblem, state: SokobanState):
    return min(manhattan_distance(state.player, crate) for crate in state.crates) - 1

#TODO: Import any modules and write any functions you want to use

flag = False

def strong_heuristic(problem: SokobanProblem, state: SokobanState) -> float:
    #TODO: ADD YOUR CODE HERE
    #IMPORTANT: DO NOT USE "problem.get_actions" HERE.
    # Calling it here will mess up the tracking of the expanded nodes count
    # which is the number of get_actions calls during the search
    #NOTE: you can use problem.cache() to get a dictionary in which you can store information that will persist between calls of this function
    # This could be useful if you want to store the results heavy computations that can be cached and used across multiple calls of this function

    is_wall = lambda point: point not in state.layout.walkable
    is_goal = lambda point: point in state.layout.goals
    is_crate = lambda point: point in state.crates
    up = lambda point: Point(point.x, point.y + 1)
    down = lambda point: Point(point.x, point.y - 1)
    right = lambda point: Point(point.x + 1, point.y)
    left  = lambda point: Point(point.x - 1, point.y)
    
    # Deadlock detection: if a crate is in a corner and that corner is not a goal, return infinity
    for crate in state.crates:

        if ( (Point(crate.x + 1, crate.y) not in state.layout.walkable and Point(crate.x, crate.y + 1) not in state.layout.walkable) or
             (Point(crate.x - 1, crate.y) not in state.layout.walkable and Point(crate.x, crate.y + 1) not in state.layout.walkable) or
             (Point(crate.x + 1, crate.y) not in state.layout.walkable and Point(crate.x, crate.y - 1) not in state.layout.walkable) or
             (Point(crate.x - 1, crate.y) not in state.layout.walkable and Point(crate.x, crate.y - 1) not in state.layout.walkable) ):
            if crate not in state.layout.goals:
                # print("[Deadlock] crate in a corner")
                return float('inf')
            
    # Deadlock detection
    for crate_1 in state.crates:
        for crate_2 in state.crates:
            
            if crate_1 == crate_2:
                continue

            # Check that both are beside a wall
            check_1 = is_wall( Point(crate_1.x + 1, crate_1.y) ) and is_wall( Point(crate_2.x + 1, crate_2.y) ) and crate_1.x == crate_2.x
            check_2 = is_wall( Point(crate_1.x - 1, crate_1.y) ) and is_wall( Point(crate_2.x - 1, crate_2.y) ) and crate_1.x == crate_2.x
            check_3 = is_wall( Point(crate_1.x, crate_1.y + 1) ) and is_wall( Point(crate_2.x, crate_2.y + 1) ) and crate_1.y == crate_2.y
            check_4 = is_wall( Point(crate_1.x, crate_1.y - 1) ) and is_wall( Point(crate_2.x, crate_2.y - 1) ) and crate_1.y == crate_2.y

            if check_1 or check_2 or check_3 or check_4:
                if crate_1 not in state.layout.goals and crate_2 not in state.layout.goals:
                    # print("[Deadlock] two crates beside walls")
                    return float('inf')
                

    # Deadlock detection: Four boxes in a square formation
    for crate in state.crates:
        check_1 = is_crate(up(crate)) and is_crate(left(crate)) and is_crate(Point(crate.x - 1, crate.y + 1))
        check_2 = is_crate(up(crate)) and is_crate(right(crate)) and is_crate(Point(crate.x + 1, crate.y + 1))
        check_3 = is_crate(down(crate)) and is_crate(left(crate)) and is_crate(Point(crate.x - 1, crate.y - 1))
        check_4 = is_crate(down(crate)) and is_crate(right(crate)) and is_crate(Point(crate.x + 1, crate.y - 1)) 
   
        if check_1 or check_2 or check_3 or check_4:
            print("[Deadlock] four boxes in square formation")
            return float('inf')
        

    h = 0.0
    goals_copy = list(state.layout.goals.copy())

    for crate in state.crates:
        goal = min(goals_copy, key = lambda x : manhattan_distance(x, crate))
        h += manhattan_distance(crate, goal)

    return h