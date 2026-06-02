import numpy as np
from typing import List, Dict, Any, Tuple
from .expression_eval import eval_expression

# Status constants
STATUS_OPTIMAL = 0
STATUS_INFEASIBLE = 1
STATUS_UNBOUNDED = 2
STATUS_ERROR = 3

SOL_UNIQUE = 0
SOL_MULTIPLE = 1

PIVOT_DANTZIG = 1
PIVOT_BLAND = 2

EPS = 1e-9

class SimplexCoreSolver:
    def __init__(self):
        self.T: np.ndarray = np.zeros((0, 0))
        self.basis: List[int] = []
        self.is_art: List[bool] = []
        self.var_names: List[str] = []
        self.total_vars = 0
        self.art_count = 0
        self.skip_artificial_entering = False
        self.n_orig = 0
        self.m = 0
        self.loai_muc_tieu = "max"
        self.iteration_log: List[Dict[str, Any]] = []
        self.tie_break_leaving = True

    def log_tableau(self, phase_name: str, desc: str, bien_vao: str = "-", bien_ra: str = "-"):
        """Save the current tableau state to the iteration log."""
        tableau_copy = self.T.copy()
        
        # Determine the current basic variable names
        co_so_names = []
        for idx in self.basis:
            if idx < len(self.var_names):
                co_so_names.append(self.var_names[idx])
            else:
                co_so_names.append(f"x{idx + 1}")

        # Prepare table headers and labels
        cols = list(self.var_names) + ["b"]
        rows = co_so_names + ["z" if phase_name in ["pha2", "don_hinh"] else "w"]
                
        # Build matrix values
        matrix_vals = []
        for i in range(self.T.shape[0]):
            matrix_vals.append([float(x) for x in self.T[i]])

        # Calculate nghiem_tam (current basic solution for original variables)
        nghiem_tam = [0.0] * self.n_orig
        for i, idx in enumerate(self.basis):
            if idx < self.n_orig:
                nghiem_tam[idx] = float(self.T[i, -1])

        # Objective value
        obj_val = float(self.T[-1, -1])
        if phase_name == "pha2" or phase_name == "don_hinh":
            obj_val = float(self.T[-1, -1])

        step = {
            "giai_doan": phase_name,
            "mo_ta": desc,
            "bien_vao": bien_vao,
            "bien_ra": bien_ra,
            "gia_tri_muc_tieu": obj_val,
            "co_so": co_so_names,
            "basic_indices": list(self.basis),
            "nghiem_tam": nghiem_tam,
            "bang": {
                "ten_cot": cols,
                "ten_hang": rows,
                "co_so": co_so_names,
                "gia_tri": matrix_vals
            }
        }
        self.iteration_log.append(step)

    def pivot(self, r: int, c: int):
        pv = self.T[r, c]
        self.T[r, :] /= pv
        for i in range(self.T.shape[0]):
            if i == r:
                continue
            f = self.T[i, c]
            if abs(f) > EPS:
                self.T[i, :] -= f * self.T[r, :]
        self.basis[r] = c

    def choose_entering(self, rule: int) -> int:
        best = -1
        most_neg = -EPS
        cols = self.T.shape[1] - 1
        for j in range(cols):
            if self.skip_artificial_entering and self.is_art[j]:
                continue
            if self.T[-1, j] < -EPS:
                if rule == PIVOT_BLAND:
                    return j
                if self.T[-1, j] < most_neg:
                    most_neg = self.T[-1, j]
                    best = j
        return best

    def choose_leaving(self, ent: int, rule: int) -> int:
        best = -1
        best_ratio = 0.0
        cols = self.T.shape[1] - 1
        for i in range(self.m):
            if self.T[i, ent] > EPS:
                ratio = self.T[i, cols] / self.T[i, ent]
                if best < 0 or ratio < best_ratio - EPS or (
                    abs(ratio - best_ratio) <= EPS and self.tie_break_leaving and self.basis[i] < self.basis[best]
                ):
                    best = i
                    best_ratio = ratio
        return best

    def run_simplex(self, rule: int, phase_name: str) -> int:
        iter_count = 0
        cols = self.T.shape[1] - 1
        while iter_count < 10000:
            ent = self.choose_entering(rule)
            if ent < 0:
                return STATUS_OPTIMAL
            lev = self.choose_leaving(ent, rule)
            if lev < 0:
                return STATUS_UNBOUNDED
            
            bien_vao = self.var_names[ent] if ent < len(self.var_names) else f"x{ent + 1}"
            bien_ra = self.var_names[self.basis[lev]] if self.basis[lev] < len(self.var_names) else f"x{self.basis[lev] + 1}"
            
            self.pivot(lev, ent)
            iter_count += 1
            self.log_tableau(phase_name, f"Đổi cơ sở ở bước {iter_count}", bien_vao, bien_ra)
            
        return STATUS_ERROR

    def set_objective_from_costs(self, cost: np.ndarray):
        """Configure the objective row based on the specific cost vector."""
        cols = self.T.shape[1] - 1
        self.T[-1, :] = 0.0
        for j in range(cols):
            self.T[-1, j] = -cost[j]
        for i in range(self.m):
            bv = self.basis[i]
            cb = cost[bv]
            if abs(cb) >= EPS:
                self.T[-1, :] += cb * self.T[i, :]

    def build_tableau(self, p) -> bool:
        self.n_orig = len(p.c)
        self.m = len(p.b)
        self.loai_muc_tieu = p.loai_muc_tieu
        self.basis = [-1] * self.m
        
        # Build variable names and track columns
        self.var_names = [f"x{j + 1}" for j in range(self.n_orig)]
        self.is_art = [False] * self.n_orig
        
        # We need to construct rows for the tableau.
        # Temp structures for Slack, Surplus, and Artificials.
        rows_A = []
        rhs_vals = []
        
        cols_slack_surplus = [] # list of lists, each representing a column
        cols_art = []
        
        slack_surplus_count = 0
        art_count = 0
        
        for i in range(self.m):
            rhs = float(p.b[i])
            sign_val = p.sign[i]
            mult = 1.0
            if rhs < -EPS:
                rhs = -rhs
                mult = -1.0
                if sign_val == "<=":
                    sign_val = ">="
                elif sign_val == ">=":
                    sign_val = "<="
            
            rhs_vals.append(rhs)
            row_coeffs = [mult * float(val) for val in p.A[i]]
            rows_A.append(row_coeffs)
            
            if sign_val == "<=":
                # Add slack column
                slack_surplus_count += 1
                col = [0.0] * self.m
                col[i] = 1.0
                cols_slack_surplus.append((col, f"s{i + 1}"))
                # Basis variable for this row is the slack variable
            elif sign_val == ">=":
                # Add surplus and artificial columns
                slack_surplus_count += 1
                col_s = [0.0] * self.m
                col_s[i] = -1.0
                cols_slack_surplus.append((col_s, f"s{i + 1}"))
                
                art_count += 1
                col_a = [0.0] * self.m
                col_a[i] = 1.0
                cols_art.append((col_a, f"a{i + 1}"))
            elif sign_val == "=":
                # Add artificial column
                art_count += 1
                col_a = [0.0] * self.m
                col_a[i] = 1.0
                cols_art.append((col_a, f"a{i + 1}"))
                
        # Now rebuild self.var_names and self.is_art in order:
        # 1. Original variables: x1, x2, ...
        # 2. Slack/surplus columns
        # 3. Artificial columns
        
        columns = [np.array([rows_A[i][j] for i in range(self.m)]) for j in range(self.n_orig)]
        
        # Add slack/surplus columns
        for col, name in cols_slack_surplus:
            self.var_names.append(name)
            self.is_art.append(False)
            columns.append(np.array(col))
            
        # Add artificial columns
        for col, name in cols_art:
            self.var_names.append(name)
            self.is_art.append(True)
            columns.append(np.array(col))
            
        self.total_vars = len(self.var_names)
        self.art_count = art_count
        
        # Build T matrix: m + 1 rows, total_vars + 1 columns
        self.T = np.zeros((self.m + 1, self.total_vars + 1))
        for j, col in enumerate(columns):
            self.T[:-1, j] = col
        self.T[:-1, -1] = rhs_vals
        
        # Set basis
        # Find which column corresponds to basis variable for each row
        # For each row i:
        # - if sign was <=: slack column i has 1.0 in row i, others 0. It is in basis.
        # - if sign was >=: artificial column has 1.0 in row i, others 0. It is in basis.
        # - if sign was =: artificial column has 1.0 in row i, others 0. It is in basis.
        slack_surplus_idx = self.n_orig
        art_idx = self.n_orig + len(cols_slack_surplus)
        
        slack_surplus_counter = 0
        art_counter = 0
        
        for i in range(self.m):
            sign_val = p.sign[i]
            rhs = float(p.b[i])
            if rhs < -EPS:
                if sign_val == "<=":
                    sign_val = ">="
                elif sign_val == ">=":
                    sign_val = "<="
                    
            if sign_val == "<=":
                self.basis[i] = slack_surplus_idx + slack_surplus_counter
                slack_surplus_counter += 1
            elif sign_val == ">=":
                slack_surplus_counter += 1  # skip surplus column, it's not in basis
                self.basis[i] = art_idx + art_counter
                art_counter += 1
            elif sign_val == "=":
                self.basis[i] = art_idx + art_counter
                art_counter += 1
                
        return True

    def get_solution_dict(self, p) -> Dict[str, Any]:
        xs = [0.0] * self.n_orig
        for i in range(self.m):
            bv = self.basis[i]
            if bv < self.n_orig:
                xs[bv] = float(self.T[i, -1])
                
        opt = 0.0
        for j in range(self.n_orig):
            opt += p.c[j] * xs[j]
            
        return {
            "status": STATUS_OPTIMAL,
            "x": xs,
            "optimum": opt
        }

    def has_multiple(self) -> bool:
        cols = self.T.shape[1] - 1
        for j in range(self.n_orig):
            if j not in self.basis and abs(self.T[-1, j]) <= 1e-7:
                return True
        return False

    def solve(self, p, pivot_rule: int, tie_break_leaving: bool = True) -> Dict[str, Any]:
        self.iteration_log = []
        self.tie_break_leaving = tie_break_leaving
        if not self.build_tableau(p):
            return {"status": STATUS_ERROR, "text": "Lỗi: Không thể dựng bảng đơn hình\n"}
            
        # Initial tableau logging
        self.log_tableau("pha1" if self.art_count > 0 else "don_hinh", "Bảng đơn hình ban đầu")
        
        # Phase 1
        if self.art_count > 0:
            cost = np.zeros(self.total_vars)
            for j in range(self.total_vars):
                cost[j] = -1.0 if self.is_art[j] else 0.0
            self.set_objective_from_costs(cost)
            self.skip_artificial_entering = False
            
            # Log objective update for Phase 1
            self.log_tableau("pha1", "Thiết lập hàm mục tiêu phụ cho pha 1")
            
            st = self.run_simplex(pivot_rule, "pha1")
            if st != STATUS_OPTIMAL or self.T[-1, -1] < -1e-7:
                return {
                    "status": STATUS_INFEASIBLE,
                    "iteration_log": self.iteration_log,
                    "text": f"Kết quả: Vô nghiệm\nz = {'-∞' if p.objectiveType == 1 else '∞'}\n"
                }
                
            # Drive remaining artificials out of basis if any
            for i in range(self.m):
                if self.is_art[self.basis[i]]:
                    entering = -1
                    for j in range(self.total_vars):
                        if not self.is_art[j] and abs(self.T[i, j]) > EPS:
                            entering = j
                            break
                    if entering >= 0:
                        self.pivot(i, entering)
                        self.log_tableau("pha1", f"Đẩy biến giả ra khỏi cơ sở tại hàng {i + 1}")
                        
        # Phase 2
        cost = np.zeros(self.total_vars)
        for j in range(self.n_orig):
            cost[j] = p.c[j] if p.objectiveType == 1 else -p.c[j]
            
        self.set_objective_from_costs(cost)
        self.skip_artificial_entering = True
        
        # Log objective update for Phase 2
        self.log_tableau("pha2" if self.art_count > 0 else "don_hinh", "Thiết lập hàm mục tiêu chính")
        
        st = self.run_simplex(pivot_rule, "pha2" if self.art_count > 0 else "don_hinh")
        self.skip_artificial_entering = False
        
        if st == STATUS_UNBOUNDED:
            return {
                "status": STATUS_UNBOUNDED,
                "iteration_log": self.iteration_log,
                "text": f"Kết quả: Không giới nội\nz = {'∞' if p.objectiveType == 1 else '-∞'}\n"
            }
        elif st != STATUS_OPTIMAL:
            return {
                "status": STATUS_ERROR,
                "iteration_log": self.iteration_log,
                "text": "Kết quả: Lỗi không thể giải\n"
            }
            
        # Success! Read solution
        sol = self.get_solution_dict(p)
        sol["iteration_log"] = self.iteration_log
        is_multiple = self.has_multiple()
        sol["solution_type"] = SOL_MULTIPLE if is_multiple else SOL_UNIQUE
        
        # Format text output
        lines = []
        status_txt = "Vô số nghiệm tối ưu" if is_multiple else "Nghiệm tối ưu duy nhất"
        lines.append(f"Kết quả: {status_txt}")
        for j in range(self.n_orig):
            lines.append(f"x{j + 1} = {sol['x'][j]:.10g}")
        lines.append(f"z = {sol['optimum']:.10g}")
        sol["text"] = "\n".join(lines) + "\n"
        
        return sol
