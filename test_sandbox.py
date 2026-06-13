"""
Test suite for safe_eval sandbox.

Validates both:
1. Legitimate mathematical expressions produce correct results
2. Sandbox escape attempts are all blocked
"""

import sys
import math
from safe_eval import safe_eval
from whitelist import _HAS_NUMPY

PASS = 0
FAIL = 0


def test(expression, expect_result=None, expect_blocked=False, label=""):
    """Run a single test case and report the outcome."""
    global PASS, FAIL
    try:
        result = safe_eval(expression)
        if expect_blocked:
            print(f"  ESCAPE NOT BLOCKED! [{label}] {expression} => {repr(result)}")
            FAIL += 1
        elif expect_result is not None:
            # Use numpy.allclose for float comparison when both are arrays
            ok = _values_equal(result, expect_result)
            if ok:
                print(f"  OK  [{label}] {expression} => {repr(result)}")
                PASS += 1
            else:
                print(
                    f"  MISMATCH [{label}] {expression} => {repr(result)}  (expected {repr(expect_result)})"
                )
                FAIL += 1
        else:
            print(f"  OK  [{label}] {expression} => {repr(result)}")
            PASS += 1
    except Exception as e:
        if expect_blocked:
            print(f"  BLOCKED [{label}] {expression}  ({type(e).__name__}: {e})")
            PASS += 1
        else:
            print(
                f"  UNEXPECTED ERROR [{label}] {expression} => {type(e).__name__}: {e}"
            )
            FAIL += 1


def _values_equal(a, b):
    """Compare two values, handling numpy arrays and containers."""
    if _HAS_NUMPY:
        import numpy as np

        if isinstance(a, np.ndarray) and isinstance(b, np.ndarray):
            return bool(np.allclose(a, b))
        # Handle tuples of arrays (e.g. nonzero return value)
        if isinstance(a, tuple) and isinstance(b, tuple):
            if len(a) != len(b):
                return False
            return all(_values_equal(x, y) for x, y in zip(a, b))
        # Handle lists of arrays (e.g. split return value)
        if isinstance(a, list) and isinstance(b, list):
            if len(a) != len(b):
                return False
            return all(_values_equal(x, y) for x, y in zip(a, b))
    return a == b


# ============================================================
# 1. Basic arithmetic
# ============================================================
print("=" * 60)
print("1. Basic arithmetic")
print("=" * 60)

test("1 + 1", 2, label="addition")
test("2 ** 10", 1024, label="exponentiation")
test("2 * 3 + 4", 10, label="precedence")
test("(2 + 3) * 4", 20, label="parentheses")
test("10 / 3", 10 / 3, label="float division")
test("10 // 3", 3, label="floor division")
test("10 % 3", 1, label="modulo")
test("1 << 4", 16, label="left shift")
test("16 >> 2", 4, label="right shift")
test("5 & 3", 1, label="bitwise AND")
test("5 | 3", 7, label="bitwise OR")
test("5 ^ 3", 6, label="bitwise XOR")
test("~0", -1, label="bitwise NOT")
test("-5 + 3", -2, label="negation")
test("not True", False, label="not True")
test("not False", True, label="not False")

# ============================================================
# 2. Comparison operators
# ============================================================
print("=" * 60)
print("2. Comparison operators")
print("=" * 60)

test("1 < 2", True, label="less than")
test("1 <= 1", True, label="less or equal")
test("2 > 1", True, label="greater than")
test("2 >= 2", True, label="greater or equal")
test("1 == 1", True, label="equal")
test("1 != 2", True, label="not equal")
test("1 is None", False, label="is None")
test("None is None", True, label="None is None")
test("1 in [1, 2, 3]", True, label="in list")
test("5 not in [1, 2, 3]", True, label="not in list")
test("1 < 2 < 3", True, label="chained comparison")
test("1 < 2 and 3 < 4", True, label="bool and")
test("1 < 0 or 2 > 1", True, label="bool or")

# ============================================================
# 3. Ternary / conditional expressions
# ============================================================
print("=" * 60)
print("3. Ternary expressions")
print("=" * 60)

test("1 if True else 0", 1, label="true branch")
test("0 if False else 1", 1, label="false branch")
test("'high' if 10 > 5 else 'low'", "high", label="string result")

# ============================================================
# 4. Built-in safe functions
# ============================================================
print("=" * 60)
print("4. Built-in safe functions")
print("=" * 60)

test("abs(-5)", 5, label="abs")
test("min(3, 1, 2)", 1, label="min")
test("max(3, 1, 2)", 3, label="max")
test("sum([1, 2, 3, 4])", 10, label="sum")
test("round(3.7)", 4, label="round")
test("len([1, 2, 3])", 3, label="len")
test("list(range(5))", [0, 1, 2, 3, 4], label="range")
test("int(3.14)", 3, label="int")
test("float(3)", 3.0, label="float")
test("str(42)", "42", label="str")
test("bool(1)", True, label="bool")
test("list(enumerate(['a', 'b']))", [(0, "a"), (1, "b")], label="enumerate")
test("list(zip([1, 2], ['a', 'b']))", [(1, "a"), (2, "b")], label="zip")
test("list(map(str, [1, 2, 3]))", ["1", "2", "3"], label="map")
test("list(filter(None, [0, 1, 0, 2, 3]))", [1, 2, 3], label="filter")
test("sorted([3, 1, 2])", [1, 2, 3], label="sorted")
test("list(reversed([1, 2, 3]))", [3, 2, 1], label="reversed")
test("any([False, False, True])", True, label="any")
test("all([True, True, False])", False, label="all")
test("chr(65)", "A", label="chr")
test("ord('A')", 65, label="ord")
test("hex(255)", "0xff", label="hex")
test("oct(8)", "0o10", label="oct")
test("bin(3)", "0b11", label="bin")
test("divmod(10, 3)", (3, 1), label="divmod")
test("pow(2, 10)", 1024, label="pow")

# ============================================================
# 5. Collections (list, tuple, set, dict)
# ============================================================
print("=" * 60)
print("5. Collections")
print("=" * 60)

test("[1, 2, 3][0]", 1, label="list indexing")
test("(1, 2, 3)[1]", 2, label="tuple indexing")
test("{1, 2, 3}", {1, 2, 3}, label="set literal")
test("{'a': 1, 'b': 2}['a']", 1, label="dict access")
test("[1, 2, 3][0:2]", [1, 2], label="list slice")

# ============================================================
# 6. Comprehensions
# ============================================================
print("=" * 60)
print("6. Comprehensions")
print("=" * 60)

