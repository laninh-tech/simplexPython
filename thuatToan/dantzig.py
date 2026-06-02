from .simplex_core import SimplexCoreSolver, PIVOT_DANTZIG

def solve_dantzig(p):
    """Solve LP problem using Dantzig's rule."""
    solver = SimplexCoreSolver()
    return solver.solve(p, PIVOT_DANTZIG, tie_break_leaving=False)
