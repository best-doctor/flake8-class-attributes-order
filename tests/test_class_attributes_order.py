from conftest import run_validator_for_test_file


def test_always_ok_for_empty_file():
    errors = run_validator_for_test_file('errored.py')
    assert len(errors) == 2
