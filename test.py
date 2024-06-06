import json
import random
import unittest
import requests


class TestRentalAPI(unittest.TestCase):
    rand = str(random.randint(0, 10000))
    print(rand)
    tenant_token = ''

    def setUp(self):
        self.base_url = 'http://127.0.0.1:5000'

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

    def test11_login(self):
        url = f'{self.base_url}/api/login'
        data = {'username': 'test_' + self.rand + 't', 'password': '123456', 'type': 'tenant'}
        response = requests.post(url, json=data)
        print(response.request.body)
        print(response.content)
        jwt = response.content.decode('utf-8')
        jwt = json.loads(jwt)
        self.__class__.tenant_token = jwt['access_token']
        print(self.tenant_token)
        self.assertEqual(response.status_code, 200)

    def test3_search_rental(self):
        url = f'{self.base_url}/api/rental/search'
        search_criteria = {'area': 'Main St'}
        response = requests.get(url, json=search_criteria)
        print(response.request.body)
        print(response.content)
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
