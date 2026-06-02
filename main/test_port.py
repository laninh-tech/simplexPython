import numpy as np
from simplexPython.thuatToan.lp_solver import LPProblem, solve_lp, METHOD_TWO_PHASE, METHOD_DANTZIG, METHOD_BLAND, METHOD_GEOMETRY

def test_basic_min():
    print("Running Test: Basic Min Problem...")
    # min: x1 + x2
    # s.t: x1 + x2 >= 3, x1 >= 1, x2 >= 2
    # optimum should be x1=1, x2=2, z=3
    p = LPProblem(
        n=2,
        m=3,
        objectiveType=2,  # MIN
        c=[1.0, 1.0],
        A=[[1.0, 1.0], [1.0, 0.0], [0.0, 1.0]],
        b=[3.0, 1.0, 2.0],
        sign=[">=", ">=", ">="],
        varSign=[">=0", ">=0"]
    )
    
    for method in [METHOD_TWO_PHASE, METHOD_DANTZIG, METHOD_BLAND, METHOD_GEOMETRY]:
        sol = solve_lp(p, method)
        assert sol["status"] == 0, f"Method {method} failed"
        assert abs(sol["optimum"] - 3.0) < 1e-7, f"Method {method} got wrong optimum {sol['optimum']}"
        assert abs(sol["x"][0] - 1.0) < 1e-7, f"Method {method} got wrong x1 {sol['x'][0]}"
        assert abs(sol["x"][1] - 2.0) < 1e-7, f"Method {method} got wrong x2 {sol['x'][1]}"
        print(f"  Method {method}: Success! optimum = {sol['optimum']}")

def test_basic_max():
    print("Running Test: Basic Max Problem...")
    # max: 3*x1 + 2*x2
    # s.t: 2*x1 + x2 <= 100, x1 + x2 <= 80, x1 + 2*x2 <= 100
    # optimum should be x1=20, x2=60, z=180
    p = LPProblem(
        n=2,
        m=3,
        objectiveType=1,  # MAX
        c=[3.0, 2.0],
        A=[[2.0, 1.0], [1.0, 1.0], [1.0, 2.0]],
        b=[100.0, 80.0, 100.0],
        sign=["<=", "<=", "<="],
        varSign=[">=0", ">=0"]
    )
    
    for method in [METHOD_TWO_PHASE, METHOD_DANTZIG, METHOD_BLAND, METHOD_GEOMETRY]:
        sol = solve_lp(p, method)
        assert sol["status"] == 0, f"Method {method} failed"
        assert abs(sol["optimum"] - 166.66666666666666) < 1e-5, f"Method {method} got wrong optimum {sol['optimum']}"
        assert abs(sol["x"][0] - 33.33333333) < 1e-5, f"Method {method} got wrong x1 {sol['x'][0]}"
        assert abs(sol["x"][1] - 33.33333333) < 1e-5, f"Method {method} got wrong x2 {sol['x'][1]}"
        print(f"  Method {method}: Success! optimum = {sol['optimum']}")

def test_unbounded():
    print("Running Test: Unbounded Problem...")
    # max: x1 + x2
    # s.t: x1 >= 1, x2 >= 1
    p = LPProblem(
        n=2,
        m=2,
        objectiveType=1,
        c=[1.0, 1.0],
        A=[[1.0, 0.0], [0.0, 1.0]],
        b=[1.0, 1.0],
        sign=[">=", ">="],
        varSign=[">=0", ">=0"]
    )
    for method in [METHOD_TWO_PHASE, METHOD_DANTZIG, METHOD_BLAND, METHOD_GEOMETRY]:
        sol = solve_lp(p, method)
        assert sol["status"] == 2, f"Method {method} should detect unboundedness but got status {sol['status']}"
        print(f"  Method {method}: Success! Detected unboundedness.")

def test_infeasible():
    print("Running Test: Infeasible Problem...")
    # max: x1
    # s.t: x1 <= 1, x1 >= 2
    p = LPProblem(
        n=1,
        m=2,
        objectiveType=1,
        c=[1.0],
        A=[[1.0], [1.0]],
        b=[1.0, 2.0],
        sign=["<=", ">="],
        varSign=[">=0"]
    )
    for method in [METHOD_TWO_PHASE, METHOD_DANTZIG, METHOD_BLAND]:
        sol = solve_lp(p, method)
        assert sol["status"] == 1, f"Method {method} should detect infeasibility but got status {sol['status']}"
        print(f"  Method {method}: Success! Detected infeasibility.")

if __name__ == "__main__":
    print("==========================================")
    print("Executing tests for simplexPython...")
    print("==========================================")
    test_basic_min()
    test_basic_max()
    test_unbounded()
    test_infeasible()
    print("==========================================")
    print("All tests passed successfully!")
    print("==========================================")
