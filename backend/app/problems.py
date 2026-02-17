PROBLEM_BANK = [
    # --- Basics (difficulty 1) ---
    {
        "id": "sum_two",
        "title": "Sum of Two Numbers",
        "description": "Write a function `sum(a, b)` that returns the sum of two numbers.",
        "difficulty": 1,
        "category": "basics",
        "starter_code": "function sum(a, b) {\n  // your code here\n}\n",
        "test_cases": [
            {"input": [1, 2], "expected": 3},
            {"input": [-1, 5], "expected": 4},
            {"input": [0, 0], "expected": 0},
        ],
        "hints": [
            {"id": "sum_h1", "text": "Use the + operator to add two numbers.", "level": 1},
            {"id": "sum_h2", "text": "return a + b;", "level": 2},
        ],
        "concepts": ["functions", "arithmetic"],
    },
    {
        "id": "max_two",
        "title": "Maximum of Two",
        "description": "Write a function `maxOfTwo(a, b)` that returns the larger of two numbers.",
        "difficulty": 1,
        "category": "basics",
        "starter_code": "function maxOfTwo(a, b) {\n  // your code here\n}\n",
        "test_cases": [
            {"input": [3, 7], "expected": 7},
            {"input": [10, 2], "expected": 10},
            {"input": [5, 5], "expected": 5},
        ],
        "hints": [
            {"id": "max_h1", "text": "Compare a and b using > or use Math.max().", "level": 1},
            {"id": "max_h2", "text": "return a > b ? a : b;", "level": 2},
        ],
        "concepts": ["conditionals", "comparison"],
    },
    {
        "id": "absolute_val",
        "title": "Absolute Value",
        "description": "Write a function `absolute(n)` that returns the absolute value of a number without using Math.abs().",
        "difficulty": 1,
        "category": "basics",
        "starter_code": "function absolute(n) {\n  // your code here\n}\n",
        "test_cases": [
            {"input": [-5], "expected": 5},
            {"input": [3], "expected": 3},
            {"input": [0], "expected": 0},
        ],
        "hints": [
            {"id": "abs_h1", "text": "If the number is negative, negate it.", "level": 1},
            {"id": "abs_h2", "text": "return n < 0 ? -n : n;", "level": 2},
        ],
        "concepts": ["conditionals", "arithmetic"],
    },
    {
        "id": "is_even",
        "title": "Even or Odd",
        "description": "Write a function `isEven(n)` that returns true if n is even, false otherwise.",
        "difficulty": 1,
        "category": "basics",
        "starter_code": "function isEven(n) {\n  // your code here\n}\n",
        "test_cases": [
            {"input": [4], "expected": True},
            {"input": [7], "expected": False},
            {"input": [0], "expected": True},
        ],
        "hints": [
            {"id": "even_h1", "text": "Use the modulo operator %.", "level": 1},
            {"id": "even_h2", "text": "return n % 2 === 0;", "level": 2},
        ],
        "concepts": ["modulo", "boolean"],
    },
    # --- Strings (difficulty 2) ---
    {
        "id": "reverse_string",
        "title": "Reverse a String",
        "description": "Write a function `reverseStr(s)` that returns the reversed version of a string.",
        "difficulty": 2,
        "category": "strings",
        "starter_code": "function reverseStr(s) {\n  // your code here\n}\n",
        "test_cases": [
            {"input": ["hello"], "expected": "olleh"},
            {"input": ["abc"], "expected": "cba"},
            {"input": [""], "expected": ""},
        ],
        "hints": [
            {"id": "rev_h1", "text": "You can split the string into an array, reverse it, then join.", "level": 1},
            {"id": "rev_h2", "text": "return s.split('').reverse().join('');", "level": 2},
        ],
        "concepts": ["strings", "arrays"],
    },
    {
        "id": "is_palindrome",
        "title": "Palindrome Check",
        "description": "Write a function `isPalindrome(s)` that returns true if the string reads the same forwards and backwards (case-insensitive).",
        "difficulty": 2,
        "category": "strings",
        "starter_code": "function isPalindrome(s) {\n  // your code here\n}\n",
        "test_cases": [
            {"input": ["racecar"], "expected": True},
            {"input": ["hello"], "expected": False},
            {"input": ["Madam"], "expected": True},
        ],
        "hints": [
            {"id": "pal_h1", "text": "Convert to lowercase first, then compare with its reverse.", "level": 1},
            {"id": "pal_h2", "text": "const low = s.toLowerCase(); return low === low.split('').reverse().join('');", "level": 2},
        ],
        "concepts": ["strings", "comparison"],
    },
    {
        "id": "count_vowels",
        "title": "Count Vowels",
        "description": "Write a function `countVowels(s)` that returns the number of vowels (a, e, i, o, u) in a string (case-insensitive).",
        "difficulty": 2,
        "category": "strings",
        "starter_code": "function countVowels(s) {\n  // your code here\n}\n",
        "test_cases": [
            {"input": ["hello"], "expected": 2},
            {"input": ["AEIOU"], "expected": 5},
            {"input": ["xyz"], "expected": 0},
        ],
        "hints": [
            {"id": "vow_h1", "text": "Loop through each character and check if it's a vowel.", "level": 1},
            {"id": "vow_h2", "text": "return s.toLowerCase().split('').filter(c => 'aeiou'.includes(c)).length;", "level": 2},
        ],
        "concepts": ["strings", "loops", "filtering"],
    },
    # --- Arrays (difficulty 3) ---
    {
        "id": "filter_evens",
        "title": "Filter Even Numbers",
        "description": "Write a function `filterEvens(arr)` that returns a new array containing only the even numbers.",
        "difficulty": 3,
        "category": "arrays",
        "starter_code": "function filterEvens(arr) {\n  // your code here\n}\n",
        "test_cases": [
            {"input": [[1, 2, 3, 4, 5, 6]], "expected": [2, 4, 6]},
            {"input": [[1, 3, 5]], "expected": []},
            {"input": [[2, 4]], "expected": [2, 4]},
        ],
        "hints": [
            {"id": "filt_h1", "text": "Use the .filter() method with a condition for even numbers.", "level": 1},
            {"id": "filt_h2", "text": "return arr.filter(n => n % 2 === 0);", "level": 2},
        ],
        "concepts": ["arrays", "filter", "modulo"],
    },
    {
        "id": "array_sum",
        "title": "Sum of Array",
        "description": "Write a function `arraySum(arr)` that returns the sum of all numbers in an array.",
        "difficulty": 3,
        "category": "arrays",
        "starter_code": "function arraySum(arr) {\n  // your code here\n}\n",
        "test_cases": [
            {"input": [[1, 2, 3]], "expected": 6},
            {"input": [[10, -5, 3]], "expected": 8},
            {"input": [[]], "expected": 0},
        ],
        "hints": [
            {"id": "asum_h1", "text": "Use .reduce() to accumulate the sum.", "level": 1},
            {"id": "asum_h2", "text": "return arr.reduce((sum, n) => sum + n, 0);", "level": 2},
        ],
        "concepts": ["arrays", "reduce"],
    },
    {
        "id": "find_max",
        "title": "Find Maximum in Array",
        "description": "Write a function `findMax(arr)` that returns the largest number in an array. Assume the array is non-empty.",
        "difficulty": 3,
        "category": "arrays",
        "starter_code": "function findMax(arr) {\n  // your code here\n}\n",
        "test_cases": [
            {"input": [[1, 5, 3, 9, 2]], "expected": 9},
            {"input": [[-1, -5, -2]], "expected": -1},
            {"input": [[42]], "expected": 42},
        ],
        "hints": [
            {"id": "fmax_h1", "text": "You can use Math.max with the spread operator.", "level": 1},
            {"id": "fmax_h2", "text": "return Math.max(...arr);", "level": 2},
        ],
        "concepts": ["arrays", "Math"],
    },
    {
        "id": "unique_elements",
        "title": "Remove Duplicates",
        "description": "Write a function `unique(arr)` that returns a new array with duplicates removed, preserving order.",
        "difficulty": 3,
        "category": "arrays",
        "starter_code": "function unique(arr) {\n  // your code here\n}\n",
        "test_cases": [
            {"input": [[1, 2, 2, 3, 1]], "expected": [1, 2, 3]},
            {"input": [["a", "b", "a"]], "expected": ["a", "b"]},
            {"input": [[]], "expected": []},
        ],
        "hints": [
            {"id": "uniq_h1", "text": "You can use a Set to track seen values.", "level": 1},
            {"id": "uniq_h2", "text": "return [...new Set(arr)];", "level": 2},
        ],
        "concepts": ["arrays", "Set", "deduplication"],
    },
    # --- Recursion (difficulty 4) ---
    {
        "id": "factorial",
        "title": "Factorial",
        "description": "Write a function `factorial(n)` that returns n! using recursion. Assume n >= 0.",
        "difficulty": 4,
        "category": "recursion",
        "starter_code": "function factorial(n) {\n  // your code here\n}\n",
        "test_cases": [
            {"input": [5], "expected": 120},
            {"input": [0], "expected": 1},
            {"input": [1], "expected": 1},
        ],
        "hints": [
            {"id": "fact_h1", "text": "Base case: 0! = 1. Recursive case: n! = n * (n-1)!.", "level": 1},
            {"id": "fact_h2", "text": "if (n <= 1) return 1; return n * factorial(n - 1);", "level": 2},
        ],
        "concepts": ["recursion", "base case"],
    },
    {
        "id": "fibonacci",
        "title": "Fibonacci Number",
        "description": "Write a function `fib(n)` that returns the nth Fibonacci number (0-indexed: fib(0)=0, fib(1)=1, fib(2)=1, ...).",
        "difficulty": 4,
        "category": "recursion",
        "starter_code": "function fib(n) {\n  // your code here\n}\n",
        "test_cases": [
            {"input": [0], "expected": 0},
            {"input": [1], "expected": 1},
            {"input": [6], "expected": 8},
            {"input": [10], "expected": 55},
        ],
        "hints": [
            {"id": "fib_h1", "text": "Base cases: fib(0)=0, fib(1)=1. Otherwise fib(n)=fib(n-1)+fib(n-2).", "level": 1},
            {"id": "fib_h2", "text": "Use iteration or memoization for efficiency.", "level": 2},
        ],
        "concepts": ["recursion", "dynamic programming"],
    },
    {
        "id": "power",
        "title": "Power Function",
        "description": "Write a function `power(base, exp)` that computes base^exp using recursion. Assume exp >= 0.",
        "difficulty": 4,
        "category": "recursion",
        "starter_code": "function power(base, exp) {\n  // your code here\n}\n",
        "test_cases": [
            {"input": [2, 3], "expected": 8},
            {"input": [5, 0], "expected": 1},
            {"input": [3, 4], "expected": 81},
        ],
        "hints": [
            {"id": "pow_h1", "text": "Base case: anything to the power of 0 is 1.", "level": 1},
            {"id": "pow_h2", "text": "if (exp === 0) return 1; return base * power(base, exp - 1);", "level": 2},
        ],
        "concepts": ["recursion", "exponentiation"],
    },
    # --- Data Structures (difficulty 5) ---
    {
        "id": "stack_impl",
        "title": "Implement a Stack",
        "description": "Implement a Stack class with push(val), pop(), and peek() methods. pop() and peek() should return undefined on empty stack.",
        "difficulty": 5,
        "category": "data_structures",
        "starter_code": "class Stack {\n  constructor() {\n    // your code here\n  }\n  push(val) {\n    // your code here\n  }\n  pop() {\n    // your code here\n  }\n  peek() {\n    // your code here\n  }\n}\n",
        "test_cases": [
            {"input": ["push:1", "push:2", "peek", "pop", "peek"], "expected": [None, None, 2, 2, 1]},
            {"input": ["pop", "push:5", "pop"], "expected": [None, None, 5]},
        ],
        "hints": [
            {"id": "stack_h1", "text": "Use an array as the internal storage. Push adds to end, pop removes from end.", "level": 1},
            {"id": "stack_h2", "text": "this.items = []; push: this.items.push(val); pop: return this.items.pop();", "level": 2},
        ],
        "concepts": ["stack", "LIFO", "class"],
    },
    {
        "id": "two_sum",
        "title": "Two Sum",
        "description": "Write a function `twoSum(nums, target)` that returns the indices of two numbers that add up to the target. Assume exactly one solution exists.",
        "difficulty": 5,
        "category": "data_structures",
        "starter_code": "function twoSum(nums, target) {\n  // your code here\n}\n",
        "test_cases": [
            {"input": [[2, 7, 11, 15], 9], "expected": [0, 1]},
            {"input": [[3, 2, 4], 6], "expected": [1, 2]},
        ],
        "hints": [
            {"id": "ts_h1", "text": "Use a hash map to store each number's index as you iterate.", "level": 1},
            {"id": "ts_h2", "text": "For each num, check if (target - num) is already in the map.", "level": 2},
        ],
        "concepts": ["hash map", "arrays", "optimization"],
    },
    {
        "id": "flatten_array",
        "title": "Flatten Nested Array",
        "description": "Write a function `flatten(arr)` that takes a nested array and returns a single flat array. E.g. [1,[2,[3]]] -> [1,2,3].",
        "difficulty": 5,
        "category": "data_structures",
        "starter_code": "function flatten(arr) {\n  // your code here\n}\n",
        "test_cases": [
            {"input": [[[1, [2, [3]]]]], "expected": [1, 2, 3]},
            {"input": [[[1, 2, 3]]], "expected": [1, 2, 3]},
            {"input": [[[]]], "expected": []},
        ],
        "hints": [
            {"id": "flat_h1", "text": "Use recursion: if an element is an array, recursively flatten it.", "level": 1},
            {"id": "flat_h2", "text": "return arr.reduce((acc, item) => acc.concat(Array.isArray(item) ? flatten(item) : item), []);", "level": 2},
        ],
        "concepts": ["recursion", "arrays", "flatten"],
    },
]


def get_problem(problem_id: str) -> dict | None:
    for p in PROBLEM_BANK:
        if p["id"] == problem_id:
            return p
    return None


def get_all_problems() -> list[dict]:
    return PROBLEM_BANK
