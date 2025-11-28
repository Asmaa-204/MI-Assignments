from typing import Tuple
from game import HeuristicFunction, Game, S, A
from helpers.utils import NotImplemented

# TODO: Import any modules you want to use
import math

# All search functions take a problem, a state, a heuristic function and the maximum search depth.
# If the maximum search depth is -1, then there should be no depth cutoff (The expansion should not stop before reaching a terminal state)

# All the search functions should return the expected tree value and the best action to take based on the search results

# This is a simple search function that looks 1-step ahead and returns the action that lead to highest heuristic value.
# This algorithm is bad if the heuristic function is weak. That is why we use minimax search to look ahead for many steps.
def greedy(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    agent = game.get_turn(state)
    
    terminal, values = game.is_terminal(state)
    if terminal: return values[agent], None

    actions_states = [(action, game.get_successor(state, action)) for action in game.get_actions(state)]
    value, _, action = max((heuristic(game, state, agent), -index, action) for index, (action , state) in enumerate(actions_states))
    return value, action

# Apply Minimax search and return the game tree value and the best action
# Hint: There may be more than one player, and in all the testcases, it is guaranteed that
# game.get_turn(state) will return 0 (which means it is the turn of the player). All the other players
# (turn > 0) will be enemies. So for any state "s", if the game.get_turn(s) == 0, it should a max node,
# and if it is > 0, it should be a min node. Also remember that game.is_terminal(s), returns the values
# for all the agents. So to get the value for the player (which acts at the max nodes), you need to
# get values[0].
def minimax(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    # TODO: Complete this function
    def dfs(state, depth):
        # check if it's a terminal state
        terminal, values = game.is_terminal(state)
        # if it's a terminal state, return MAX node's utility
        if terminal: return values[0], None
        if depth == 0: return heuristic(game, state, 0), None
        agent = game.get_turn(state)
        # if it's a max player
        if agent == 0:
            # value it tries to maximize
            value = float("-inf")
            # action to get the max value
            best_action = None
            for action in game.get_actions(state):
                next_state = game.get_successor(state, action)
                v, _ = dfs(next_state, depth - 1 if depth > 0 else -1)
                # if the value returned from min node is higher than the node's value
                if v > value:
                    # update node's value
                    value = v
                    # update the action
                    best_action = action
            return value, best_action
        # if it's a min player
        else: 
            # value it tries to minimize
            value = float("inf")
            # action to get the min value
            best_action = None
            for action in game.get_actions(state):
                next_state = game.get_successor(state, action)
                v, _ = dfs(next_state, depth - 1 if depth > 0 else -1)
                # if the value returned from a node is less than the node's value
                if v < value:
                    # update node's value
                    value = v
                    # update the action
                    best_action = action
            return value, best_action
    return dfs(state, max_depth)


# Apply Alpha Beta pruning and return the tree value and the best action
# Hint: Read the hint for minimax.
def alphabeta(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    # TODO: Complete this function
    def dfs(s, depth, alpha, beta):
        terminal, values = game.is_terminal(s)
        if terminal:
            return values[0], None

        if depth == 0:
            return heuristic(game, s, 0), None

        turn = game.get_turn(s)
        actions = game.get_actions(s)

        # if it's a max node (the player)
        if turn == 0:
            # tries to maximize its value
            value = float("-inf")
            action = None
            for a in actions:
                next_state = game.get_successor(s, a)
                v, _ = dfs(next_state, depth - 1 if depth > 0 else -1, alpha, beta)
                # prune if the current value is not less than what a min node has prev got
                if v >= beta: return v, action
                if v > value:
                    value = v
                    action = a
                alpha = max(alpha, v)
            return value, action

        # if it's a min node (the enemies)
        else:
            # tries to minimize its value
            value = float("inf")
            action = None
            for a in actions:
                next_state = game.get_successor(s, a)
                v, _ = dfs(next_state, depth - 1 if depth > 0 else -1, alpha, beta)
                # prune if the current value is not higher than what a max node has prev got
                if v <= alpha: return v, action
                if v < value:
                    value = v
                    action = a
                beta = min(beta, v)

            return value, action

    return dfs(state, max_depth, float("-inf"), float("inf"))

# Apply Alpha Beta pruning with move ordering and return the tree value and the best action
# Hint: Read the hint for minimax.
def alphabeta_with_move_ordering(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    #TODO: Complete this function
    NotImplemented()

# Apply Expectimax search and return the tree value and the best action
# Hint: Read the hint for minimax, but note that the monsters (turn > 0) do not act as min nodes anymore,
# they now act as chance nodes (they act randomly).
def expectimax(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    # TODO: Complete this function
    def dfs(state, depth):
        # check if it's a terminal state
        terminal, values = game.is_terminal(state)
        # if it's a terminal state, return MAX node's utility
        if terminal: return values[0], None
        if depth == 0: return heuristic(game, state, 0), None
        agent = game.get_turn(state)

        # max node
        if agent == 0:
            # value it tries to maximize
            value = float("-inf")
            # action to get the max value
            best_action = None
            for action in game.get_actions(state):
                next_state = game.get_successor(state, action)
                v, _ = dfs(next_state, depth - 1 if depth > 0 else -1)
                # if the value returned from min node is higher than the node's value
                if v > value:
                    # update node's value
                    value = v
                    # update the action
                    best_action = action
            return value, best_action
        # chance node
        else: 
            values = []
            for action in game.get_actions(state):
                next_state = game.get_successor(state, action)
                v, _ = dfs(next_state, depth - 1 if depth > 0 else -1)
                values.append(v)
            # returns the expected value from all actions
            expectation = sum(values) / len(values)
            return expectation, None

    return dfs(state, max_depth)
