from .simplex_core import SimplexCoreSolver, PIVOT_DANTZIG

def solve_two_phase(p):
    """Solve LP problem using Two Phase method."""
    solver = SimplexCoreSolver()
    return solver.solve(p, PIVOT_DANTZIG, tie_break_leaving=True)
