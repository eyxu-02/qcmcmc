"""
Unit and regression test for the qcmcmc package.
"""

# Import package, test suite, and other packages as needed
import sys

import pytest

import qcmcmc


def test_qcmcmc_imported():
    """Sample test, will always pass so long as import statement worked."""
    assert "qcmcmc" in sys.modules
