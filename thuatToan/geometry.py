import math
from typing import Dict, Any, List, Tuple

STATUS_OPTIMAL = 0
STATUS_INFEASIBLE = 1
STATUS_UNBOUNDED = 2
STATUS_ERROR = 3

SOL_UNIQUE = 0
SOL_MULTIPLE = 1

EPS = 1e-9

def feasible_point(p, x: float, y: float) -> bool:
    if x < -1e-8 or y < -1e-8:
        return False
    for i in range(len(p.b)):
        v = p.A[i][0] * x + p.A[i][1] * y
        limit = p.b[i]
        sign_val = p.sign[i]
        if sign_val == "<=" and v - limit > 1e-7:
            return False
        if sign_val == ">=" and limit - v > 1e-7:
            return False
        if sign_val == "=" and abs(v - limit) > 1e-7:
            return False
    return True

def feasible_dir(p, dx: float, dy: float) -> bool:
    if dx < -1e-8 or dy < -1e-8:
        return False
    if abs(dx) < EPS and abs(dy) < EPS:
        return False
    for i in range(len(p.b)):
        v = p.A[i][0] * dx + p.A[i][1] * dy
        sign_val = p.sign[i]
        if sign_val == "<=" and v > 1e-8:
            return False
        if sign_val == ">=" and v < -1e-8:
            return False
        if sign_val == "=" and abs(v) > 1e-8:
            return False
    return True

def unbounded_dir_exists(p) -> bool:
    dirs = []
    cc0 = p.c[0] if p.objectiveType == 1 else -p.c[0]
    cc1 = p.c[1] if p.objectiveType == 1 else -p.c[1]
    
    # Check axis directions
    dirs.append((1.0, 0.0))
    dirs.append((0.0, 1.0))
    
    # Check directions parallel to constraints
    for i in range(len(p.b)):
        a, b = p.A[i][0], p.A[i][1]
        dirs.append((b, -a))
        dirs.append((-b, a))
        
    for dx, dy in dirs:
        length = math.sqrt(dx * dx + dy * dy)
        if length < EPS:
            continue
        dx /= length
        dy /= length
        if feasible_dir(p, dx, dy) and (cc0 * dx + cc1 * dy) > 1e-8:
            return True
    return False

def solve_geometry(p) -> Dict[str, Any]:
    sol = {
        "status": STATUS_ERROR,
        "solution_type": SOL_UNIQUE,
        "x": [0.0, 0.0],
        "optimum": 0.0,
        "text": "",
        "intersection_points": [],
        "iteration_log": []
    }
    
    if len(p.c) != 2:
        sol["text"] = "Kết quả: Phương pháp hình học chỉ hỗ trợ 2 biến\n"
        return sol
        
    pts: List[Tuple[float, float]] = []
    
    # 1. Check origin
    if feasible_point(p, 0.0, 0.0):
        pts.append((0.0, 0.0))
        
    # 2. Intersections with axes
    for i in range(len(p.b)):
        a0, a1 = p.A[i][0], p.A[i][1]
        if abs(a1) > EPS:
            y = p.b[i] / a1
            if feasible_point(p, 0.0, y):
                pts.append((0.0, y))
        if abs(a0) > EPS:
            x = p.b[i] / a0
            if feasible_point(p, x, 0.0):
                pts.append((x, 0.0))
                
    # 3. Intersections between constraints
    for i in range(len(p.b)):
        for j in range(i + 1, len(p.b)):
            a1, b1, c1 = p.A[i][0], p.A[i][1], p.b[i]
            a2, b2, c2 = p.A[j][0], p.A[j][1], p.b[j]
            det = a1 * b2 - a2 * b1
            if abs(det) < EPS:
                continue
            x = (c1 * b2 - c2 * b1) / det
            y = (a1 * c2 - a2 * c1) / det
            if feasible_point(p, x, y):
                pts.append((x, y))
                
    # Deduplicate points
    unique_pts: List[Tuple[float, float]] = []
    for pt in pts:
        if not any(abs(pt[0] - u[0]) < 1e-7 and abs(pt[1] - u[1]) < 1e-7 for u in unique_pts):
            unique_pts.append(pt)
            
    sol["intersection_points"] = [{"x": float(pt[0]), "y": float(pt[1])} for pt in unique_pts]
    
    if not unique_pts:
        sol["status"] = STATUS_INFEASIBLE
        sol["text"] = f"Kết quả: Vô nghiệm\nz = {'-∞' if p.objectiveType == 1 else '∞'}\n"
        return sol
        
    if unbounded_dir_exists(p):
        sol["status"] = STATUS_UNBOUNDED
        sol["text"] = f"Kết quả: Không giới nội\nz = {'∞' if p.objectiveType == 1 else '-∞'}\n"
        return sol
        
    best_val = 0.0
    best_pt = (0.0, 0.0)
    best_cnt = 0
    
    # Store iteration log simulating steps (evaluating each vertex)
    simplex_log = []
    for idx, pt in enumerate(unique_pts):
        z = p.c[0] * pt[0] + p.c[1] * pt[1]
        val = z if p.objectiveType == 1 else -z
        
        step_info = {
            "giai_doan": "don_hinh",
            "mo_ta": f"Xét đỉnh {idx + 1}: ({pt[0]:.6g}, {pt[1]:.6g})",
            "bien_vao": f"x1={pt[0]:.6g}",
            "bien_ra": f"x2={pt[1]:.6g}",
            "gia_tri_muc_tieu": float(z),
            "co_so": ["x1", "x2"],
            "basic_indices": [0, 1],
            "nghiem_tam": [float(pt[0]), float(pt[1])],
            "bang": None
        }
        simplex_log.append(step_info)
        
        if idx == 0 or val > best_val + 1e-7:
            best_val = val
            best_pt = pt
            sol["optimum"] = float(z)
            best_cnt = 1
        elif abs(val - best_val) <= 1e-7:
            best_cnt += 1
            
    sol["status"] = STATUS_OPTIMAL
    sol["x"] = [float(best_pt[0]), float(best_pt[1])]
    sol["solution_type"] = SOL_MULTIPLE if best_cnt > 1 else SOL_UNIQUE
    sol["iteration_log"] = simplex_log
    
    status_txt = "Vô số nghiệm tối ưu" if sol["solution_type"] == SOL_MULTIPLE else "Nghiệm tối ưu duy nhất"
    sol["text"] = (
        f"Kết quả: {status_txt}\n"
        f"x1 = {sol['x'][0]:.10g}\n"
        f"x2 = {sol['x'][1]:.10g}\n"
        f"z = {sol['optimum']:.10g}\n"
    )
    return sol
