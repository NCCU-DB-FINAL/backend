import random
import unittest
import requests


class TestRentalAPI(unittest.TestCase):
    rand = str(random.randint(0, 10000))
    print(rand)

    def setUp(self):
        self.base_url = 'http://127.0.0.1:5000'

    def test0_signup(self):
        url = f'{self.base_url}/api/signup'
        data = {'username': 'test_' + self.rand + 'l', 'phonenum': '0912345678', 'password': '123456',
                'type': 'landlord'}
        response = requests.post(url, json=data)
        print(response.request.body)
        print(response.content)
        self.assertEqual(response.status_code, 201)

    def test00_signup(self):
        url = f'{self.base_url}/api/signup'
        data = {'username': 'test_' + self.rand + 't', 'phonenum': '0912345678', 'password': '123456',
                'type': 'tenant'}
        response = requests.post(url, json=data)
        print(response.request.body)
        print(response.content)
        self.assertEqual(response.status_code, 201)

    def test00_signup1(self):
        '''重複註冊'''
        url = f'{self.base_url}/api/signup'
        data = {'username': 'test_' + self.rand + 't', 'phonenum': '0912345678', 'password': '123456',
                'type': 'tenant'}
        response = requests.post(url, json=data)
        print(response.request.body)
        print(response.content)
        self.assertEqual(response.status_code, 409)

    def test1_login(self):
        url = f'{self.base_url}/api/login'
        data = {'username': 'test_' + self.rand + 'l', 'password': '123456',
                'type': 'landlord'}
        response = requests.post(url, json=data)
        print(response.request.body)
        print(response.content)
        self.assertEqual(response.status_code, 200)

    def test11_login(self):
        url = f'{self.base_url}/api/login'
        data = {'username': 'test_' + self.rand + 't', 'password': '123456', 'type': 'tenant'}
        response = requests.post(url, json=data)
        print(response.request.body)
        print(response.content)
        self.assertEqual(response.status_code, 200)

    def test2_add_rental(self):
        url = f'{self.base_url}/api/rental'
        data = {
            'address': '123 Main St',
            'price': 1000,
            'type': 'Apartment',
            'bedroom': 2,
            'living_room': 1,
            'bathroom': 1,
            'ping': 50,
            'rental_term': 'Long term',
            'landLord_id': 1
        }
        response = requests.post(url, json=data)
        print(response.request.body)
        print(response.content)
        self.assertEqual(response.status_code, 201)

    def test3_search_rental(self):
        url = f'{self.base_url}/api/rental/search'
        search_criteria = {'area': 'Main St'}
        response = requests.get(url, json=search_criteria)
        print(response.request.body)
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
