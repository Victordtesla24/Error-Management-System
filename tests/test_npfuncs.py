import numpy as np
import pandas._testing as tm
from pandas import date_range


class TestSplit:
    def test_split_non_utc(self):
        # GH#14042
        indices = date_range("2016-01-01 00:00:00+0200", freq="s", periods=10)
        result = np.split(indices, indices_or_sections=[])[0]
        expected = indices._with_freq(None)
        tm.assert_index_equal(result, expected)
