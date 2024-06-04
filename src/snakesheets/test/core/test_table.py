# pylint: disable=comparison-with-itself,redefined-outer-name

from collections.abc import Iterable
from itertools import product

import pytest

from snakesheets.core import table
from snakesheets.core.exception import InvalidInput


@pytest.fixture
def regularArrays():
    """Arrays with an equal value count per row"""
    return (
        [[1]],
        [[1], [2]],
        [[1, 'two'], [3.0, 4]],
        [[True, 2.0, 3], [4, '5', 6j], [7j, 'eight', 9]],
        [[1, 2.0, 3, 4], [5, '6', 1+7j, 8], [9, 'ten', -11, 12.0]],
        [[1, 2.0, 3], [4, 5, '6'], [1+7j, 8, 9], ['ten', -11, 12.0]],
    )


@pytest.fixture
def jaggedArrays():
    """Arrays with an unequal value count per row"""
    return (
        [[1], [2, 3]],
        [[1, True], ['string']],
        [[1, '2'], [3], [4, 'five', 6]],
        [[True, 2, 3.0, 'four', 5j], ['6'], [7, 8]],
        [[1.0, 2j], ['3'], [4+4j, 5.0, 6, 'seven', 8]],
        [[False, 2, 'three'], [4, 5.0, 6, '7'], [8j, 9.0, 10], [11, 12.0]]
    )


@pytest.fixture
def validDimensions():
    """Collection of valid array dimensions for use in testing"""
    return ((1, 1), (3, 2), (4, 9), (100, 1), (1, 100))


@pytest.fixture
def invalidData() -> dict[str, Iterable]:
    """Problematic values for data in Table.__init__

    A dict mapping substrings of intended exception messages to a collection
    of values that should provoke such errors
    """
    nonListValues = [True, 'data', 1, 1.0, (), {}, object()]
    return {
        'data must be a list': nonListValues,
        'rows must be lists': [[x] * 3 for x in nonListValues],
        'data must have at least 1 row': ([]),
        'data must have at least 1 column': ([[]], [[] * 2], [[] * 3])
    }


@pytest.fixture
def invalidDimensions() -> dict[str, Iterable]:
    """Problematic values for dimensions in Table.__init__

    A dict mapping substrings of intended exception messages to a collection
    of values that should provoke such errors
    """
    nonIntegerValues = [None, 1.5, '1', object(), 1j, [], {}, (1,)]
    return {
        'dimensions must be a tuple': (1, 1.5, [], {}, [1, 2], 'xy'),
        'dimensions must be a tuple in the form (rows, columns)': (
            (), (1,), (1, 1, 1)
        ),
        'must be an integer': [(x, x) for x in nonIntegerValues],
        'number of rows must be an integer': [
            (x, 1) for x in nonIntegerValues
        ],
        'number of columns must be an integer': [
            (1, x) for x in nonIntegerValues
        ],
        'must have at least 1 row': ((0, 1), (0, 5)),
        'must have at least 1 column': ((1, 0), (5, 0)),
        'must have at least 1': ((0, 0),),
        'table cannot have a negative number of rows': ((-1, 1), (-5, 1)),
        'table cannot have a negative number of columns': ((1, -5), (1, -5)),
    }


@pytest.fixture
def invalidStrIndicies():
    """Problematic values for index in Table.__getattr__with type = str"""
    return {}


def testInitNoArgs():
    testTable = table.Table()
    assert testTable.data == [[None]]
    assert testTable.columns == 1
    assert testTable.rows == 1


def testInitRegularArray(regularArrays):
    for array in regularArrays:
        testTable = table.Table(array)
        assert len(array) == testTable.rows
        for row in testTable.data:
            assert len(row) == testTable.columns
            assert len(row) == len(array[0])


def testInitJaggedArray(jaggedArrays):
    testParams = product(jaggedArrays, ({}, {'defaultValue': 'test'}))
    for array, kwargs in testParams:
        testTable = table.Table(array, **kwargs)
        maxRowLength = max(len(row) for row in array)

        assert testTable.data != array
        for y, row in enumerate(array):
            for x, element in enumerate(row):
                assert testTable[x, y] == element
            for x in range(len(row), maxRowLength):
                if kwargs:
                    assert testTable[x, y] == kwargs['defaultValue']
                else:
                    assert testTable[x, y] is None
        assert testTable.rows == len(array)
        assert testTable.columns == maxRowLength
        for row in testTable.data:
            assert len(row) == testTable.columns


def testInitRowsColumns(validDimensions):
    testParams = product(validDimensions, ({}, {'defaultValue': 'test'}))
    for dimensions, kwargs in testParams:
        print(dimensions)
        testTable = table.Table(dimensions=dimensions, **kwargs)
        rows, columns = dimensions
        assert testTable.rows == rows
        assert testTable.columns == columns
        for y, x in product(range(rows), range(columns)):
            if kwargs:
                assert testTable[x, y] == kwargs['defaultValue']
            else:
                assert testTable[x, y] is None


def testEquals(regularArrays, jaggedArrays, validDimensions):
    for data in None, *regularArrays, *jaggedArrays:
        tableA = table.Table(data=data)
        tableB = table.Table(data=data)
        assert tableA == tableB

    testParams = product(validDimensions, ({}, {'defaultValue': 'test'}))
    for dimensions, kwargs in testParams:
        tableA = table.Table(dimensions=dimensions, **kwargs)
        tableB = table.Table(dimensions=dimensions, **kwargs)
        assert tableA == tableB


def testEqualsSelf(regularArrays, jaggedArrays, validDimensions):
    for data in None, *regularArrays, *jaggedArrays:
        testTable = table.Table(data=data)
        assert testTable == testTable

    testParams = product(validDimensions, ({}, {'defaultValue': 'test'}))
    for dimensions, kwargs in testParams:
        testTable = table.Table(dimensions=dimensions, **kwargs)
        assert testTable == testTable


def testInitInvalidData(invalidData):
    for errorSubstring, testData in invalidData.items():
        for data in testData:
            with pytest.raises(InvalidInput) as exceptionInfo:
                table.Table(data=data)
            assert errorSubstring in str(exceptionInfo.value)


def testInitInvalidDimensions(invalidDimensions):
    testParams = product(invalidDimensions.items(),
                         ({}, {'defaultValue': 'test'}))
    for (errorSubstring, testDimensions), kwargs in testParams:
        for dimensions in testDimensions:
            with pytest.raises(InvalidInput) as exceptionInfo:
                table.Table(dimensions=dimensions, **kwargs)
            assert errorSubstring in str(exceptionInfo.value)
