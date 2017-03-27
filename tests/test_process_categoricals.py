#!/usr/bin/env python2.7


import testUtil as tu
import StringIO
import pandas as pd
import unittest
import os
import process_categoricals as pc

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

    def test_many_categories(s):
        '''

        @return:
        '''
        #length of categorical descriptors
        lenStr=3
        #generate categorical vectors of varying length and make colormaps
        for i in [19,22,33]:
            #generate 'i' random strings
            df = pd.DataFrame([tu.randStr(lenStr) for x in range(i)])
            #switch over to a string buffer so can pass to process_cat*
            df = tu.dataFrameToStrBuf(df)
            out = StringIO.StringIO()
            try:
                pc.create_colormaps_file([df],out)
            except Exception as e:
                s.assertTrue(False,'exception thrown when doing cat vector of '
                                   'size ' + str(i) + ' with exception '
                                   + str(e))
