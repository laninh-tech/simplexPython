import numpy as np
from typing import List, Dict, Any, Union
from .dantzig import solve_dantzig
from .bland import solve_bland
from .two_phase import solve_two_phase
from .geometry import solve_geometry

# Method Constants
METHOD_GEOMETRY = 0
METHOD_DANTZIG = 1
METHOD_BLAND = 2
METHOD_TWO_PHASE = 3

# Sign Constants
SIGN_LE = 0
SIGN_GE = 1
SIGN_EQ = 2

# Variable Sign Constants
VAR_NONNEG = 0
VAR_NONPOS = 1
VAR_FREE = 2

# Objective Constants
OBJ_MAX = 1
OBJ_MIN = 2

class LPProblem:
    def __init__(
        self,
        n: int,
        m: int,
        objectiveType: int,
        c: List[float],
        A: List[List[float]],
        b: List[float],
        sign: List[Union[int, str]],
        varSign: List[Union[int, str]]
    ):
        self.n = n
        self.m = m
        self.objectiveType = objectiveType  # 1 for MAX, 2 for MIN
        self.c = list(c)
        self.A = [list(row) for row in A]
        self.b = list(b)
        
        # Standardize constraint signs to strings
        self.sign = []
        for s in sign:
            if s == SIGN_LE or s == "<=":
                self.sign.append("<=")
            elif s == SIGN_GE or s == ">=":
                self.sign.append(">=")
            elif s == SIGN_EQ or s == "=":
                self.sign.append("=")
            else:
                self.sign.append(str(s))
                
        # Standardize variable signs to integers
        self.varSign = []
        for vs in varSign:
            if vs == VAR_NONNEG or vs == ">=0":
                self.varSign.append(VAR_NONNEG)
            elif vs == VAR_NONPOS or vs == "<=0":
                self.varSign.append(VAR_NONPOS)
            elif vs == VAR_FREE or vs == "free":
                self.varSign.append(VAR_FREE)
            else:
                self.varSign.append(int(vs))

    @property
    def loai_muc_tieu(self) -> str:
        return "max" if self.objectiveType == OBJ_MAX else "min"

class VarMap:
    def __init__(self, size: int):
        self.plusIndex = [-1] * size
        self.minusIndex = [-1] * size

def has_free_var(p: LPProblem) -> bool:
    return any(vs == VAR_FREE for vs in p.varSign)

def has_nonstandard_var(p: LPProblem) -> bool:
    return any(vs == VAR_NONPOS or vs == VAR_FREE for vs in p.varSign)

def transform_problem(p: LPProblem) -> tuple:
    """Transform free and non-positive variables into standard non-negative variables."""
    q_c = []
    q_A = [[] for _ in range(p.m)]
    var_map = VarMap(p.n)
    
    k = 0
    for j in range(p.n):
        vs = p.varSign[j]
        if vs == VAR_NONNEG:
            var_map.plusIndex[j] = k
            q_c.append(p.c[j])
            for i in range(p.m):
                q_A[i].append(p.A[i][j])
            k += 1
        elif vs == VAR_NONPOS:
            var_map.minusIndex[j] = k
            q_c.append(-p.c[j])
            for i in range(p.m):
                q_A[i].append(-p.A[i][j])
            k += 1
        elif vs == VAR_FREE:
            var_map.plusIndex[j] = k
            q_c.append(p.c[j])
            for i in range(p.m):
                q_A[i].append(p.A[i][j])
            k += 1
            
            var_map.minusIndex[j] = k
            q_c.append(-p.c[j])
            for i in range(p.m):
                q_A[i].append(-p.A[i][j])
            k += 1
            
    q = LPProblem(
        n=k,
        m=p.m,
        objectiveType=p.objectiveType,
        c=q_c,
        A=q_A,
        b=p.b,
        sign=p.sign,
        varSign=[VAR_NONNEG] * k
    )
    return q, var_map

def recover_original_solution(p: LPProblem, var_map: VarMap, tmp_sol: Dict[str, Any]) -> Dict[str, Any]:
    """Translate standard form solution back to original problem variables."""
    sol = dict(tmp_sol)
    if tmp_sol["status"] != 0: # not STATUS_OPTIMAL
        return sol
        
    orig_x = [0.0] * p.n
    for j in range(p.n):
        val = 0.0
        vs = p.varSign[j]
        if vs == VAR_NONPOS:
            idx = var_map.minusIndex[j]
            if idx >= 0:
                val = -tmp_sol["x"][idx]
        elif vs == VAR_FREE:
            idx_plus = var_map.plusIndex[j]
            idx_minus = var_map.minusIndex[j]
            if idx_plus >= 0:
                val += tmp_sol["x"][idx_plus]
            if idx_minus >= 0:
                val -= tmp_sol["x"][idx_minus]
        else:
            idx = var_map.plusIndex[j]
            if idx >= 0:
                val = tmp_sol["x"][idx]
                
        if abs(val) < 1e-9:
            val = 0.0
        orig_x[j] = val
        
    sol["x"] = orig_x
    opt = 0.0
    for j in range(p.n):
        opt += p.c[j] * orig_x[j]
    sol["optimum"] = opt
    
    # Formulate nice solution text representation
    lines = []
    if has_free_var(p):
        status_txt = "Một nghiệm tối ưu"
    else:
        status_txt = "Vô số nghiệm tối ưu" if tmp_sol.get("solution_type") == 1 else "Nghiệm tối ưu duy nhất"
        
    lines.append(f"Kết quả: {status_txt}")
    for j in range(p.n):
        lines.append(f"x{j + 1} = {orig_x[j]:.10g}")
    lines.append(f"z = {opt:.10g}")
    sol["text"] = "\n".join(lines) + "\n"
    
    return sol

def solve_lp(p: LPProblem, method: int) -> Dict[str, Any]:
    """Coordinate solving of LP problem, handling variables transformations."""
    if not has_nonstandard_var(p):
        if method == METHOD_GEOMETRY:
            return solve_geometry(p)
        elif method == METHOD_DANTZIG:
            return solve_dantzig(p)
        elif method == METHOD_BLAND:
            return solve_bland(p)
        elif method == METHOD_TWO_PHASE:
            return solve_two_phase(p)
        else:
            return {"status": 3, "text": "Lỗi: Không tìm thấy phương pháp giải hợp lệ\n"}
            
    if method == METHOD_GEOMETRY:
        return {
            "status": 3,
            "text": "Kết quả: Phương pháp hình học chỉ hỗ trợ các biến x >= 0\n"
        }
        
    # Transform problem to positive variables only
    q, var_map = transform_problem(p)
    
    if method == METHOD_DANTZIG:
        tmp_sol = solve_dantzig(q)
    elif method == METHOD_BLAND:
        tmp_sol = solve_bland(q)
    elif method == METHOD_TWO_PHASE:
        tmp_sol = solve_two_phase(q)
    else:
        return {"status": 3, "text": "Lỗi: Không tìm thấy phương pháp giải hợp lệ\n"}
        
    return recover_original_solution(p, var_map, tmp_sol)
