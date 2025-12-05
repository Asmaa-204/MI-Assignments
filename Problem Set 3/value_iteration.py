from typing import Dict, Optional
from agents import Agent
from environment import Environment
from mdp import MarkovDecisionProcess, S, A
import json
from helpers.utils import NotImplemented

# This is a class for a generic Value Iteration agent
class ValueIterationAgent(Agent[S, A]):
    mdp: MarkovDecisionProcess[S, A] # The MDP used by this agent for training 
    utilities: Dict[S, float] # The computed utilities
    # The key is the string representation of the state and the value is the utility
    discount_factor: float # The discount factor (gamma)

    def __init__(self, mdp: MarkovDecisionProcess[S, A], discount_factor: float = 0.99) -> None:
        super().__init__()
        self.mdp = mdp
        self.utilities = {state:0 for state in self.mdp.get_states()} # We initialize all the utilities to be 0
        self.discount_factor = discount_factor

    # Given a state, compute its utility using the bellman equation
    # if the state is terminal, return 0
    def compute_bellman(self, state: S) -> float:
        # TODO: Complete this function
        # if the state is terminal, its utility is defined as 0
        if self.mdp.is_terminal(state):
            return 0

        max_utility = float("-inf")

        # evaluate the utility for each possible action
        for action in self.mdp.get_actions(state):
            prob_dist = self.mdp.get_successor(state, action)

            # expected utility of taking this action
            utility = 0
            for next_state, prob in prob_dist.items():
                # reward for transitioning to next_state
                reward = self.mdp.get_reward(state, action, next_state)

                # contribution: P(s'|s,a) * (R(s,a,s') + γ * U(s'))
                utility += prob * (reward + self.discount_factor * self.utilities[next_state])

            # keep the best action value
            max_utility = max(max_utility, utility)

        # return the optimal utility for the state
        return max_utility

    # Applies a single utility update
    # then returns True if the utilities has converged (the maximum utility change is less or equal the tolerance)
    # and False otherwise
    def update(self, tolerance: float = 0) -> bool:
        # TODO: Complete this function
        new_utilities = {}
        max_change = 0.0

        for state in self.mdp.get_states():
            # for each state, compute its utility using bellman equation
            new_utility = self.compute_bellman(state)
            # get the utility computed from prev iteration
            old_utility = self.utilities[state]
            new_utilities[state] = new_utility
            max_change = max(max_change, abs(new_utility - old_utility))

        # update all utilities
        self.utilities = new_utilities
        # returns whether utilities have converged or not
        return max_change <= tolerance

    # This function applies value iteration starting from the current utilities stored in the agent and stores the new utilities in the agent
    # NOTE: this function does incremental update and does not clear the utilities to 0 before running
    # In other words, calling train(M) followed by train(N) is equivalent to just calling train(N+M)
    def train(self, iterations: Optional[int] = None, tolerance: float = 0) -> int:
        # TODO: Complete this function to apply value iteration for the given number of iterations
        # store the actual number of iterations
        count = 0
        
        while True:
            # update the utilities
            converged = self.update(tolerance)
            count += 1
            # if utilities converged or completed the specified num of iterations, return
            if converged or count == iterations:
                break

        return count
            

    # Given an environment and a state, return the best action as guided by the learned utilities and the MDP
    # If the state is terminal, return None
    def act(self, env: Environment[S, A], state: S) -> A:
        # TODO: Complete this function
        # this func is same as bellman function but it should retunr the action that's combined with the max utility
        if self.mdp.is_terminal(state):
            return None

        # store best action
        optimal_policy = None
        max_utility = float("-inf")

        for action in self.mdp.get_actions(state):
            utility = 0.0
            for next_state, prob in self.mdp.get_successor(state, action).items():
                reward = self.mdp.get_reward(state, action, next_state)
                utility += prob * (reward + self.discount_factor * self.utilities[next_state])
            
            if utility > max_utility:
                max_utility = utility
                optimal_policy = action

        return optimal_policy

    # Save the utilities to a json file
    def save(self, env: Environment[S, A], file_path: str):
        with open(file_path, 'w') as f:
            utilities = {self.mdp.format_state(state): value for state, value in self.utilities.items()}
            json.dump(utilities, f, indent=2, sort_keys=True)

    # loads the utilities from a json file
    def load(self, env: Environment[S, A], file_path: str):
        with open(file_path, 'r') as f:
            utilities = json.load(f)
            self.utilities = {self.mdp.parse_state(state): value for state, value in utilities.items()}