test("[x**2 for x in range(5)]", [0, 1, 4, 9, 16], label="list comp")
test("{x for x in range(3)}", {0, 1, 2}, label="set comp")
test("{x: x**2 for x in range(3)}", {0: 0, 1: 1, 2: 4}, label="dict comp")
test("list(x for x in range(3))", [0, 1, 2], label="generator exp")
test(
    "[x*y for x in range(3) for y in range(2)]", [0, 0, 0, 1, 0, 2], label="nested comp"
)
test("[x for x in range(10) if x % 2 == 0]", [0, 2, 4, 6, 8], label="comp with if")

# ============================================================
# 7. math module
# ============================================================
print("=" * 60)
print("7. math module")
print("=" * 60)

test("math.pi", 3.141592653589793, label="pi constant")
test("math.e", 2.718281828459045, label="e constant")
test("math.sin(0)", 0.0, label="sin(0)")
test("math.cos(0)", 1.0, label="cos(0)")
test("math.tan(0)", 0.0, label="tan(0)")
test("math.sin(math.pi / 2)", 1.0, label="sin(pi/2)")
test("math.sqrt(16)", 4.0, label="sqrt")
test("math.log(math.e)", 1.0, label="log")
test("math.log10(100)", 2.0, label="log10")
test("math.exp(0)", 1.0, label="exp(0)")
test("math.floor(3.7)", 3, label="floor")
test("math.ceil(3.2)", 4, label="ceil")
test("math.fabs(-5.0)", 5.0, label="fabs")
test("math.degrees(math.pi)", 180.0, label="degrees")
test("math.radians(180)", 3.141592653589793, label="radians")
test("math.gcd(48, 18)", 6, label="gcd")
test("math.factorial(5)", 120, label="factorial")
test("math.comb(5, 2)", 10, label="comb")
test("math.hypot(3, 4)", 5.0, label="hypot")
test("math.isinf(math.inf)", True, label="isinf")

# ============================================================
# 8. random module
# ============================================================
print("=" * 60)
print("8. random module")
print("=" * 60)

test("random.random() >= 0", True, label="random in [0,1)")
test("0 <= random.randint(1, 10) <= 10", True, label="randint range")
test("random.choice([1, 2, 3]) in [1, 2, 3]", True, label="choice")
test("random.uniform(0, 1) >= 0", True, label="uniform")

# ============================================================
# 9. numpy module (if available)
# ============================================================
if _HAS_NUMPY:
    print("=" * 60)
    print("9. numpy module")
    print("=" * 60)

    import numpy as np

    test("numpy.array([1, 2, 3])", np.array([1, 2, 3]), label="array")
    test("numpy.arange(5)", np.arange(5), label="arange")
    test("numpy.linspace(0, 10, 5)", np.linspace(0, 10, 5), label="linspace")
    test("numpy.zeros(3)", np.zeros(3), label="zeros")
    test("numpy.ones(3)", np.ones(3), label="ones")
    test("numpy.eye(2)", np.eye(2), label="eye")
    test("numpy.sin(numpy.pi/2)", 1.0, label="numpy sin")
    test(
        "numpy.sqrt(numpy.array([1, 4, 9]))",
        np.array([1.0, 2.0, 3.0]),
        label="numpy sqrt",
    )
    test("numpy.mean(numpy.array([1, 2, 3]))", 2.0, label="mean")
    test("numpy.std(numpy.array([1, 2, 3]))", np.std([1, 2, 3]), label="std")
    test("numpy.dot(numpy.array([1, 2]), numpy.array([3, 4]))", 11, label="dot")
    test(
        "numpy.reshape(numpy.arange(6), (2, 3))",
        np.arange(6).reshape(2, 3),
        label="reshape",
    )
    test("numpy.sum(numpy.array([1, 2, 3]))", 6, label="sum")
    test("numpy.max(numpy.array([1, 5, 3]))", 5, label="max")

    # np alias
    test("np.array([1, 2, 3])", np.array([1, 2, 3]), label="np alias")
    test("np.mean(np.array([1, 2, 3]))", 2.0, label="np.mean alias")


# ============================================================
# 9x. Complex number base & bitwise calculations
# ============================================================
print("=" * 60)
print("9x. Number base & bitwise operations")
print("=" * 60)

# Hex arithmetic
test("0xFF + 0x01", 256, label="hex addition")
test("0xFF - 0x0F", 240, label="hex subtraction")
test("0x10 * 0x10", 256, label="hex multiplication")
test("0xFF & 0x0F", 15, label="hex bitwise AND")
test("0xF0 | 0x0F", 255, label="hex bitwise OR")
test("0xF0 ^ 0xFF", 15, label="hex bitwise XOR")
test("~0xFF & 0xFFFF", 0xFF00, label="hex bitwise NOT (masked)")
test("0x1 << 8", 256, label="hex left shift")
test("0x100 >> 4", 16, label="hex right shift")

# Octal
test("0o777 + 0o001", 512, label="octal addition")
test("0o777 & 0o070", 56, label="octal bitwise")

# Binary
test("0b1010 + 0b0101", 15, label="binary addition")
test("0b1111 & 0b1010", 10, label="binary AND")
test("0b1111 | 0b0000", 15, label="binary OR")
test("0b1111 ^ 0b1010", 5, label="binary XOR")

# Mixed radix
test("hex(0xFF)", "0xff", label="hex conversion")
test("oct(0o777)", "0o777", label="oct conversion")
test("bin(0b1010)", "0b1010", label="bin conversion")
test("int('FF', 16)", 255, label="parse hex string")
test("int('1010', 2)", 10, label="parse binary string")
test("int('777', 8)", 511, label="parse octal string")

# Complex bit manipulation
test("(0x1234 >> 8) & 0xFF", 0x12, label="extract high byte")
test("0x1234 & 0xFF", 0x34, label="extract low byte")
test("((0x12 << 8) | 0x34)", 0x1234, label="combine bytes")
test("0xAA ^ 0x55", 0xFF, label="XOR complement")
test("(~0x0F + 1) & 0xFFFF", 0xFFF1, label="two's complement low 16")
test("(0xDEADBEEF >> 16) & 0xFFFF", 0xDEAD, label="extract high word")
test("0b11110000 >> 4", 15, label="nibble shift")

# Large number arithmetic
test("2 ** 64", 18446744073709551616, label="2^64")
test("math.factorial(20)", 2432902008176640000, label="20!")
test("1 << 63", 9223372036854775808, label="1 << 63")

# Float precision edge cases
test("1.0 / 3.0 * 3.0", 1.0, label="float roundtrip")
test("math.ulp(1.0)", 2.220446049250313e-16, label="float epsilon")
test("1e308 * 10", float("inf"), label="overflow to inf")
test("-1e308 * 10", float("-inf"), label="overflow to -inf")
test(
    "math.isnan(0.0 / 0.0) if False else math.isnan(math.nan)",
    True,
    label="NaN truth check",
)
test("math.inf > 1e308", True, label="inf greater than any finite")

