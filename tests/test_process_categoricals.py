#!/usr/bin/env python2.7


import process_categoricals as pc
import testUtil as tu
import StringIO
import unittest

class Test_layoutBasic(unittest.TestCase):

    def test_bool(s):
        '''
        makes sure boolean input doesn't throw an error
        @return:
        '''
        #make random boolean data
        df = tu.getdf(type_='random',nrows=20,ncols=2)
        df[0] = df[0] > 0
        df[1] = df[1] < 0

        df = tu.dataFrameToStrBuf(df)
        #df = '/home/duncan/hex/compute/tests/in/layout/mcrchopra.atts
        # .with_strs.tab'
        #print df
        out = StringIO.StringIO()
        passed = True
        e = None
        try:
            pc.create_colormaps_file([df],out)

        except Exception as e:
            passed = False

        #make sure there was no exception and some values for the
        # colormap were put in
        s.assertTrue(passed and len(out.getvalue()),'exception thrown '
                            'from '
                            'passing booleans '
                             'to '
                            'create_colormaps_file' + str(e))
