from typing import Tuple
import re
from CSP import Assignment, Problem, UnaryConstraint, BinaryConstraint

# TODO (Optional): Import any builtin library or define any helper function you want to use

# This is a class to define for cryptarithmetic puzzles as CSPs
class CryptArithmeticProblem(Problem):
    LHS: Tuple[str, str]
    RHS: str

    # Convert an assignment into a string (so that is can be printed).
    def format_assignment(self, assignment: Assignment) -> str:
        LHS0, LHS1 = self.LHS
        RHS = self.RHS
        letters = set(LHS0 + LHS1 + RHS)
        formula = f"{LHS0} + {LHS1} = {RHS}"
        postfix = []
        valid_values = list(range(10))
        for letter in letters:
            value = assignment.get(letter)
            if value is None: continue
            if value not in valid_values:
                postfix.append(f"{letter}={value}")
            else:
                formula = formula.replace(letter, str(value))
        if postfix:
            formula = formula + " (" + ", ".join(postfix) +  ")" 
        return formula

    @staticmethod
    def from_text(text: str) -> 'CryptArithmeticProblem':
        # Given a text in the format "LHS0 + LHS1 = RHS", the following regex
        # matches and extracts LHS0, LHS1 & RHS
        # For example, it would parse "SEND + MORE = MONEY" and extract the
        # terms such that LHS0 = "SEND", LHS1 = "MORE" and RHS = "MONEY"
        pattern = r"\s*([a-zA-Z]+)\s*\+\s*([a-zA-Z]+)\s*=\s*([a-zA-Z]+)\s*"
        match = re.match(pattern, text)
        if not match: raise Exception("Failed to parse:" + text)
        LHS0, LHS1, RHS = [match.group(i+1).upper() for i in range(3)]

        problem = CryptArithmeticProblem()
        problem.LHS = (LHS0, LHS1)
        problem.RHS = RHS

        # TODO Edit and complete the rest of this function
        # problem.variables:    should contain a list of variables where each variable is string (the variable name)
        # problem.domains:      should be dictionary that maps each variable (str) to its domain (set of values)
        #                       For the letters, the domain can only contain integers in the range [0,9].
        # problem.constaints:   should contain a list of constraint (either unary or binary constraints).

        problem.variables = []
        problem.domains = {}
        problem.constraints = []

        # add all unique letters to variables with domain 0->9
        letters = sorted(set(LHS0 + LHS1 + RHS))
        problem.variables = list(letters)
        problem.domains = {l: list(range(10)) for l in letters}

        # uniqueness constraints (all letters values' have to be unique)
        letters = list(letters)
        for i in range(len(letters)):
            for j in range(i + 1, len(letters)):
                problem.constraints.append(
                    BinaryConstraint((letters[i], letters[j]), lambda a, b: a != b)
                )

        # add auxiliary carry variables with domain of 0 or 1
        n = len(RHS)
        carries = [f"c{i}" for i in range(n)]
        for c in carries:
            problem.variables.append(c)
            problem.domains[c] = [0, 1]

        # pad LHS numbers with 0's on the left for alignment
        L0, L1 = LHS0.rjust(n, "0"), LHS1.rjust(n, "0")

        # left most digits can't be zero
        for word in (LHS0, LHS1, RHS):
            if len(word) > 1:
                problem.constraints.append(UnaryConstraint(word[0], lambda val: val != 0))

        # column-wise sum tuples
        # add new auxiliary variables for each constrain lhs0 + lhs1 + cin = rhs + cout
        # where p is a tuple contains (lhs0, lhs1, cin)
        ps = [f"p{i}" for i in range(n)]
        for i in range(n):
            # start from rigth
            lhs0, lhs1, rhs = L0[-1 - i], L1[-1 - i], RHS[-1 - i]
            cin, cout = carries[i], carries[i + 1] if i + 1 < n else None
            p = ps[i]

            problem.variables.append(p)
            problem.domains[p] = [
                (a, b, c) for a in range(10) for b in range(10) for c in range(2)
            ]

            # Connect tuple inputs
            problem.constraints += [
                BinaryConstraint( (p, lhs0), lambda p_val, lhs0_val: p_val[0] == lhs0_val ), 
                BinaryConstraint( (p, lhs1), lambda p_val, lhs1_val: p_val[1] == lhs1_val ), 
                BinaryConstraint( (p, cin), lambda p_val, cin_val: p_val[2] == cin_val )
            ]

            # output constraints
            problem.constraints.append(BinaryConstraint((p, rhs), lambda pv, rv: rv == (pv[0] + pv[1] + pv[2]) % 10))
            problem.constraints.append(BinaryConstraint((p, cout), lambda pv, cv: cv == (pv[0] + pv[1] + pv[2]) // 10))
            # most significant column must not produce a carry
            if i == n - 1: problem.constraints.append(UnaryConstraint(p, lambda pv: (pv[0] + pv[1] + pv[2]) < 10))
            # ensure the first carry_in is 0
            if i == 0: problem.constraints.append(UnaryConstraint(p, lambda p_val: p_val[2] == 0))

            # if either lhs0 or lhs1 is "0" -> add its unary constraint to the corresponding variable in p
            if lhs0 == "0": problem.constraints.append(UnaryConstraint(p, lambda p_val: p_val[0] == 0))
            if lhs1 == "0": problem.constraints.append(UnaryConstraint(p, lambda p_val: p_val[1] == 0))

        return problem

    # Read a cryptarithmetic puzzle from a file
    @staticmethod
    def from_file(path: str) -> "CryptArithmeticProblem":
        with open(path, 'r') as f:
            return CryptArithmeticProblem.from_text(f.read())
        