# ============================================================
# 9y. Advanced math module
# ============================================================
print("=" * 60)
print("9y. Advanced math module")
print("=" * 60)

test("round(math.erf(1.0), 14)", round(0.8427007929497148, 14), label="erf(1)")
test("round(math.erfc(1.0), 14)", round(0.15729920705028513, 14), label="erfc(1)")
test("math.gamma(5)", 24.0, label="gamma(5)=4!")
test("round(math.lgamma(5), 13)", round(3.1780538303479458, 13), label="lgamma(5)")
test("round(math.expm1(1e-10), 20)", round(1.00000000005e-10, 20), label="expm1 small")
test("round(math.log1p(1e-10), 10)", 1e-10, label="log1p small ≈ x")
test("math.isfinite(1e308)", True, label="finite check")
test("math.isinf(math.inf)", True, label="inf check")
test("math.isnan(math.nan)", True, label="nan check")
test("math.copysign(1.0, -5.0)", -1.0, label="copysign")
test("math.fsum([0.1]*10)", 1.0, label="fsum precise")
test("math.prod([1,2,3,4,5])", 120, label="prod")
test("math.dist((0,0), (3,4))", 5.0, label="dist")
test("math.perm(10, 3)", 720, label="permutations")
test("math.lcm(12, 18)", 36, label="lcm")
test("math.nextafter(1.0, 2.0)", 1.0000000000000002, label="nextafter up")
test("math.ulp(0.0)", 5e-324, label="ulp zero")
test("math.modf(3.14)[0] + math.modf(3.14)[1]", 3.14, label="modf sum")
test("math.frexp(8.0)[0] * (2 ** math.frexp(8.0)[1])", 8.0, label="frexp roundtrip")

# Trigonometric identities
test("round(math.sin(math.pi/6), 10)", 0.5, label="sin(30°)")
test("round(math.cos(math.pi/3), 10)", 0.5, label="cos(60°)")
test("round(math.tan(math.pi/4), 10)", 1.0, label="tan(45°)")
test("round(math.asin(0.5), 10)", round(math.pi / 6, 10), label="asin(0.5)")
test("round(math.atan2(1, 1), 10)", round(math.pi / 4, 10), label="atan2(1,1)")
test("round(math.sinh(0), 10)", 0.0, label="sinh(0)")
test("round(math.cosh(0), 10)", 1.0, label="cosh(0)")


