import unittest
from fastapi.testclient import TestClient
from aep_example.main import app

class TestExceptions(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_404_not_found(self):
        response = self.client.get("/non-existent-path")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.headers["content-type"], "application/problem+json")
        data = response.json()
        self.assertEqual(data["type"], "aep.example.com/http-error")
        self.assertEqual(data["status"], 404)
        # detail might be missing for generic 404


    def test_422_validation_error(self):
        # GET /shelves?max_page_size=invalid (integer expected)
        response = self.client.get("/shelves?max_page_size=invalid")
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.headers["content-type"], "application/problem+json")
        data = response.json()
        self.assertEqual(data["type"], "aep.example.com/validation-error")
        self.assertEqual(data["title"], "Validation Error")
        self.assertEqual(data["status"], 422)
        self.assertTrue("detail" in data)

if __name__ == '__main__':
    unittest.main()
