""" Test functions for linalg module using the matrix class."""

import numpy as np
from numpy.linalg.tests.test_linalg import (
    CondCases,
    DetCases,
    EigCases,
    EigvalsCases,
    InvCases,
    LinalgCase,
    LinalgTestCase,
    LstsqCases,
    PinvCases,
    SolveCases,
    SVDCases,
)
from numpy.linalg.tests.test_linalg import TestQR as _TestQR
from numpy.linalg.tests.test_linalg import (
    _TestNorm2D,
    _TestNormDoubleBase,
    _TestNormInt64Base,
    _TestNormSingleBase,
    apply_tag,
)

CASES = []

# square test cases
CASES += apply_tag(
    "square",
    [
        LinalgCase(
            "0x0_matrix",
            np.empty((0, 0), dtype=np.double).view(np.matrix),
            np.empty((0, 1), dtype=np.double).view(np.matrix),
            tags={"size-0"},
        ),
        LinalgCase(
            "matrix_b_only", np.array([[1.0, 2.0], [3.0, 4.0]]), np.matrix([2.0, 1.0]).T
        ),
        LinalgCase(
            "matrix_a_and_b",
            np.matrix([[1.0, 2.0], [3.0, 4.0]]),
            np.matrix([2.0, 1.0]).T,
        ),
    ],
)

# hermitian test-cases
CASES += apply_tag(
    "hermitian",
    [
        LinalgCase("hmatrix_a_and_b", np.matrix([[1.0, 2.0], [2.0, 1.0]]), None),
    ],
)
# No need to make generalized or strided cases for matrices.


class MatrixTestCase(LinalgTestCase):
    TEST_CASES = CASES


class TestSolveMatrix(SolveCases, MatrixTestCase):
    pass


class TestInvMatrix(InvCases, MatrixTestCase):
    pass


class TestEigvalsMatrix(EigvalsCases, MatrixTestCase):
    pass


class TestEigMatrix(EigCases, MatrixTestCase):
    pass


class TestSVDMatrix(SVDCases, MatrixTestCase):
    pass


class TestCondMatrix(CondCases, MatrixTestCase):
    pass


class TestPinvMatrix(PinvCases, MatrixTestCase):
    pass


class TestDetMatrix(DetCases, MatrixTestCase):
    pass


class TestLstsqMatrix(LstsqCases, MatrixTestCase):
    pass


class _TestNorm2DMatrix(_TestNorm2D):
    array = np.matrix


class TestNormDoubleMatrix(_TestNorm2DMatrix, _TestNormDoubleBase):
    pass


class TestNormSingleMatrix(_TestNorm2DMatrix, _TestNormSingleBase):
    pass


class TestNormInt64Matrix(_TestNorm2DMatrix, _TestNormInt64Base):
    pass


class TestQRMatrix(_TestQR):
    array = np.matrix