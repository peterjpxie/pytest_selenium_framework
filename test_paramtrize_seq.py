import pytest


@pytest.mark.parametrize("x", ["Chrome", "Firefox"])
class TestParamtrizeSeq:

    def test_a(self, x):
        pass

    def test_b(self, x):
        pass


"""original out sequence:
test_paramtrize_seq.py::TestParamtrizeSeq::test_a[Chrome] PASSED  
test_paramtrize_seq.py::TestParamtrizeSeq::test_a[Firefox] PASSED 
test_paramtrize_seq.py::TestParamtrizeSeq::test_b[Chrome] PASSED  
test_paramtrize_seq.py::TestParamtrizeSeq::test_b[Firefox] PASSED  

out sequence with pytest_collection_modifyitems() change in conftest.py:
test_paramtrize_seq.py::TestParamtrizeSeq::test_a[Chrome] PASSED  
test_paramtrize_seq.py::TestParamtrizeSeq::test_b[Chrome] PASSED  
test_paramtrize_seq.py::TestParamtrizeSeq::test_a[Firefox] PASSED 
test_paramtrize_seq.py::TestParamtrizeSeq::test_b[Firefox] PASSED 
"""
