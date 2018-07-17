# -*- coding: utf-8 -*-
import nose
import pandas.util.testing as tm

import numpy as np
import pandas as pd

from ..frame import ZFrame

N = 100
data = np.random.randn(N,3)
index = pd.date_range(start="2000", freq="D", periods=N)
df = ZFrame(data, columns=['dale', 'bob', 'frank'], index=index)
print(isinstance(df, pd.DataFrame))

if __name__ == '__main__':
    nose.runmodule(argv=[__file__, '-vvs', '-x', '--pdb', '--pdb-failure'],
                   exit=False)
