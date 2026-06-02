from typing import List
from ..thuatToan.lp_solver import LPProblem, VAR_NONPOS, VAR_FREE, OBJ_MAX

EPS = 1e-9

def _term(a: float, j: int, first: bool) -> str:
    if abs(a) < EPS:
        return ""
    if first:
        dau = "-" if a < 0 else ""
    else:
        dau = " + " if a >= 0 else " - "
    
    val_str = ""
    if abs(abs(a) - 1.0) > EPS:
        val_str = f"{abs(a):.6g}"
        
    return f"{dau}{val_str}x{j + 1}"

def build_initial_vocabulary(p: LPProblem) -> str:
    """Generate the starting dictionary text representation matching vocabulary.c."""
    lines = []
    lines.append("Từ vựng xuất phát:")
    
    # 1. z equation
    z_parts = []
    first = True
    for j in range(p.n):
        c = p.c[j] if p.objectiveType == OBJ_MAX else -p.c[j]
        term_str = _term(c, j, first)
        if term_str:
            z_parts.append(term_str)
            first = False
            
    z_expr = "".join(z_parts) if z_parts else "0"
    lines.append(f"z = {z_expr}")
    
    # 2. Slack/Surplus equations (represented as W_i)
    for i in range(p.m):
        row_parts = [f"W{i + 1} = {p.b[i]:.6g}"]
        for j in range(p.n):
            a = -p.A[i][j]
            term_str = _term(a, j, False)
            if term_str:
                row_parts.append(term_str)
        lines.append("".join(row_parts))
        
    # 3. Variable bounds
    lines.append("")
    lines.append("Ràng buộc dấu:")
    for j in range(p.n):
        if p.varSign[j] == VAR_NONPOS:
            lines.append(f"x{j + 1} <= 0")
        elif p.varSign[j] == VAR_FREE:
            lines.append(f"x{j + 1} tự do")
        else:
            lines.append(f"x{j + 1} >= 0")
            
    for i in range(p.m):
        lines.append(f"W{i + 1} >= 0")
        
    return "\r\n".join(lines) + "\r\n"
