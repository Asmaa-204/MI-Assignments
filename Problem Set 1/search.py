from problem import HeuristicFunction, Problem, S, A, Solution
from collections import deque
from helpers.utils import NotImplemented

# TODO: Import any modules you want to use
import heapq
import itertools

# All search functions take a problem and a state
# If it is an informed search function, it will also receive a heuristic function
# S and A are used for generic typing where S represents the state type and A represents the action type

# All the search functions should return one of two possible type:
# 1. A list of actions which represent the path from the initial state to the final state
# 2. None if there is no solution


def BreadthFirstSearch(problem: Problem[S, A], initial_state: S) -> Solution:
    # TODO: ADD YOUR CODE HERE
    # BFS checks whether a node is goal BEFORE inserting it into the frontier
    if problem.is_goal(initial_state):
        return []

    # FIFO queue storing tuples of (state, path)
    frontier = deque([(initial_state, [])])
    # set of nodes in frontier for faster search for a specific node
    frontier_states = {initial_state}
    explored = set()

    while frontier:
        state, path = frontier.popleft()
        explored.add(state)

        for action in problem.get_actions(state):
            next_state = problem.get_successor(state, action)

            # if the node is already in the frontier or explored --> neglect it
            if next_state in explored or next_state in frontier_states:
                continue

            new_path = path + [action]
            # check if the state is goal state before adding it to the frontier
            if problem.is_goal(next_state):
                return new_path

            # add it to the frontier
            frontier.append((next_state, new_path))
            frontier_states.add(next_state)

    # frontier is empty and no goal is found
    return None


def DepthFirstSearch(problem: Problem[S, A], initial_state: S) -> Solution:
    # TODO: ADD YOUR CODE HERE
    NotImplemented()


def UniformCostSearch(problem: Problem[S, A], initial_state: S) -> Solution:
    # TODO: ADD YOUR CODE HERE

    # for FIFO behavior on a cost tie
    counter = itertools.count()
    # frontier is a priority queue of action costs
    frontier = []
    # frontier is a heap of tubles (cost, tie_resolver, state, path)
    # sorted with the cost, if there's a tie sort with the counter which follows FIFO behavior
    heapq.heappush(frontier, (0, next(counter), initial_state, []))

    # dictionary of path costs from initial state to any node --> updated when the node is inserted to the frontier AKA if the state exists as a key then it's already in the frontier
    cost_so_far = {initial_state: 0}
    explored = set()

    # goal-test is done when the node is expanded
    while frontier:
        cost, _, state, path = heapq.heappop(frontier)

        # skip if a newer version with less cost was found -> avoid deletion from the heap
        if cost > cost_so_far[state]:
            continue

        explored.add(state)

        # if it's the goal, return the path to this node
        if problem.is_goal(state):
            return path

        # expand the node
        for action in problem.get_actions(state):
            next_state = problem.get_successor(state, action)
            new_cost = cost + problem.get_cost(state, action)

            # if the node is already explored -> neglect it
            if next_state in explored:
                continue
            # if the node was already in the frontier, replace it with the new node if its cost < old node
            # Only push if it's new or cheaper than before
            if next_state not in cost_so_far or new_cost < cost_so_far[next_state]:
                cost_so_far[next_state] = new_cost
                heapq.heappush(
                    frontier, (new_cost, next(counter), next_state, path + [action])
                )

    # frontier is empty and no solution is found
    return None


def AStarSearch(
    problem: Problem[S, A], initial_state: S, heuristic: HeuristicFunction
) -> Solution:
    # TODO: ADD YOUR CODE HERE
    # for FIFO behavior on a cost tie
    counter = itertools.count()
    # maintian a priority queue based on total cost = total backward cost + node's heuristic
    frontier = []
    explored = set()
    total_costs = {initial_state: heuristic(problem, initial_state)}
    # insert initial state goal into the frontier
    # heap_item = (total_cost, counter, total_backward_cost, state, path)
    heapq.heappush(
        frontier,
        (heuristic(problem, initial_state), next(counter), 0, initial_state, []),
    )
    # loop until the frontier is empty
    while frontier:
        # pop from the frontier
        _, _, total_backward_cost, state, path = heapq.heappop(frontier)
        # add it to explored set
        explored.add(state)
        # if the node is goal, return the solution
        if problem.is_goal(state):
            return path
        # expand it
        for action in problem.get_actions(state):
            next_state = problem.get_successor(state, action)
            new_cost = problem.get_cost(state, action)

            # if the node is already explored, neglect it
            if next_state in explored:
                continue
            # compute the node's total cost
            next_state_total_cost = (
                total_backward_cost + new_cost + heuristic(problem, next_state)
            )
            # if the node is already in the frontier with higher cost, replace it with the the new one
            if (
                next_state not in total_costs
                or total_costs[next_state] > next_state_total_cost
            ):
                total_costs[next_state] = next_state_total_cost
                # add it to the frontier
                heapq.heappush(
                    frontier,
                    (
                        next_state_total_cost,
                        next(counter),
                        total_backward_cost + new_cost,
                        next_state,
                        path + [action],
                    ),
                )
    # frontier is empty and no solution is found
    return None


def BestFirstSearch(
    problem: Problem[S, A], initial_state: S, heuristic: HeuristicFunction
) -> Solution:
    # TODO: ADD YOUR CODE HERE
    # for FIFO behavior on a cost tie
    counter = itertools.count()
    # maintian a priority queue based on node's heuristic
    frontier = []
    explored = set()
    heuristics = {initial_state: heuristic(problem, initial_state)}
    # insert initial state goal into the frontier
    # heap_item = (heuristic, counter, state, path)
    heapq.heappush(
        frontier,
        (heuristic(problem, initial_state), next(counter), initial_state, []),
    )
    # loop until the frontier is empty
    while frontier:
        # pop from the frontier
        _, _, state, path = heapq.heappop(frontier)
        # add it to explored set
        explored.add(state)
        # if the node is goal, return the solution
        if problem.is_goal(state):
            return path
        # expand it
        for action in problem.get_actions(state):
            next_state = problem.get_successor(state, action)
            new_cost = problem.get_cost(state, action)

            # if the node is already explored, neglect it
            if next_state in explored:
                continue
            # compute the node's total cost
            next_state_heuristic = heuristic(problem, next_state)
            # if the node is already in the frontier with higher cost, replace it with the the new one
            if (
                next_state not in heuristics
                or heuristics[next_state] > next_state_heuristic
            ):
                heuristics[next_state] = next_state_heuristic
                # add it to the frontier
                heapq.heappush(
                    frontier,
                    (
                        next_state_heuristic,
                        next(counter),
                        next_state,
                        path + [action],
                    ),
                )
    # frontier is empty and no solution is found
    return None