# ============================================================
# 9z. Complex numpy operations (if available)
# ============================================================
if _HAS_NUMPY:
    print("=" * 60)
    print("9z. Complex numpy operations")
    print("=" * 60)

    import numpy as np

    # --- Linear algebra ---
    test("numpy.trace(numpy.eye(3))", 3.0, label="trace of I3")
    test("numpy.linalg.det(numpy.eye(3))", 1.0, label="det(I3)")
    test("numpy.linalg.inv(numpy.array([[2.0]]))", np.array([[0.5]]), label="inv 1x1")
    test("numpy.linalg.matrix_rank(numpy.eye(4))", 4, label="rank I4")
    test("numpy.linalg.norm(numpy.array([3.0, 4.0]))", 5.0, label="norm [3,4]")
    test("numpy.linalg.eigvals(numpy.eye(2))", np.array([1.0, 1.0]), label="eigvals I2")

    # --- Statistics ---
    test("numpy.median(numpy.array([1, 2, 3, 4, 5]))", 3.0, label="median")
    test("numpy.percentile(numpy.arange(1, 101), 50)", 50.5, label="50th percentile")
    test("numpy.quantile(numpy.arange(1, 101), 0.5)", 50.5, label="0.5 quantile")
    test("numpy.var(numpy.array([1, 2, 3, 4, 5]))", 2.0, label="var")
    test(
        "numpy.corrcoef(numpy.array([1,2,3]), numpy.array([3,2,1]))",
        np.array([[1.0, -1.0], [-1.0, 1.0]]),
        label="corrcoef",
    )
    test(
        "numpy.cov(numpy.array([1,2,3]), numpy.array([3,2,1]))",
        np.array([[1.0, -1.0], [-1.0, 1.0]]),
        label="cov",
    )
    test("numpy.ptp(numpy.array([1, 5, 3, 9, 2]))", 8, label="ptp (peak-to-peak)")

    # --- Cumulative operations ---
    test(
        "numpy.cumsum(numpy.array([1, 2, 3, 4]))",
        np.array([1, 3, 6, 10]),
        label="cumsum",
    )
    test(
        "numpy.cumprod(numpy.array([1, 2, 3, 4]))",
        np.array([1, 2, 6, 24]),
        label="cumprod",
    )

    # --- Array manipulation ---
    test(
        "numpy.transpose(numpy.array([[1,2],[3,4]]))",
        np.array([[1, 3], [2, 4]]),
        label="transpose",
    )
    test(
        "numpy.ravel(numpy.array([[1,2],[3,4]]))", np.array([1, 2, 3, 4]), label="ravel"
    )
    test("numpy.squeeze(numpy.array([[[1],[2]]]))", np.array([1, 2]), label="squeeze")
    test(
        "numpy.expand_dims(numpy.array([1,2,3]), axis=0)",
        np.array([[1, 2, 3]]),
        label="expand_dims",
    )
    test(
        "numpy.swapaxes(numpy.array([[[1,2],[3,4]]]), 0, 2)",
        np.array([[[1], [3]], [[2], [4]]]),
        label="swapaxes",
    )
    test(
        "numpy.moveaxis(numpy.array([[1,2],[3,4]]), 0, 1)",
        np.array([[1, 3], [2, 4]]),
        label="moveaxis",
    )

    # --- Stacking / concatenation ---
    test(
        "numpy.concatenate((numpy.array([1,2]), numpy.array([3,4])))",
        np.array([1, 2, 3, 4]),
        label="concatenate 1d",
    )
    test(
        "numpy.vstack((numpy.array([1,2]), numpy.array([3,4])))",
        np.array([[1, 2], [3, 4]]),
        label="vstack",
    )
    test(
        "numpy.hstack((numpy.array([1,2]), numpy.array([3,4])))",
        np.array([1, 2, 3, 4]),
        label="hstack",
    )
    test(
        "numpy.stack((numpy.array([1,2]), numpy.array([3,4])), axis=0)",
        np.array([[1, 2], [3, 4]]),
        label="stack axis=0",
    )
    test(
        "numpy.column_stack((numpy.array([1,2]), numpy.array([3,4])))",
        np.array([[1, 3], [2, 4]]),
        label="column_stack",
    )

    # --- Splitting ---
    test(
        "numpy.split(numpy.array([1,2,3,4]), 2)",
        [np.array([1, 2]), np.array([3, 4])],
        label="split",
    )
    test(
        "numpy.array_split(numpy.arange(5), 2)",
        [np.array([0, 1, 2]), np.array([3, 4])],
        label="array_split odd",
    )

    # --- Tiling / padding ---
    test("numpy.tile(numpy.array([1,2]), 2)", np.array([1, 2, 1, 2]), label="tile")
    test("numpy.repeat(numpy.array([1,2]), 2)", np.array([1, 1, 2, 2]), label="repeat")
    test(
        "numpy.pad(numpy.array([1,2,3]), pad_width=1, mode='constant', constant_values=0)",
        np.array([0, 1, 2, 3, 0]),
        label="pad",
    )

    # --- Rolling / flipping ---
    test(
        "numpy.roll(numpy.array([1,2,3,4]), shift=1)",
        np.array([4, 1, 2, 3]),
        label="roll",
    )
    test("numpy.flip(numpy.array([1,2,3]))", np.array([3, 2, 1]), label="flip")
    test(
        "numpy.fliplr(numpy.array([[1,2],[3,4]]))",
        np.array([[2, 1], [4, 3]]),
        label="fliplr",
    )
    test(
        "numpy.flipud(numpy.array([[1,2],[3,4]]))",
        np.array([[3, 4], [1, 2]]),
        label="flipud",
    )
    test(
        "numpy.rot90(numpy.array([[1,2],[3,4]]))",
        np.array([[2, 4], [1, 3]]),
        label="rot90",
    )

    # --- Diagonal ---
    test(
        "numpy.diag(numpy.array([1,2,3]))",
        np.array([[1, 0, 0], [0, 2, 0], [0, 0, 3]]),
        label="diag 1d->2d",
    )
    test(
        "numpy.diag(numpy.array([[1,2],[3,4]]))", np.array([1, 4]), label="diag 2d->1d"
    )
    test(
        "numpy.triu(numpy.array([[1,2,3],[4,5,6],[7,8,9]]))",
        np.array([[1, 2, 3], [0, 5, 6], [0, 0, 9]]),
        label="triu",
    )
    test(
        "numpy.tril(numpy.array([[1,2,3],[4,5,6],[7,8,9]]))",
        np.array([[1, 0, 0], [4, 5, 0], [7, 8, 9]]),
        label="tril",
    )

    # --- Sorting / searching ---
    test(
        "numpy.sort(numpy.array([3, 1, 4, 1, 5]))",
        np.array([1, 1, 3, 4, 5]),
        label="sort",
    )
    test("numpy.argsort(numpy.array([3, 1, 2]))", np.array([1, 2, 0]), label="argsort")
    test("numpy.argmax(numpy.array([1, 5, 3]))", 1, label="argmax")
    test("numpy.argmin(numpy.array([3, 1, 5]))", 1, label="argmin")
    test("numpy.searchsorted(numpy.array([1, 3, 5]), 2)", 1, label="searchsorted")
    test(
        "numpy.unique(numpy.array([1, 2, 2, 3, 3, 3]))",
        np.array([1, 2, 3]),
        label="unique",
    )
    test(
        "numpy.bincount(numpy.array([0, 1, 1, 2, 2, 2]))",
        np.array([1, 2, 3]),
        label="bincount",
    )
    test(
        "numpy.digitize(numpy.array([0.5, 1.5, 2.5]), bins=numpy.array([1, 2]))",
        np.array([0, 1, 2]),
        label="digitize",
    )

    # --- Logic ---
    test(
        "numpy.where(numpy.array([True, False, True]), numpy.array([1,2,3]), numpy.array([4,5,6]))",
        np.array([1, 5, 3]),
        label="where 3-arg",
    )
    test(
        "numpy.argwhere(numpy.array([True, False, True]))",
        np.array([[0], [2]]),
        label="argwhere",
    )
    test("numpy.clip(numpy.array([1, 5, 10]), 2, 8)", np.array([2, 5, 8]), label="clip")
    test(
        "numpy.isclose(numpy.array([1.0, 2.0]), numpy.array([1.0, 2.0001]), atol=1e-3)",
        np.array([True, True]),
        label="isclose",
    )
    test(
        "numpy.allclose(numpy.array([1.0, 2.0]), numpy.array([1.0, 2.0001]), atol=1e-3)",
        True,
        label="allclose",
    )
    test(
        "numpy.isnan(numpy.array([1, numpy.nan, 3]))",
        np.array([False, True, False]),
        label="isnan",
    )
    test(
        "numpy.isinf(numpy.array([1, numpy.inf, 3]))",
        np.array([False, True, False]),
        label="isinf",
    )
    test(
        "numpy.isfinite(numpy.array([1, numpy.nan, numpy.inf, 3]))",
        np.array([True, False, False, True]),
        label="isfinite",
    )

    # --- Meshgrid / broadcasting ---
    test(
        "numpy.meshgrid(numpy.array([1,2]), numpy.array([3,4]))[0]",
        np.array([[1, 2], [1, 2]]),
        label="meshgrid x",
    )
    test(
        "numpy.meshgrid(numpy.array([1,2]), numpy.array([3,4]))[1]",
        np.array([[3, 3], [4, 4]]),
        label="meshgrid y",
    )
    test(
        "numpy.broadcast_to(numpy.array([1,2,3]), (2, 3))",
        np.array([[1, 2, 3], [1, 2, 3]]),
        label="broadcast_to",
    )
    test(
        "numpy.broadcast_arrays(numpy.array([1,2,3]), numpy.array([[1],[2]]))[0]",
        np.array([[1, 2, 3], [1, 2, 3]]),
        label="broadcast_arrays",
    )

    # --- Einsum (advanced) ---
    test(
        "numpy.einsum('i,i->', numpy.array([1,2,3]), numpy.array([4,5,6]))",
        32,
        label="einsum dot product",
    )
    test(
        "numpy.einsum('ij,jk->ik', numpy.array([[1,0],[0,1]]), numpy.array([[2,3],[4,5]]))",
        np.array([[2, 3], [4, 5]]),
        label="einsum matmul",
    )
    test("numpy.einsum('ii->', numpy.array([[1,2],[3,4]]))", 5, label="einsum trace")

    # --- Outer / inner / kron ---
    test(
        "numpy.outer(numpy.array([1,2,3]), numpy.array([4,5]))",
        np.array([[4, 5], [8, 10], [12, 15]]),
        label="outer",
    )
    test(
        "numpy.inner(numpy.array([1,2,3]), numpy.array([4,5,6]))",
        32,
        label="inner product",
    )
    test(
        "numpy.kron(numpy.array([1,2]), numpy.array([3,4]))",
        np.array([3, 4, 6, 8]),
        label="kron",
    )
    test(
        "numpy.vdot(numpy.array([1+2j, 3+4j]), numpy.array([5+6j, 7+8j]))",
        70 - 8j,
        label="vdot complex",
    )

    # --- Tensordot ---
    test(
        "numpy.tensordot(numpy.ones((2,3)), numpy.ones((3,4)), axes=1)",
        np.full((2, 4), 3.0),
        label="tensordot",
    )

    # --- Polynomials ---
    test(
        "numpy.poly(numpy.array([1, 2]))",
        np.array([1.0, -3.0, 2.0]),
        label="poly from roots",
    )
    test("numpy.polyval(numpy.array([1, 0, 0]), 2)", 4.0, label="polyval x^2 at 2")
    test(
        "numpy.roots(numpy.array([1, -3, 2]))",
        np.array([2.0, 1.0]),
        label="roots quadratic",
    )
    test("numpy.polyder(numpy.array([1, 0, 0]))", np.array([2.0, 0.0]), label="polyder")
    test(
        "numpy.polyint(numpy.array([2, 0]))", np.array([1.0, 0.0, 0.0]), label="polyint"
    )
    test(
        "numpy.polyadd(numpy.array([1, 0]), numpy.array([0, 1]))",
        np.array([1.0, 1.0]),
        label="polyadd",
    )
    test(
        "numpy.polysub(numpy.array([1, 0]), numpy.array([0, 1]))",
        np.array([1.0, -1.0]),
        label="polysub",
    )
    test(
        "numpy.polymul(numpy.array([1, 0]), numpy.array([1, 1]))",
        np.array([1.0, 1.0, 0.0]),
        label="polymul",
    )

    # --- Window functions ---
    test("numpy.hamming(5)", np.array([0.08, 0.54, 1.0, 0.54, 0.08]), label="hamming 5")
    test("numpy.hanning(5)", np.array([0.0, 0.5, 1.0, 0.5, 0.0]), label="hanning 5")
    test("numpy.bartlett(5)", np.array([0.0, 0.5, 1.0, 0.5, 0.0]), label="bartlett 5")
    test(
        "numpy.blackman(5)",
        np.array(
            [
                -1.38777878e-17,
                3.40000000e-01,
                1.00000000e00,
                3.40000000e-01,
                -1.38777878e-17,
            ]
        ),
        label="blackman 5",
    )
    test("numpy.kaiser(5, 0.0)", np.ones(5), label="kaiser beta=0")

    # --- FFT ---
    test(
        "numpy.fft.fft(numpy.array([1.0, 0.0, 0.0, 0.0]))",
        np.array([1.0 + 0.0j, 1.0 + 0.0j, 1.0 + 0.0j, 1.0 + 0.0j]),
        label="fft impulse",
    )
    test(
        "numpy.fft.ifft(numpy.array([1.+0.j, 1.+0.j, 1.+0.j, 1.+0.j]))",
        np.array([1.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j]),
        label="ifft constant",
    )
    test(
        "numpy.fft.rfft(numpy.array([1.0, 0.0, 0.0, 0.0]))",
        np.array([1.0 + 0.0j, 1.0 + 0.0j, 1.0 + 0.0j]),
        label="rfft impulse",
    )
    test(
        "numpy.fft.fftfreq(4, d=1.0)",
        np.array([0.0, 0.25, -0.5, -0.25]),
        label="fftfreq 4",
    )
    test(
        "numpy.fft.fftshift(numpy.fft.fftfreq(4))",
        np.array([-0.5, -0.25, 0.0, 0.25]),
        label="fftshift",
    )
    test(
        "numpy.fft.ifftshift(numpy.array([0., 0.25, -0.5, -0.25]))",
        np.array([-0.5, -0.25, 0.0, 0.25]),
        label="ifftshift",
    )

    # --- Geometric space ---
    test(
        "numpy.geomspace(1, 1000, 4)",
        np.array([1.0, 10.0, 100.0, 1000.0]),
        label="geomspace",
    )
    test(
        "numpy.logspace(0, 3, 4)",
        np.array([1.0, 10.0, 100.0, 1000.0]),
        label="logspace",
    )

    # --- Vandermonde / tri ---
    test(
        "numpy.vander(numpy.array([1,2,3]), N=3)",
        np.array([[1, 1, 1], [4, 2, 1], [9, 3, 1]]),
        label="vander 3",
    )
    test("numpy.full((2, 2), 3.0)", np.full((2, 2), 3.0), label="full")
    test(
        "numpy.fromiter(range(5), dtype=float)",
        np.array([0.0, 1.0, 2.0, 3.0, 4.0]),
        label="fromiter",
    )

    # --- Histogram ---
    test(
        "numpy.histogram(numpy.array([1, 2, 2, 3, 3, 3, 4]), bins=2)[0]",
        np.array([3, 4]),
        label="histogram",
    )
    test(
        "numpy.histogram2d(numpy.array([0,1,1]), numpy.array([0,1,1]), bins=1)[0]",
        np.array([[3.0]]),
        label="histogram2d",
    )
    test(
        "numpy.gradient(numpy.array([1, 2, 4, 7]))",
        np.array([1.0, 1.5, 2.5, 3.0]),
        label="gradient",
    )

    # --- Type conversion ---
    test("numpy.asarray([1, 2, 3])", np.array([1, 2, 3]), label="asarray list")
    test("numpy.asanyarray([1, 2, 3])", np.array([1, 2, 3]), label="asanyarray")
    test(
        "numpy.ascontiguousarray(numpy.array([[1,2],[3,4]]))",
        np.array([[1, 2], [3, 4]]),
        label="ascontiguousarray",
    )
    test("numpy.atleast_1d(1)", np.array([1]), label="atleast_1d scalar")
    test(
        "numpy.atleast_2d(numpy.array([1,2,3]))",
        np.array([[1, 2, 3]]),
        label="atleast_2d 1d",
    )
    test(
        "numpy.atleast_3d(numpy.array([1,2]))",
        np.array([[[1], [2]]]),
        label="atleast_3d 1d",
    )

    # --- Matrix multiplication operator @ ---
    test(
        "numpy.eye(2) @ numpy.ones(2)",
        np.eye(2) @ np.ones(2),
        label="matmul @ operator",
    )

    # --- Chained numpy with math ---
    test(
        "math.sqrt(numpy.mean(numpy.square(numpy.array([1, 2, 3]))))",
        np.sqrt(np.mean(np.square([1, 2, 3]))),
        label="rms via numpy+math",
    )
    test(
        "numpy.sum(numpy.sin(numpy.linspace(0, math.pi, 3)))",
        np.sum(np.sin(np.linspace(0, np.pi, 3))),
        label="mixed numpy+math trig",
    )

    # --- Difference ---
    test("numpy.diff(numpy.array([1, 2, 4, 7]))", np.array([1, 2, 3]), label="diff 1st")
    test(
        "numpy.diff(numpy.array([1, 2, 4, 7]), n=2)", np.array([1, 1]), label="diff 2nd"
    )

    # --- Sign / real checks ---
    test("numpy.sign(numpy.array([-3, 0, 5]))", np.array([-1, 0, 1]), label="sign")
    test(
        "numpy.isreal(numpy.array([1+0j, 1j, 2.0]))",
        np.array([True, False, True]),
        label="isreal",
    )
    test(
        "numpy.iscomplex(numpy.array([1+0j, 1j, 2.0]))",
        np.array([False, True, False]),
        label="iscomplex",
    )
    test(
        "numpy.real_if_close(numpy.array([2+1e-15j]))",
        np.array([2.0]),
        label="real_if_close",
    )

    # --- Nonzero / flatnonzero ---
    test(
        "numpy.nonzero(numpy.array([0, 2, 0, 3]))", (np.array([1, 3]),), label="nonzero"
    )
    test(
        "numpy.flatnonzero(numpy.array([0, 2, 0, 3]))",
        np.array([1, 3]),
        label="flatnonzero",
    )

    # --- Rounding ---
    test(
        "numpy.rint(numpy.array([1.2, 1.5, 1.8, 2.5]))",
        np.array([1.0, 2.0, 2.0, 2.0]),
        label="rint",
    )
    test("numpy.fix(numpy.array([-1.5, 1.5]))", np.array([-1.0, 1.0]), label="fix")

    # --- Remainder ---
    test(
        "numpy.remainder(numpy.array([10]), numpy.array([3]))",
        np.array([1]),
        label="remainder",
    )
    test(
        "numpy.reciprocal(numpy.array([2.0, 4.0]))",
        np.array([0.5, 0.25]),
        label="reciprocal",
    )

    # --- Unwrap ---
    test(
        "numpy.unwrap(numpy.array([0.0, 3.0, 6.0, 9.0, 0.0, 3.0]), period=12.0)",
        np.array([0.0, 3.0, 6.0, 9.0, 12.0, 15.0]),
        label="unwrap phase wrapping",
    )

    # --- Constants ---
    test("numpy.pi", np.pi, label="numpy.pi constant")
    test("numpy.e", np.e, label="numpy.e constant")
    test("numpy.euler_gamma", np.euler_gamma, label="euler_gamma")
    test("numpy.newaxis is None", True, label="newaxis is None")


