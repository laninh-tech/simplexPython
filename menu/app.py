import os
import re
from flask import Flask, jsonify, render_template, request
import numpy as np
try:
    from ..thuatToan.lp_solver import LPProblem, solve_lp, OBJ_MAX, OBJ_MIN
    from ..thuatToan.expression_eval import eval_expression
    from ..tuVung.vocabulary import build_initial_vocabulary
except (ImportError, ValueError):
    from thuatToan.lp_solver import LPProblem, solve_lp, OBJ_MAX, OBJ_MIN
    from thuatToan.expression_eval import eval_expression
    from tuVung.vocabulary import build_initial_vocabulary


_template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
app = Flask(__name__, template_folder=_template_dir)
app.config["TEMPLATES_AUTO_RELOAD"] = True

UI_BUILD = ""

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"success": True}), 200

@app.route("/")
def index():
    response = app.make_response(render_template("index.html"))
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/api/version", methods=["GET"])
def version():
    return jsonify({"success": True}), 200

def _parse_problem_payload(data) -> tuple:
    """Parse problem parameters, evaluating math expressions for coefficients."""
    loai_muc_tieu = data.get("loai_muc_tieu", "max").lower()
    obj_type = OBJ_MAX if loai_muc_tieu == "max" else OBJ_MIN
    
    he_so_raw = data.get("he_so_muc_tieu", [])
    A_raw = data.get("A", [])
    b_raw = data.get("b", [])
    dau_rang_buoc = data.get("dau_rang_buoc", [])
    rang_buoc_bien = data.get("rang_buoc_bien", [])
    ten_bien = data.get("ten_bien", [])
    
    # 1. Tính toán các hệ số hàm mục tiêu
    he_so_muc_tieu = []
    for idx, item in enumerate(he_so_raw):
        try:
            val = eval_expression(str(item))
            he_so_muc_tieu.append(val)
        except Exception as e:
            return None, f"Lỗi biểu thức c{idx+1} ('{item}'): {str(e)}"
            
    # 2. Tính toán ma trận hệ số ràng buộc A
    A = []
    for r_idx, row in enumerate(A_raw):
        A_row = []
        for c_idx, item in enumerate(row):
            try:
                val = eval_expression(str(item))
                A_row.append(val)
            except Exception as e:
                return None, f"Lỗi biểu thức hệ số A dòng {r_idx+1} cột {c_idx+1} ('{item}'): {str(e)}"
        A.append(A_row)
        
    # 3. Tính toán vế phải b
    b = []
    for idx, item in enumerate(b_raw):
        try:
            val = eval_expression(str(item))
            b.append(val)
        except Exception as e:
            return None, f"Lỗi biểu thức vế phải b{idx+1} ('{item}'): {str(e)}"
            
    n = len(he_so_muc_tieu)
    m = len(A)
    
    if n == 0:
        return None, "Phải nhập hệ số hàm mục tiêu"
    if m == 0:
        return None, "Phải nhập ít nhất một ràng buộc"
    if len(A[0]) != n:
        return None, "Số lượng biến trong ràng buộc không khớp với hàm mục tiêu"
    if len(b) != m:
        return None, "Số lượng ràng buộc không khớp với vế phải"
    if len(dau_rang_buoc) != m:
        return None, "Số lượng dấu ràng buộc không khớp"
    if len(rang_buoc_bien) != n:
        return None, "Số lượng điều kiện biến không khớp"
        
    if not ten_bien or len(ten_bien) != n:
        ten_bien = [f"x{i+1}" for i in range(n)]
        
    problem = LPProblem(
        n=n,
        m=m,
        objectiveType=obj_type,
        c=he_so_muc_tieu,
        A=A,
        b=b,
        sign=dau_rang_buoc,
        varSign=rang_buoc_bien
    )
    return problem, None

@app.route("/api/vocabulary", methods=["POST"])
def get_vocabulary():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Không nhận được dữ liệu JSON hợp lệ"}), 400
    problem, err = _parse_problem_payload(data)
    if err:
        return jsonify({"error": err}), 400
    vocab = build_initial_vocabulary(problem)
    return jsonify({"success": True, "tu_vung": vocab}), 200

