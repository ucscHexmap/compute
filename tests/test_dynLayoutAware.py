import unittest
import pandas as pd
import numpy as np
import leesL

class Test_dynLayoutAware(unittest.TestCase):

    A = np.concatenate(
        [
        np.repeat(0, 10),
        np.repeat(1, 4),
        np.repeat(0, 2),
        np.repeat(1, 5),
        np.repeat(0, 1),
        np.repeat(1, 2),
        np.repeat(2, 2),
        np.repeat(1, 3),
        np.repeat(2, 3),
        np.repeat(1, 2),
        np.repeat(2, 2),
        np.repeat(1, 1)
        ]
    )

    B = np.array(
        [
            0,1,0,0,
            0,0,1,0,1,
            1,1,0,1,1,1,
            1,1,1,1,2,0,0,
            2,1,2,0,1,0,
            2,2,1,1,0,
            2,2,1,0
        ]
    )

    C = np.array(
        [
            0,1,0,1,
            1,0,1,1,0,
            0,2,0,2,0,1,
            0,1,1,1,1,2,0,
            2,1,2,0,1,0,
            1,1,1,2,1,
            0,2,1,0
        ]
    )

    hexSim = pd.DataFrame(
        np.reshape(
            np.repeat(0, 37 * 37),
            (37, 37)
        )
    )

    edges = [
        [2, 5, 6], # 1
        [1, 3, 6, 7], # 2
        [2, 4, 7, 8], # 3
        [3, 8, 9], # 4
        [1, 6, 10, 11], # 5
        [1, 2, 5, 7, 11, 12], # 6
        [2, 3, 6, 8, 12, 13], # 7
        [3, 4, 7, 9, 13, 14], # 8
        [4, 8, 14, 15], # 9
        [5, 11, 16, 17], # 10
        [5, 6, 10, 12, 17, 18], # 11
        [6, 7, 11, 13, 18, 19], # 12
        [7, 8, 12, 14, 19, 20], # 13
        [8, 9, 13, 15, 20, 21], # 14
        [9, 14, 21, 22], # 15
        [10, 17, 23], #16
        [10, 11, 16, 18, 23, 24], # 17
        [11, 12, 17, 19, 24, 25], # 18
        [12, 13, 18, 20, 25, 26], # 19
        [13, 14, 19, 21, 26, 27], # 20
        [14, 15, 20, 22, 27, 28], # 21
        [15, 21, 28], # 22
        [16, 17, 24, 29], # 23
        [17, 18, 23, 25, 29, 30], # 24
        [18, 19, 24, 26, 30, 31], # 25
        [19, 20, 25, 27, 31, 32], # 26
        [20, 21, 26, 28, 32, 33], # 27
        [21, 22, 27, 33], # 28
        [23, 24, 30, 34], # 29
        [24, 25, 29, 31, 34, 35], # 30
        [25, 26, 30, 32, 35, 36], # 31
        [26, 27, 31, 33, 36, 37], # 32
        [28, 27, 32, 37], # 33
        [29, 30, 35], # 34
        [30, 31, 34, 36], # 35
        [31, 32, 35, 37], # 36
        [32, 33, 36] # 37
    ]

    for i in range(37):
        neighbors = map(lambda x: x-1, edges[i])
        hexSim.loc[i, neighbors] = 1

    attrs = pd.DataFrame({"A": A, "B": B, "C": C})
    attrs = leesL.ztransDF(attrs)
    #hexSim.values[[np.arange(37)]*2] = 1
    hexSim = leesL.rowNormalize(hexSim)

    leesL.leesL(hexSim, attrs)

    def make_edges_hex_neigh(self):
        empty_arr = [
            range(4),
            range(5),
            range(6),
            range(7),
            range(6),
            range(5),
            range(4),
        ]
        
        def up_left_upper(row_n, col_n):
            row = row_n-1
            col_n = col_n-1
            return row, col_n

        def up_right_upper(row_n, col_n):
            row = row_n-1
            col_n = col_n
            return row, col_n

        def down_right_upper(row_n, col_n):
            return row_n+1, col_n+1

        def down_left_upper(row_n, col_n):
            return row_n+1, col_n
        
        def left(row_n, col_n):
            return row_n, col_n-1

        def right(row_n, col_n):
            return row_n, col_n + 1
        
        def down_right_lower(row_n, col_n):
            return row_n+1, col_n
        
        def down_left_lower(row_n, col_n):
            return row_n+1, col_n-1
        
        def up_left_lower(row_n, col_n):
            row = row_n-1
            col_n = col_n
            return row, col_n

        def up_right_lower(row_n, col_n):
            row = row_n-1
            col_n = col_n + 1
            return row, col_n
        
        neighborFsU = [
            up_left_upper,
            up_right_upper,
            left,
            right,
            down_left_upper,
            down_right_upper
        ]

        neighborFsL = [
            up_left_lower,
            up_right_lower,
            left,
            right,
            down_left_lower,
            down_right_lower
        ]

        indecies = {}

        for row_n, row in enumerate(empty_arr):
            for place in row:
                neig_arr = []
                if row_n > 3:
                    neighborFs = neighborFsL
                else:
                    neighborFs = neighborFsU
                #row_n, place = 6,3
                for neighborF in neighborFs:
                    try:

                        neighborRow, neighborPlace = neighborF(row_n,
                                                            place)
                        #print neighborRow, neighborPlace
                        if neighborPlace <0 or neighborRow<0:
                            raise IndexError
                        empty_arr[neighborRow][neighborPlace]
                        neig_arr.append((neighborRow, neighborPlace))
                    except IndexError:
                        pass
                indecies[(row_n, place)] = neig_arr

        # Tough edge cases (corners of widest row).
        indecies[(3, 0)].pop(indecies[(3, 0)].index((4, 1)))
        indecies[(3, 6)].append((4, 5))

        df = pd.DataFrame(
            np.reshape(np.repeat(0, 37 * 37), (37,37)),
            index=indecies.keys(),
            columns=indecies.keys()
        )

        for node in indecies.keys():
            edges = indecies[node]
            for edge in edges:
                df.loc[node, edge] = 1

        df = df.loc[sorted(df.columns),sorted(df.columns)]
        return df


    def test_leesL_computation(self):
        simDF = self.make_edges_hex_neigh(self)
        attrDF = self.attrs

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
        passes = np.allclose(
            realInvEucDistance,
            leesL.inverseEucDistance(xys)
        )
        s.assertTrue(passes,"Inverse Euclidean distance function "
                            "failed against hand calculation." )

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
        passes = np.allclose(
            realInvEucDistance,
            leesL.inverseEucDistance(xys)
        )
        s.assertTrue(passes,"Inverse Euclidean distance function "
                            "failed against hand calculation." )

if __name__ == '__main__':
    unittest.main()