# ============================================================
# SANDBOX ESCAPE ATTEMPTS — all must be BLOCKED
# ============================================================
print("=" * 60)
print("SANDBOX ESCAPE TESTS (all must be BLOCKED)")
print("=" * 60)

# --- 10. Dunder attribute escapes ---
print("10. Dunder attribute escapes")
test("().__class__", expect_blocked=True, label="().__class__")
test("().__class__.__bases__", expect_blocked=True, label="().__class__.__bases__")
test(
    "().__class__.__bases__[0].__subclasses__()",
    expect_blocked=True,
    label="full subclass chain",
)
test("''.__class__.__mro__", expect_blocked=True, label="str.__class__.__mro__")
test("{}.__class__.__bases__", expect_blocked=True, label="dict.__class__.__bases__")
test("().__class__.__base__.__subclasses__()", expect_blocked=True, label="single base")
test(
    "[].__class__.__mro__[1].__subclasses__()",
    expect_blocked=True,
    label="list mro chain",
)
test("math.__class__", expect_blocked=True, label="math.__class__")
test("math.__dict__", expect_blocked=True, label="math.__dict__")
test("math.__globals__", expect_blocked=True, label="math.__globals__")
test(
    "numpy.__class__" if _HAS_NUMPY else "math.__class__",
    expect_blocked=True,
    label="module.__class__",
)

