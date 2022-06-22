import pytest
import tail
from distutils import dir_util
import os


@pytest.fixture
def datadir(tmpdir, request):
    '''
    https://stackoverflow.com/questions/29627341/pytest-where-to-store-expected-data/29631801#29631801

    Fixture responsible for searching a folder with the same name of test
    module and, if available, moving all contents to a temporary directory so
    tests can use them freely.
    '''
    filename = request.module.__file__
    test_dir, _ = os.path.splitext(filename)

    if os.path.isdir(test_dir):
        dir_util.copy_tree(test_dir, str(tmpdir))

    return tmpdir


@pytest.mark.parametrize('limit', range(1,15))
def test_tail (datadir, limit):
    fname = os.path.join(datadir, 'testdata')
    with open(fname) as f:
        t = tail.Tail(f, limit=limit)
        x = t.tail().split()
    if limit == 14:
        limit = 13  # file is only 13 lines long, testing edge case
    assert len(x) == limit
    