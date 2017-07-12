import www
import unittest

class wwwTestCase(unittest.TestCase):

    def setUp(self):
        www.app.config['UNIT_TEST'] = True
        self.app = www.app.test_client()

    def tearDown(self):
        pass

    def test_404_root(s):
        rv = s.app.get('/')
        s.assertTrue(rv.status_code == 404)
        #assert b'No entries here so far' in rv.data

    def test_404_query(s):
        rv = s.app.get('/query')
        """
        print 'rv:', str(rv)
        print 'rv.status_code:', str(rv.status_code)
        print 'rv.status:', str(rv.status)
        print 'rv.data:', str(rv.data)
        """
        s.assertTrue(rv.status_code == 404)

if __name__ == '__main__':
    unittest.main()
