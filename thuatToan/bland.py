from .simplex_core import SimplexCoreSolver, PIVOT_BLAND

def solve_bland(p):
    """Solve LP problem using Bland's rule."""
    solver = SimplexCoreSolver()
    return solver.solve(p, PIVOT_BLAND, tie_break_leaving=True)