# --- 11. Dangerous builtins ---
print("11. Dangerous builtins")
test("open('/etc/passwd')", expect_blocked=True, label="open()")
test("eval('1+1')", expect_blocked=True, label="eval()")
test("exec('print(1)')", expect_blocked=True, label="exec()")
test("__import__('os')", expect_blocked=True, label="__import__()")
test("compile('1+1', '', 'eval')", expect_blocked=True, label="compile()")
test("globals()", expect_blocked=True, label="globals()")
test("locals()", expect_blocked=True, label="locals()")
test("getattr(math, 'sin')", expect_blocked=True, label="getattr()")
test("setattr(math, 'x', 1)", expect_blocked=True, label="setattr()")
test("delattr(math, 'pi')", expect_blocked=True, label="delattr()")
test("breakpoint()", expect_blocked=True, label="breakpoint()")
test("input()", expect_blocked=True, label="input()")
test("memoryview(b'')", expect_blocked=True, label="memoryview()")
test("bytearray(b'')", expect_blocked=True, label="bytearray()")
test("bytes(b'')", expect_blocked=True, label="bytes()")
test("help()", expect_blocked=True, label="help()")
test("exit()", expect_blocked=True, label="exit()")
test("quit()", expect_blocked=True, label="quit()")
test("copyright()", expect_blocked=True, label="copyright()")
test("license()", expect_blocked=True, label="license()")
test("credits()", expect_blocked=True, label="credits()")

# --- 12. Direct module access ---
print("12. Direct module access attempts")
test("os.system('whoami')", expect_blocked=True, label="os.system")
test("os.popen('ls')", expect_blocked=True, label="os.popen")
test("import os", expect_blocked=True, label="import os")
test("subprocess.run('whoami')", expect_blocked=True, label="subprocess.run")
test("sys.exit(0)", expect_blocked=True, label="sys.exit")
test("shutil.rmtree('/')", expect_blocked=True, label="shutil.rmtree")
test("socket.socket()", expect_blocked=True, label="socket")
test("ctypes.CDLL('libc.so.6')", expect_blocked=True, label="ctypes.CDLL")
test("builtins.open('/etc/passwd')", expect_blocked=True, label="builtins.open")
test("posix.system('ls')", expect_blocked=True, label="posix.system")
test("pty.spawn('/bin/sh')", expect_blocked=True, label="pty.spawn")

