import backend.models as md
import unittest



class TestDB(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # TODO: create new database for testing here
        # TODO: once created, add function to generate some data for testing
        pass

    def test_no_user(self):
        result = md.get_user_from_email('')
        self.assertEqual(result, [])
    
    def test_no_schedule_from_link(self):
        result = md.get_schedule_from_link('')
        self.assertEqual(result, [])

    