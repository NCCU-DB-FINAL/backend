import json
import random
import string
import unittest
import requests


class TestRentalAPI(unittest.TestCase):
    def setUp(self):
        self.base_url = 'http://127.0.0.1:5000'
        self.rand = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        self.username = 'testuser' + self.rand
        self.password = 'testpassword'
        self.user_type = 'landlord'

        # Sign up
        signup_url = f'{self.base_url}/api/signup'
        signup_data = {
            'username': self.username,
            'phonenum': '1234567890',
            'password': self.password,
            'type': self.user_type
        }
        response = requests.post(signup_url, json=signup_data)
        self.assertEqual(response.status_code, 201)

        # Log in
        login_url = f'{self.base_url}/api/login'
        login_data = {
            'username': self.username,
            'password': self.password,
            'type': self.user_type
        }
        response = requests.post(login_url, json=login_data)
        self.assertEqual(response.status_code, 200)
        self.token = response.json()['access_token']

    def test2_add_rental(self):
        url = f'{self.base_url}/api/rental'
        data = {
            'address': '123 Main St' + self.rand,
            'price': 1000,
            'type': 'Apartment',
            'bedroom': 2,
            'living_room': 1,
            'bathroom': 1,
            'ping': 50,
            'rental_term': 'Long term'
        }
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        response = requests.post(url, json=data, headers=headers)
        print(response.request.body)
        print(response.content)
        self.assertEqual(response.status_code, 201)


    def test3_search_rental(self):
        url = f'{self.base_url}/api/rental/search'
        search_criteria = {'area': 'Main St'}
        response = requests.get(url, params=search_criteria)
        print(response.request.url)
        print(response.content)
        self.assertEqual(response.status_code, 200)

    # def test4_like_rental(self):
    #     url = f'{self.base_url}/api/like/0'  # Assuming rental ID 0
    #     data = {'tenant_id': 0}  # Assuming tenant ID 1
    #     response = requests.post(url, json=data)
    #     self.assertEqual(response.status_code, 201)
    #
    # def test5_add_comment(self):
    #     url = f'{self.base_url}/api/comment/1'  # Assuming rental ID 1
    #     data = {'tenant_id': 1, 'rating': 5, 'comment': 'Great place!'}
    #     response = requests.post(url, json=data)
    #     self.assertEqual(response.status_code, 201)


if __name__ == '__main__':
    unittest.main()