# --- 13. Expression-based exploits ---
print("13. Expression-based exploits")
test(
    "[x for x in ().__class__.__bases__[0].__subclasses__()]",
    expect_blocked=True,
    label="comp with dunder",
)
test("(lambda: 0).__code__", expect_blocked=True, label="lambda dunder")
test("type('', (), {})", expect_blocked=True, label="type() for class creation")
test("vars()", expect_blocked=True, label="vars()")
test("dir()", expect_blocked=True, label="dir()")
test("object()", expect_blocked=True, label="object()")
test("property()", expect_blocked=True, label="property()")
test("staticmethod(lambda: 0)", expect_blocked=True, label="staticmethod")
test("classmethod(lambda: 0)", expect_blocked=True, label="classmethod")
test("super()", expect_blocked=True, label="super()")
test("hasattr(math, 'sin')", expect_blocked=True, label="hasattr")
test("callable(open)", expect_blocked=True, label="callable")
test("isinstance(1, int)", expect_blocked=True, label="isinstance")
test("issubclass(int, object)", expect_blocked=True, label="issubclass")
test("id(1)", expect_blocked=True, label="id()")
test("hash('abc')", expect_blocked=True, label="hash()")
test("repr(1)", expect_blocked=True, label="repr()")
test("ascii('abc')", expect_blocked=True, label="ascii()")
test("format(1, 'x')", expect_blocked=True, label="format()")
test("iter([1, 2, 3])", expect_blocked=True, label="iter()")
test("next(iter([1]))", expect_blocked=True, label="next()")
test("slice(1, 2, 3)", expect_blocked=True, label="slice()")
test("complex(1, 2)", expect_blocked=True, label="complex()")
test("frozenset([1, 2])", expect_blocked=True, label="frozenset()")
test("bytes([65, 66])", expect_blocked=True, label="bytes()")
test("bytearray([65, 66])", expect_blocked=True, label="bytearray()")
test("memoryview(b'abc')", expect_blocked=True, label="memoryview()")
test("print('hello')", expect_blocked=True, label="print()")
test("type(1)", expect_blocked=True, label="type()")

# --- 14. numpy-specific dangerous functions (if numpy available) ---
if _HAS_NUMPY:
    print("14. numpy dangerous functions")
    test("numpy.load('evil.npy')", expect_blocked=True, label="numpy.load")
    test(
        "numpy.save('/tmp/out.npy', numpy.array([1]))",
        expect_blocked=True,
        label="numpy.save",
    )
    test(
        "numpy.savez('/tmp/out.npz', numpy.array([1]))",
        expect_blocked=True,
        label="numpy.savez",
    )
    test(
        "numpy.fromfile('/etc/passwd', dtype=float)",
        expect_blocked=True,
        label="numpy.fromfile",
    )
    test(
        "numpy.tofile(numpy.array([1]), '/tmp/out')",
        expect_blocked=True,
        label="numpy.tofile",
    )
    test(
        "numpy.genfromtxt('/etc/passwd')", expect_blocked=True, label="numpy.genfromtxt"
    )
    test("numpy.loadtxt('/etc/passwd')", expect_blocked=True, label="numpy.loadtxt")
    test(
        "numpy.savetxt('/tmp/out.txt', numpy.array([1]))",
        expect_blocked=True,
        label="numpy.savetxt",
    )
    test(
        "numpy.memmap('/tmp/mmap', dtype=float)",
        expect_blocked=True,
        label="numpy.memmap",
    )
    test("numpy.__class__", expect_blocked=True, label="numpy.__class__")
    test("np.load('evil.npy')", expect_blocked=True, label="np.load (alias)")
    test(
        "numpy.DataSource('https://evil.com')",
        expect_blocked=True,
        label="numpy.DataSource",
    )
    # numpy.fft.fft is now supported via nested attribute whitelist


# --- Instance method calls on return values ---
if _HAS_NUMPY:
    print()
    print("=" * 60)
    print("9zz. Instance method calls (e.g. array.tolist(), array.T)")
    print("=" * 60)

    import numpy as np

    test(
        "numpy.linspace(0, 10, 5).tolist()",
        np.linspace(0, 10, 5).tolist(),
        label="tolist",
    )
    test(
        "numpy.array([[1,2],[3,4]]).T",
        np.array([[1, 3], [2, 4]]),
        label=".T property",
    )
    test(
        "numpy.array([1.5, 2.7]).astype(int)",
        np.array([1, 2]),
        label="astype",
    )
    test(
        "numpy.array([3,1,2]).copy()",
        np.array([3, 1, 2]),
        label=".copy()",
    )
    test(
        "numpy.array([[1,2],[3,4]]).shape",
        (2, 2),
        label=".shape property",
    )
    test(
        "numpy.arange(6).reshape(2, 3)",
        np.arange(6).reshape(2, 3),
        label=".reshape()",
    )
    test(
        "numpy.array([1+2j, 3+4j]).real",
        np.array([1.0, 3.0]),
        label=".real property",
    )
    test(
        "numpy.array([[1,2,3],[4,5,6]]).diagonal()",
        np.array([1, 5]),
        label=".diagonal()",
    )
    # Reduction methods
    test("numpy.array([1,2,3]).sum()", 6, label=".sum()")
    test("numpy.array([1,2,3]).mean()", 2.0, label=".mean()")
    test("numpy.array([1,2,3]).prod()", 6, label=".prod()")
    test(
        "numpy.array([1,2,3,4,5]).std()",
        np.float64(np.std([1, 2, 3, 4, 5])),
        label=".std()",
    )
    test("numpy.array([1,2,3]).var()", np.float64(np.var([1, 2, 3])), label=".var()")
    test("numpy.array([3,1,5]).min()", 1, label=".min()")
    test("numpy.array([3,1,5]).max()", 5, label=".max()")
    test("numpy.array([True,False,True]).all()", False, label=".all()")
    test("numpy.array([True,False,True]).any()", True, label=".any()")
    test("numpy.array([1,2,3]).cumsum()", np.array([1, 3, 6]), label=".cumsum()")
    test("numpy.array([1,2,3]).cumprod()", np.array([1, 2, 6]), label=".cumprod()")
    # More methods
    test("len(numpy.array([0,2,0,3]).nonzero()[0])", 2, label=".nonzero()")
    test("numpy.array([1,2,3]).dot(numpy.array([4,5,6]))", 32, label=".dot()")
    test("numpy.array([1.5, 2.7]).item(0)", 1.5, label=".item()")
    test("numpy.array([1,2,3]).view()", np.array([1, 2, 3]), label=".view()")
    test(
        "numpy.array([[1,2],[3,4]]).swapaxes(0,1)",
        np.array([[1, 3], [2, 4]]),
        label=".swapaxes()",
    )
    test("numpy.array([1,2,3]).searchsorted(2)", 1, label=".searchsorted()")
    # Chained method calls
    test(
        "numpy.array([1,2,3,4,5]).reshape(5,1).sum()",
        15,
        label="chain: .reshape().sum()",
    )
    test(
        "numpy.arange(6).reshape(2,3).T.flatten().tolist()",
        [0, 3, 1, 4, 2, 5],
        label="chain: .reshape().T.flatten().tolist()",
    )
    test(
        "numpy.eye(3).diagonal().sum()",
        3.0,
        label="chain: .diagonal().sum()",
    )
    test(
        "numpy.array([[1,2],[3,4]]).T.copy().reshape(4).tolist()",
        [1, 3, 2, 4],
        label="chain: .T.copy().reshape().tolist()",
    )
    test(
        "numpy.array([1.5, 2.7, 3.1]).round().astype(int).tolist()",
        [2, 3, 3],
        label="chain: .round().astype().tolist()",
    )

    # --- Lambda & callback-based functions ---
    print()
    print("=" * 60)
    print("9zy. Lambda & callback-based functions")
    print("=" * 60)

    test("(lambda x: x**2)(5)", 25, label="basic lambda")
    test(
        "(lambda x: (lambda y: x + y))(1)(2)",
        3,
        label="curried lambda",
    )
    test(
        "sorted([3, 1, 2], key=lambda x: -x)",
        [3, 2, 1],
        label="sorted with lambda key",
    )
    test(
        "list(map(lambda x: x * 2, [1, 2, 3]))",
        [2, 4, 6],
        label="map with lambda",
    )
    test(
        "list(filter(lambda x: x > 2, [1, 3, 5]))",
        [3, 5],
        label="filter with lambda",
    )
    test(
        "sorted(['bb', 'a', 'ccc'], key=lambda s: len(s))",
        ["a", "bb", "ccc"],
        label="sorted with len key",
    )
    test(
        "[(lambda y: y * 2)(x) for x in range(3)]",
        [0, 2, 4],
        label="lambda in list comp",
    )
    test(
        "list(map(lambda x: x**2, filter(lambda x: x > 1, [1, 2, 3])))",
        [4, 9],
        label="nested lambda in map/filter",
    )
    # apply_along_axis
    test(
        "numpy.apply_along_axis(lambda x: x.sum(), 1, numpy.array([[1, 2], [3, 4]]))",
        np.array([3, 7]),
        label="apply_along_axis with lambda",
    )
    test(
        "numpy.apply_along_axis(lambda x: x.max(), 0, numpy.array([[1, 5], [3, 2]]))",
        np.array([3, 5]),
        label="apply_along_axis lambda.max()",
    )
    # vectorize
    test(
        "numpy.vectorize(lambda x: x**2)(numpy.array([1, 2, 3]))",
        np.array([1, 4, 9]),
        label="vectorize",
    )
    test(
        "numpy.frompyfunc(lambda x: x * 2, 1, 1) is not None",
        True,
        label="frompyfunc returns ufunc",
    )


