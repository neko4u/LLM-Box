import unittest
from src.api.main import app

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_health_check(self):
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'status': 'ok'})

    def test_model_endpoint(self):
        response = self.app.post('/model/predict', json={'data': 'sample input'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('prediction', response.json)

if __name__ == '__main__':
    unittest.main()