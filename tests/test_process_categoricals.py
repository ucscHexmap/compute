#!/usr/bin/env python2.7


import process_categoricals as pc
import testUtil as tu
import StringIO
import unittest
import os

testDir = os.getcwd()

class Test_colormapGeneration(unittest.TestCase):

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

    def test_attrs(s):
        '''
        makes sure our edge case file performs as expected..
        @return:
        '''
        #make random boolean data
        out = StringIO.StringIO()

        try:
            pc.create_colormaps_file([os.path.join(testDir,
                                                   'in/layout/attributes.tab')],
                                     out)
        except Exception as e:
            s.assertTrue(False,'exception thrown when processing edge cases'
                         + str(e))

        #get colormaps to interogate
        colormaps = pc.read_colormaps(StringIO.StringIO(out.getvalue()))

        s.assertTrue(len(colormaps) ==7,'did not find the correct amount of'
                ' colormap vars')
