import unittest
import pandas as pd
import numpy as np
import leesl
from itertools import product

class Test_leesl(unittest.TestCase):

    # Correct values came from the R implementation of
    # leesl in the package spdep Version 0.6-15.
    known_answers = np.array(
        [
            [.358653846, 0, 0, -0.044989875,  0.184495192],
            [0, 1,  -1, .0678401,  -.0193506],
            [0,  -1,   1, -.0678401, .0193506],
            [-.0449899, .0678401,  -.0678401, .1385315, -.135423],
            [.184495,  -.01935059,   .01935059, -.1354234, .409495192]
        ]
    )

    # Attributes with known lees l values. 2d array represents
    # squares on a 6x6 grid.
    A = np.array([
        [0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 0],
        [0, 1, 1, 1, 1, 0],
        [0, 1, 1, 1, 1, 0],
        [0, 1, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 0],
    ])
    B = np.array([
        [0, 1, 0, 1, 0, 1],
        [1, 0, 1, 0, 1, 0],
        [0, 1, 0, 1, 0, 1],
        [1, 0, 1, 0, 1, 0],
        [0, 1, 0, 1, 0, 1],
        [1, 0, 1, 0, 1, 0],
    ])
    C = np.array([
        [1, 0, 1, 0, 1, 0],
        [0, 1, 0, 1, 0, 1],
        [1, 0, 1, 0, 1, 0],
        [0, 1, 0, 1, 0, 1],
        [1, 0, 1, 0, 1, 0],
        [0, 1, 0, 1, 0, 1],
    ])
    D = np.array([
        [0, 1, 0, 0, 0, 1],
        [0, 1, 0, 0, 0, 1],
        [0, 1, 0, 0, 1, 0],
        [1, 0, 0, 0, 1, 0],
        [1, 0, 0, 1, 0, 0],
        [0, 0, 0, 1, 0, 0],
    ])
    E = np.array([
        [0, 0, 1, 1, 1, 0],
        [0, 0, 1, 1, 1, 0],
        [0, 0, 1, 1, 0, 0],
        [0, 1, 1, 1, 0, 0],
        [0, 1, 1, 0, 0, 0],
        [1, 1, 1, 0, 0, 0],
    ])

    known_attrs = pd.DataFrame(
        {"A": A.flatten(),
         "B": B.flatten(),
         "C": C.flatten(),
         "D": D.flatten(),
         "E": E.flatten()}
    )

    def test_leesl_pandas(self):
        spatial_weight_matrix = self.checkerboard_similarity()
        attrs = self.known_attrs
        answers = self.known_answers

        passes = np.allclose(
            answers,
            leesl.stats_matrix(attrs, spatial_weight_matrix)
        )
        self.assertTrue(passes)

    def test_leesl_numpy(self):
        spatial_weight_matrix = self.checkerboard_similarity().values
        attrs = self.known_attrs.values
        answers = self.known_answers

        passes = np.allclose(
            answers,
            leesl.stats_matrix(attrs, spatial_weight_matrix)
        )
        self.assertTrue(passes)

    def checkerboard_similarity(self):
        """Make a 6x6 grid where any square sharing an edge is
        connected."""
        # Making a 6x6 Square grid. (0, 0) in top left corner.
        board_length = 6

        # Dictionary to hold (row, col) -> similarity
        square_sim_dict = {}

        # Functions to run through at each square producing
        # neighbors.
        def neighbors(row_n, col_n):
             return [
                (row_n + 1, col_n), #down
                (row_n - 1, col_n), #up
                (row_n, col_n + 1), #right
                (row_n, col_n - 1), #left
            ]

        def on_board(row_col, length=6):
            return \
                not (
                    (row_col[0] > length-1 or row_col[1] > length-1)
                    or (row_col[0] < 0 or row_col[1] < 0)
                )

        board_indecies = [range(board_length), range(board_length)]
        for row_n, col_n in product(*board_indecies):
            neighbors_on_board = filter(
                on_board,
                neighbors(row_n, col_n)
            )
            square_sim_dict[(row_n, col_n)] = neighbors_on_board

        # Throw it in a dataframe.
        df = pd.DataFrame(
            np.reshape(np.repeat(0, 36*36), (36, 36)),
            index=square_sim_dict.keys(),
            columns=square_sim_dict.keys()
        )
        for node in square_sim_dict.keys():
            edges = square_sim_dict[node]
            for edge in edges:
                df.loc[node, edge] = 1

        # Make sure the ordering is properly defined.
        simdf = df.loc[sorted(df.columns), sorted(df.columns)]

        return simdf

    def test_L_numpy(self):
        spatial_weight_matrix = self.checkerboard_similarity()
        attrs = self.known_attrs
        answers = self.known_answers


        z_attrs = (attrs.values - attrs.values.mean(axis=0)) / \
                 attrs.values.std(axis=0,ddof=0)

        passes = np.allclose(
            answers,
            leesl.L(z_attrs, spatial_weight_matrix)
        )
        self.assertTrue(passes)

    def test_L_pandas(self):
        spatial_weight_matrix = self.checkerboard_similarity()
        attrs = self.known_attrs
        answers = self.known_answers


        z_attrs = (attrs - attrs.mean(axis=0)) / \
                 attrs.std(axis=0, ddof=0)

        passes = np.allclose(
            answers,
            leesl.L(z_attrs, spatial_weight_matrix)
        )
        self.assertTrue(passes)

if __name__ == '__main__':
    unittest.main()
