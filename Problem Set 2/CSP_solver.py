from typing import Any, Dict, List, Optional
from CSP import Assignment, BinaryConstraint, Problem, UnaryConstraint
from helpers.utils import NotImplemented


# This function applies 1-Consistency to the problem.
# In other words, it modifies the domains to only include values that satisfy their variables' unary constraints.
# Then all unary constraints are removed from the problem (they are no longer needed).
# The function returns False if any domain becomes empty. Otherwise, it returns True.
def one_consistency(problem: Problem) -> bool:
    remaining_constraints = []
    solvable = True
    for constraint in problem.constraints:
        if not isinstance(constraint, UnaryConstraint):
            remaining_constraints.append(constraint)
            continue
        variable = constraint.variable
        new_domain = {
            value for value in problem.domains[variable] if constraint.condition(value)
        }
        if not new_domain:
            solvable = False
        problem.domains[variable] = new_domain
    problem.constraints = remaining_constraints
    return solvable


# This function returns the variable that should be picked based on the MRV heuristic.
# NOTE: We don't use the domains inside the problem, we use the ones given by the "domains" argument
#       since they contain the current domains of unassigned variables only.
# NOTE: If multiple variables have the same priority given the MRV heuristic,
#       we order them in the same order in which they appear in "problem.variables".
def minimum_remaining_values(problem: Problem, domains: Dict[str, set]) -> str:
    _, _, variable = min(
        (len(domains[variable]), index, variable)
        for index, variable in enumerate(problem.variables)
        if variable in domains
    )
    return variable


# This function should implement forward checking
# The function is given the problem, the variable that has been assigned and its assigned value and the domains of the unassigned values
# The function should return False if it is impossible to solve the problem after the given assignment, and True otherwise.
# In general, the function should do the following:
#   - For each binary constraints that involve the assigned variable:
#       - Get the other involved variable.
#       - If the other variable has no domain (in other words, it is already assigned), skip this constraint.
#       - Update the other variable's domain to only include the values that satisfy the binary constraint with the assigned variable.
#   - If any variable's domain becomes empty, return False. Otherwise, return True.
# IMPORTANT: Don't use the domains inside the problem, use and modify the ones given by the "domains" argument
#            since they contain the current domains of unassigned variables only.
def forward_checking(
    problem: Problem,
    assigned_variable: str,
    assigned_value: Any,
    domains: Dict[str, set],
) -> bool:
    # TODO: Write this function
    # For each binary constraints that involve the assigned variable:
    for constraint in problem.constraints:
        # only consider binary constraints involving the assigned variable
        if (
            not isinstance(constraint, BinaryConstraint)
            or assigned_variable not in constraint.variables
        ):
            continue

        # get the other variable in the constraint
        other_var = constraint.get_other(assigned_variable)

        # if other_var is already assigned (not in domains), skip it
        if other_var not in domains:
            continue

        # filter domain of the other variable
        new_domain = set()
        for value in domains[other_var]:
            # Check if the constraint is satisfied when assigned_variable is assigned_value
            if constraint.is_satisfied(
                {assigned_variable: assigned_value, other_var: value}
            ):
                new_domain.add(value)

        # if domain becomes empty, failure
        if not new_domain:
            return False

        # update domain
        domains[other_var] = new_domain

    return True


# This function should return the domain of the given variable order based on the "least restraining value" heuristic.
# IMPORTANT: This function should not modify any of the given arguments.
# Generally, this function is very similar to the forward checking function, but it differs as follows:
#   - You are not given a value for the given variable, since you should do the process for every value in the variable's
#     domain to see how much it will restrain the neigbors domain
#   - Here, you do not modify the given domains. But you can create and modify a copy.
# IMPORTANT: If multiple values have the same priority given the "least restraining value" heuristic,
#            order them in ascending order (from the lowest to the highest value).
# IMPORTANT: Don't use the domains inside the problem, use and modify the ones given by the "domains" argument
#            since they contain the current domains of unassigned variables only.
def least_restraining_values(
    problem: Problem, variable_to_assign: str, domains: Dict[str, set]
) -> List[Any]:
    # TODO: Write this function
    # only consider binary constraints involving the assigned variable
    relatet_constraints = [
        c
        for c in problem.constraints
        if isinstance(c, BinaryConstraint) and variable_to_assign in c.variables
    ]

    # a dict of (value, number of allowed remaining values in neighbor variables)
    remaining_values = {}

    # loop for each value in the domain of the variable to assign
    for value in domains.get(variable_to_assign, set()):
        # get the remaining domain elements due to this assignment
        new_domain_len = 0
        # how many choices remain for neighbors if we assign 'value'
        for constraint in relatet_constraints:
            other_var = constraint.get_other(variable_to_assign)
            for other_val in domains.get(other_var, set()):
                if constraint.is_satisfied(
                    {variable_to_assign: value, other_var: other_val}
                ):
                    new_domain_len += 1
        remaining_values[value] = new_domain_len

    # sort values from least to most constraining
    # in case of tie, sort by values asc
    ordered_values = sorted(
        remaining_values.keys(), key=lambda v: (-remaining_values[v], v),
    )

    return ordered_values


# This function should solve CSP problems using backtracking search with forward checking.
# The variable ordering should be decided by the MRV heuristic.
# The value ordering should be decided by the "least restraining value" heurisitc.
# Unary constraints should be handled using 1-Consistency before starting the backtracking search.
# This function should return the first solution it finds (a complete assignment that satisfies the problem constraints).
# If no solution was found, it should return None.
# IMPORTANT: To get the correct result for the explored nodes, you should check if the assignment is complete only once using "problem.is_complete"
#            for every assignment including the initial empty assignment, EXCEPT for the assignments pruned by the forward checking.
#            Also, if 1-Consistency deems the whole problem unsolvable, you shouldn't call "problem.is_complete" at all.
from copy import deepcopy

def solve(problem: Problem) -> Optional[Assignment]:
    # if 1-Consistency deems the whole problem unsolvable, return failure
    if not one_consistency(problem):
        return None

    def backtrack(problem: Problem, assignment: Dict[str, any], domains: Dict[str, set]):
        # check if the assinment is complete
        if problem.is_complete(assignment):
            return assignment

        # choose the variable based on MRV
        assigned_var = minimum_remaining_values(problem, domains)
        # choose the value for the chosen variable based on least constraining value
        ordered_values = least_restraining_values(problem, assigned_var, domains)
        for value in ordered_values:
            # make the assignment
            assignment[assigned_var] = value
            # remove the current assigned var from the domain
            new_domains = deepcopy(domains)
            del new_domains[assigned_var]

            # forward check given new domains
            # this will remove the invalid domains from neighbors due this assignment if the assignment is valid
            valid_assignment = forward_checking(problem, assigned_var, value, new_domains)
            # if this assignment is valid, make it and backtrack
            if valid_assignment:
                result = backtrack(problem, assignment, new_domains)
                # if this sequence of assignments return a solution, return it
                if result is not None:
                    return result
            # not a valid assignment
            del assignment[assigned_var]
        # if no values can be assigned for the variable, return failure
        return None

    intial_domains = deepcopy(problem.domains)
    return backtrack(problem, {}, intial_domains)
