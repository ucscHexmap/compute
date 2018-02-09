import unittest
import pandas as pd
import numpy as np
import spatial

class Test_dynLayoutAware(unittest.TestCase):

    def test_inverse_euc_distance(s):
        xys = pd.DataFrame([
            [0, 0],
            [3, 4],
            [5, 12],
        ])

        # Done on a calculator.
        realEucDistance = [
            [0,5,13],
            [5,0,8.2462],
            [13,8.2462,0],
        ]

        realInvEucDistance = 1 / (1 + np.array(realEucDistance))

        test_passes = np.allclose(
            realInvEucDistance,
            spatial.inverseEucDistance(xys)
        )

        s.assertTrue(
            test_passes,
            "Inverse Euclidean distance function failed against" +\
            "hand calculation."
        )

if __name__ == '__main__':
    unittest.main()