@app.route("/api/solve", methods=["POST"])
def solve():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Không nhận được dữ liệu JSON hợp lệ"}), 400
        
    problem, err = _parse_problem_payload(data)
    if err:
        return jsonify({"error": err}), 400
        
    method = int(data.get("method", 3))  # Mặc định sử dụng Simplex Hai Pha (value = 3)
    
    try:
        # Giải bài toán quy hoạch tuyến tính
        sol = solve_lp(problem, method)
        
        # Tạo chuỗi biểu diễn từ vựng xuất phát
        vocab = build_initial_vocabulary(problem)
        
        # Dựng gói dữ liệu trả về cho client
        # Định dạng vector nghiệm sang dạng list thông thường
        x_sol = [float(val) for val in sol.get("x", [])]
        opt_val = float(sol.get("optimum", 0.0))
        
        response_data = {
            "success": True,
            "status": sol["status"],
            "tu_vung": vocab,
            "ket_qua_text": sol["text"],
            "intersection_points": sol.get("intersection_points", []),
            "problem": {
                "loai_muc_tieu": problem.loai_muc_tieu,
                "he_so_muc_tieu": problem.c,
                "A": problem.A,
                "b": problem.b,
                "dau_rang_buoc": problem.sign,
                "rang_buoc_bien": [(">=0" if vs == 0 else "<=0" if vs == 1 else "free") for vs in problem.varSign],
                "ten_bien": [f"x{i+1}" for i in range(problem.n)],
            },
            "solution": {
                "variables": {f"x{i+1}": val for i, val in enumerate(x_sol)},
                "objective_value": opt_val,
                "objective_type": problem.loai_muc_tieu,
                "solution_vector": x_sol,
                "solution_type": sol.get("solution_type", 0),
            },
            "iteration_log": sol.get("iteration_log", []),
            "num_iterations": len(sol.get("iteration_log", []))
        }
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({"error": f"Lỗi trong quá trình giải: {str(e)}"}), 500

@app.route("/api/example/<example_type>", methods=["GET"])
def get_example(example_type):
    examples = {
        "basic": {
            "loai_muc_tieu": "min",
            "he_so_muc_tieu": ["1", "1"],
            "ten_bien": ["x1", "x2"],
            "A": [["1", "1"], ["1", "0"], ["0", "1"]],
            "b": ["3", "1", "2"],
            "dau_rang_buoc": [">=", ">=", ">="],
            "rang_buoc_bien": [">=0", ">=0"],
        },
        "max": {
            "loai_muc_tieu": "max",
            "he_so_muc_tieu": ["3", "2"],
            "ten_bien": ["x1", "x2"],
            "A": [["2", "1"], ["1", "1"], ["1", "2"]],
            "b": ["100", "80", "100"],
            "dau_rang_buoc": ["<=", "<=", "<="],
            "rang_buoc_bien": [">=0", ">=0"],
        },
        "free": {
            "loai_muc_tieu": "min",
            "he_so_muc_tieu": ["1"],
            "ten_bien": ["x1"],
            "A": [["1"]],
            "b": ["2"],
            "dau_rang_buoc": ["="],
            "rang_buoc_bien": ["free"],
        },
        "mixed": {
            "loai_muc_tieu": "max",
            "he_so_muc_tieu": ["4", "3"],
            "ten_bien": ["x1", "x2"],
            "A": [["1", "2"], ["2", "1"]],
            "b": ["8", "10"],
            "dau_rang_buoc": ["<=", "<="],
            "rang_buoc_bien": [">=0", "<=0"],
        },
        "expr": {
            "loai_muc_tieu": "max",
            "he_so_muc_tieu": ["sqrt(9)", "3/2"],
            "ten_bien": ["x1", "x2"],
            "A": [["exp(0)", "2"], ["pi/pi", "abs(-3)"]],
            "b": ["10", "15"],
            "dau_rang_buoc": ["<=", "<="],
            "rang_buoc_bien": [">=0", ">=0"],
        }
    }
    if example_type in examples:
        return jsonify(examples[example_type]), 200
    return jsonify({"error": "Ví dụ không tồn tại"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True, use_reloader=True)
