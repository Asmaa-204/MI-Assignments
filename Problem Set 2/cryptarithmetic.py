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
        # All unique letters
        letters = set(LHS0 + LHS1 + RHS)
        for l in letters:
            problem.variables.append(l)
            problem.domains[l] = set(range(10))

        # Add uniqueness constraints (all letters must have different digits)
        letter_list = list(letters)
        for i in range(len(letter_list)):
            for j in range(i + 1, len(letter_list)):
                l1, l2 = letter_list[i], letter_list[j]
                problem.constraints.append(BinaryConstraint((l1, l2), lambda a, b: a != b))

        # Carry variables
        n = len(RHS)
        carries = [f"c{i}" for i in range(n)]
        for c in carries:
            problem.variables.append(c)
            problem.domains[c] = {0, 1}

        # Pad LHS numbers with '0' (just for alignment, don't treat '0' as variable)
        L0 = LHS0.rjust(n, "0")
        L1 = LHS1.rjust(n, "0")

        # Add unary constraints for leading digits (cannot be zero)
        if len(LHS0) > 1:
            problem.constraints.append(
                UnaryConstraint(LHS0[0], lambda val, l=LHS0[0]: val != 0)
            )
        if len(LHS1) > 1:
            problem.constraints.append(
                UnaryConstraint(LHS1[0], lambda val, l=LHS1[0]: val != 0)
            )
        if len(RHS) > 1:
            problem.constraints.append(
                UnaryConstraint(RHS[0], lambda val, l=RHS[0]: val != 0)
            )

        # --- Column-wise tuple variables for sums ---
        ps = [f"p{i}" for i in range(n)]
        for i in range(n):
            lhs0 = L0[-1 - i]
            lhs1 = L1[-1 - i]
            rhs = RHS[-1 - i]

            cin = carries[i]
            cout = carries[i + 1] if i + 1 < n else None
            p = ps[i]

            problem.variables.append(p)
            # Domain: all possible combinations of (lhs0_digit, lhs1_digit, carry_in)
            problem.domains[p] = [
                (a, b, c) for a in range(10) for b in range(10) for c in range(2)
            ]

            # Connect tuple inputs to real variables
            problem.constraints.append(
                BinaryConstraint(
                    (p, lhs0), lambda p_val, lhs0_val, l=lhs0: p_val[0] == lhs0_val
                )
            )
            problem.constraints.append(
                BinaryConstraint(
                    (p, lhs1), lambda p_val, lhs1_val, l=lhs1: p_val[1] == lhs1_val
                )
            )
            problem.constraints.append(
                BinaryConstraint(
                    (p, cin), lambda p_val, cin_val, c=cin: p_val[2] == cin_val
                )
            )

            # Connect tuple outputs
            problem.constraints.append(
                BinaryConstraint(
                    (p, rhs),
                    lambda p_val, rhs_val: rhs_val == (p_val[0] + p_val[1] + p_val[2]) % 10,
                )
            )
            if cout:
                problem.constraints.append(
                    BinaryConstraint(
                        (p, cout),
                        lambda p_val, cout_val: cout_val
                        == (p_val[0] + p_val[1] + p_val[2]) // 10,
                    )
                )
                
            if lhs0 == "0":
                problem.constraints.append(UnaryConstraint(p, lambda p_val: p_val[0] == 0))
            if lhs1 == "0":
                problem.constraints.append(UnaryConstraint(p, lambda p_val: p_val[1] == 0))
            if i == "0":
                problem.constraints.append(UnaryConstraint(p, lambda p_val: p_val[2] == 0))
            

        return problem

    # Read a cryptarithmetic puzzle from a file
    @staticmethod
    def from_file(path: str) -> "CryptArithmeticProblem":
        with open(path, 'r') as f:
            return CryptArithmeticProblem.from_text(f.read())
