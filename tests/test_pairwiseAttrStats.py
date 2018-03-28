import unittest
import pairwiseStats as stats
import numpy as np

class Test_pairwiseStats(unittest.TestCase):

    binData = np.concatenate(
        [np.repeat(0, 201),
         np.repeat(1, 194)],
        axis=0
    )

    catData = np.concatenate(
        [np.repeat(0, 60),
         np.repeat(1, 54),
         np.repeat(2, 46),
         np.repeat(3, 41),
         np.repeat(0, 40),
         np.repeat(1, 44),
         np.repeat(2, 53),
         np.repeat(3, 57),
         ],
        axis=0
    )

    def test_only_one_group_binCont(self):

        bin = np.repeat(1, 15)
        cont = np.array(range(15))
        res = stats.binContTest(bin, cont)
        self.assertTrue(np.isnan(res), res)

    def test_only_one_group_catCont(self):
        cat = np.repeat(1, 15)
        cont = np.array(range(15))
        res = stats.catContTest(cat, cont)
        self.assertTrue(np.isnan(res), res)

    def test_only_one_group_binBin(self):

        bin = np.repeat(1, 15)
        bin2 = self.binData
        res = stats.binBinTest(bin, bin2)
        self.assertTrue(np.isnan(res), res)

    def test_only_one_value_catCont(self):
        cat = self.catData
        cont = np.repeat(4, 400)
        res = stats.catContTest(cat, cont)
        self.assertTrue(np.isnan(res), res)

    def test_only_one_value_binCont(self):

        bin = self.binData
        cont = np.repeat(1, 34)
        res = stats.binContTest(bin, cont)
        self.assertTrue(np.isnan(res), res)

    def test_only_one_value_contCont(self):

        cont1 = np.array(range(34))
        cont = np.repeat(1, 34)
        res = stats.binContTest(cont1, cont)
        self.assertTrue(np.isnan(res), res)

    def test_all_nas_after_filter_binCont(self):

        bin = np.repeat(np.nan, 15)
        cont = np.array(range(15))
        res = stats.binContTest(bin, cont)
        self.assertTrue(np.isnan(res), res)

    def test_all_nas_after_filter_catCont(self):

        cat = np.repeat(np.nan, 15)
        cont = np.array(range(15))
        res = stats.catContTest(cat, cont)
        self.assertTrue(np.isnan(res), res)

    def test_all_nas_after_filter_catBinCatCat(self):

        bin = np.repeat(np.nan, 15)
        cont = np.array(range(15))
        res = stats.catBinOrCatCatTest(bin, cont)
        self.assertTrue(np.isnan(res), res)

    def test_all_nas_after_filter_contCont(self):

        cont1 = np.repeat(np.nan, 15)
        cont2 = np.array(range(15))
        res = stats.contContTest(cont1, cont2)
        self.assertTrue(np.isnan(res), "not na: " + str(res))

    def test_all_nas_after_filter_binBinCatBin(self):

        bin = np.repeat(np.nan, 15)
        cont = np.array(range(15))
        res = stats.catBinOrCatCatTest(bin, cont)
        self.assertTrue(np.isnan(res), res)

    def test_contingency_table(self):
        """Generate a contingency table and check counts."""
        correct = { (0, 0): 60, (0, 1): 54, (0, 2): 46, (0, 3): 41,
                    (1, 0): 40, (1, 1): 44, (1, 2): 53, (1, 3): 57}

        table = stats.contingencyTable(self.binData, self.catData)
        for indecies in correct.keys():
            self.assertTrue(
                table[indecies] == correct[indecies],
                "indecies: " + str(indecies) + " of contingency table "
                " are incorrect. Actual count is " +
                str(table[indecies]) + " true count is " +
                str(correct[indecies])
            )

    def test_contingency_table_remove_cat(self):
        """Simulates all of one category getting removed."""
        binData = np.concatenate(
            [np.repeat(0, 147),
            np.repeat(1, 150)],
            axis=0
        )
        catData = np.concatenate(
            [np.repeat(0, 60),
             np.repeat(2, 46),
             np.repeat(3, 41),
             np.repeat(0, 40),
             np.repeat(2, 53),
             np.repeat(3, 57),
             ],
            axis=0
          )
        correct = { (0, 0): 60, (0, 1): 46, (0, 2): 41,
                    (1, 0): 40, (1, 1): 53, (1, 2): 57}

        table = stats.contingencyTable(binData, catData)
        for indecies in correct.keys():
            self.assertTrue(
                table[indecies] == correct[indecies],
                "indecies: " + str(indecies) + " of contingency table "
                " are incorrect. Actual count is " +
                str(table[indecies]) + " true count is " +
                str(correct[indecies])
            )

    def test_fliter_na_filter_all(self):
        passes = False
        x = np.repeat(np.NAN, 10)
        y = np.repeat(1, 10)
        try:
            stats.filterNan(x,y)
        except ValueError:
            passes = True
        self.assertTrue(passes)

    def test_filter_na_filter_some_from_either(self):
        x = np.concatenate([np.repeat(np.NAN, 3), np.repeat(5, 7)])
        y = np.concatenate([np.repeat(5, 7), np.repeat(np.NAN, 3)])
        x, y = stats.filterNan(x, y)
        self.assertTrue(
            len(x) == len(y) and len(x) == 4,
            "NA filter did not filter properly"
        )

    def test_filter_na_filter_some_from_both(self):
        x = np.concatenate([np.repeat(np.NAN, 3), np.repeat(5, 7)])
        y = np.concatenate([np.repeat(np.NAN, 3), np.repeat(5, 7)])
        x, y = stats.filterNan(x, y)
        self.assertTrue(
            len(x) == len(y) and len(x) == 7,
            "NA filter did not filter properly"
        )

    def test_fisher_exact(self):
        x = np.concatenate([np.repeat(0, 12), np.repeat(1, 12)])
        y = np.concatenate(
            [np.repeat(0, 9),
             np.repeat(1, 3),
             np.repeat(0, 1),
             np.repeat(1, 11)]
        )

        stats.contingencyTable(x,y)
        pvalue = stats.binBinTest(x, y)

        self.assertTrue(
            round(pvalue, 6) == 0.002759,
            "Pvalue didn't come out right: " + str(round(pvalue, 6))
        )

    def test_ranksums(self):
        x = np.array([12, 6, 5, 4, 3, 2])
        y = np.array([11, 10, 9, 8, 7, 1])
        pvalue = stats.contContTest(x, y)

        self.assertTrue(
            round(pvalue, 3) == .095,
            "Pvalue didn't come out right: " + str(round(pvalue, 3))
        )

    def test_binCat_orCatCat(self):
        pvalue = stats.catBinOrCatCatTest(self.binData, self.catData)

        self.assertTrue(
            round(pvalue, 3) == .046,
            "Pvalue didn't come out right: " + str(round(pvalue, 3))
        )

    def test_for_parallel_switch(self):
        moreThanEnoughAttrs = 1000
        isEnough = stats.enoughForParallelComp(moreThanEnoughAttrs)
        self.assertTrue(
            isEnough,
            "1000 attributes wasn't enough for parallel comp flag"
        )

if __name__ == '__main__':
    unittest.main()