# --- 15. Tricky edge-case escapes ---
print("15. Tricky edge-case escapes")
# Walrus operator (NamedExpr)
test("(a := 1)", expect_blocked=True, label="walrus operator")
# f-strings
test("f'{1+1}'", expect_blocked=True, label="f-string")
# Methods on literals (base is Constant, not a module Name)
test("'hello'.format(1)", expect_blocked=True, label="str method call")
test("[1,2,3].index(2)", expect_blocked=True, label="list method call")
# Format-string dunder injection
test("'{0.__class__}'.format(1)", expect_blocked=True, label="format dunder")
# Comprehension iter using dunder chain
test(
    "[x for x in [1].__class__.__bases__]",
    expect_blocked=True,
    label="comp iter dunder",
)
# Nested comprehension with dunder in body
test(
    "[[y.__class__ for y in [1]] for x in [1]]",
    expect_blocked=True,
    label="nested comp dunder",
)
# Short-circuit (validator checks ALL branches regardless of runtime)
test("False and __import__('os')", expect_blocked=True, label="short-circuit import")
test(
    "1 if False else open('/etc/passwd')",
    expect_blocked=True,
    label="ternary dead branch",
)
# Dict unpack with import
test("{**{'a': __import__('os')}}", expect_blocked=True, label="dict unpack import")
# Unicode homoglyph (fullwidth characters normalized to ASCII by Python)
test("ｏｐｅｎ('/etc/passwd')", expect_blocked=True, label="unicode homoglyph open")
# Percent format (works, but harmless — just string ops)
test("'%d' % 42", "%d" % 42, label="percent format harmless")
# Lambda escape attempts (body goes through full AST validation)
test("(lambda: __import__('os'))()", expect_blocked=True, label="lambda __import__")
test("(lambda x: x.__class__)(1)", expect_blocked=True, label="lambda dunder")
test(
    "numpy.apply_along_axis(lambda x: __import__('os'), 0, numpy.array([1]))",
    expect_blocked=True,
    label="lambda in apply_along_axis",
)
test(
    "(lambda: lambda: __import__('os'))()()",
    expect_blocked=True,
    label="nested lambda escape",
)

# Classic PR#34 exploit payload — Subscript+Call chain
test(
    "[x for x in (1).__class__.__base__.__subclasses__() if 1][0]()",
    expect_blocked=True,
    label="classic dunder subclass chain",
)

# Star unpack with safe function
test("sum(*[[1,2,3]])", 6, label="star unpack sum")


# --- 16. Statement / control flow / print / assignment ---
print("16. Statements, print, variable creation")
# Statements — all rejected at ast.parse(mode="eval") level
for stmt, label in [
    ("a = 1", "assignment"),
    ("if True: 1", "if stmt"),
    ("for x in [1]: x", "for stmt"),
    ("while True: 1", "while stmt"),
    ("def f(): pass", "def stmt"),
    ("import os", "import stmt"),
    ("pass", "pass stmt"),
    ("del x", "del stmt"),
    ("assert True", "assert stmt"),
    ("raise Exception()", "raise stmt"),
    ("with open('/tmp'): pass", "with stmt"),
    ("1; 2", "semicolon"),
    ("1+1\n2+2", "multi expression"),
]:
    test(stmt, expect_blocked=True, label=label)

# print — blocked by Call/Name check
test("print('hello')", expect_blocked=True, label="print call")
test("print", expect_blocked=True, label="print name reference")
# print hidden in list/ternary
test("[print, sum][1]([1,2,3])", expect_blocked=True, label="print buried in list")
test("sum if True else print", expect_blocked=True, label="print in ternary")
# lambda
# yield (expression form, Python 3.3+)
test("(yield 1)", expect_blocked=True, label="yield expression")
# __debug__ constant
test("__debug__", expect_blocked=True, label="__debug__ constant")


# ============================================================
# SUMMARY
# ============================================================
print()
print("=" * 60)
total = PASS + FAIL
print(f"RESULTS: {PASS}/{total} passed, {FAIL}/{total} failed")
if FAIL == 0:
    print("All tests passed!")
else:
    print(f"{FAIL} test(s) FAILED — review output above")
    sys.exit(1)
