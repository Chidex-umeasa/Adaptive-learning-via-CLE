import subprocess
import tempfile
import os
import json
import random
from .problems import PROBLEM_BANK, get_problem


def select_next_problem(solved_ids: set[str], current_load: str | None) -> dict | None:
    unsolved = [p for p in PROBLEM_BANK if p["id"] not in solved_ids]
    if not unsolved:
        return None

    if current_load == "HIGH":
        unsolved.sort(key=lambda p: p["difficulty"])
        return unsolved[0]
    elif current_load == "LOW":
        unsolved.sort(key=lambda p: p["difficulty"], reverse=True)
        candidates = [p for p in unsolved if p["difficulty"] >= 3]
        return candidates[0] if candidates else unsolved[0]
    else:
        random.shuffle(unsolved)
        return unsolved[0]


def evaluate_submission(problem_id: str, code: str) -> dict:
    problem = get_problem(problem_id)
    if not problem:
        return {"correct": False, "tests_passed": 0, "tests_total": 0, "errors": ["Problem not found"]}

    test_cases = problem["test_cases"]

    if problem_id == "stack_impl":
        return _evaluate_stack(code, test_cases)

    return _evaluate_function(code, test_cases, problem_id)


def _evaluate_function(code: str, test_cases: list[dict], problem_id: str) -> dict:
    func_name = _infer_func_name(problem_id)
    passed = 0
    total = len(test_cases)
    errors = []

    for i, tc in enumerate(test_cases):
        args_json = json.dumps(tc["input"])
        expected_json = json.dumps(tc["expected"])

        js_code = f"""
{code}
const args = {args_json};
const expected = {expected_json};
const result = {func_name}(...args);
if (JSON.stringify(result) === JSON.stringify(expected)) {{
    process.stdout.write("PASS");
}} else {{
    process.stdout.write("FAIL:" + JSON.stringify(result));
}}
"""
        ok, output = _run_js(js_code)
        if ok and output.startswith("PASS"):
            passed += 1
        else:
            errors.append(f"Test {i+1}: expected {tc['expected']}, got {output}")

    return {
        "correct": passed == total,
        "tests_passed": passed,
        "tests_total": total,
        "errors": errors,
    }


def _evaluate_stack(code: str, test_cases: list[dict]) -> dict:
    passed = 0
    total = len(test_cases)
    errors = []

    for i, tc in enumerate(test_cases):
        commands = tc["input"]
        expected = tc["expected"]

        ops_js = ""
        for cmd in commands:
            if cmd.startswith("push:"):
                val = cmd.split(":")[1]
                ops_js += f"results.push(s.push({val}));\n"
            elif cmd == "pop":
                ops_js += "results.push(s.pop());\n"
            elif cmd == "peek":
                ops_js += "results.push(s.peek());\n"

        js_code = f"""
{code}
const s = new Stack();
const results = [];
{ops_js}
process.stdout.write(JSON.stringify(results));
"""
        ok, output = _run_js(js_code)
        if ok:
            try:
                result = json.loads(output)
                # Compare ignoring undefined -> null difference
                expected_normalized = [None if x is None else x for x in expected]
                result_normalized = [None if x is None else x for x in result]
                if result_normalized == expected_normalized:
                    passed += 1
                else:
                    errors.append(f"Test {i+1}: expected {expected}, got {result}")
            except json.JSONDecodeError:
                errors.append(f"Test {i+1}: invalid output: {output}")
        else:
            errors.append(f"Test {i+1}: runtime error: {output}")

    return {
        "correct": passed == total,
        "tests_passed": passed,
        "tests_total": total,
        "errors": errors,
    }


def _infer_func_name(problem_id: str) -> str:
    mapping = {
        "sum_two": "sum",
        "max_two": "maxOfTwo",
        "absolute_val": "absolute",
        "is_even": "isEven",
        "reverse_string": "reverseStr",
        "is_palindrome": "isPalindrome",
        "count_vowels": "countVowels",
        "filter_evens": "filterEvens",
        "array_sum": "arraySum",
        "find_max": "findMax",
        "unique_elements": "unique",
        "factorial": "factorial",
        "fibonacci": "fib",
        "power": "power",
        "two_sum": "twoSum",
        "flatten_array": "flatten",
    }
    return mapping.get(problem_id, problem_id)


def _run_js(js_code: str, timeout: int = 5) -> tuple[bool, str]:
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
            f.write(js_code)
            tmp_path = f.name

        result = subprocess.run(
            ["node", tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        os.unlink(tmp_path)

        if result.returncode == 0:
            return True, result.stdout
        return False, result.stderr[:500]
    except subprocess.TimeoutExpired:
        os.unlink(tmp_path)
        return False, "Timeout: code took too long to execute"
    except FileNotFoundError:
        return False, "Node.js not found — install Node.js to evaluate submissions"
    except Exception as e:
        return False, str(e)[:500]
