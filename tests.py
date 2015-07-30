import unittest

from autohub import main, delete_db

class AutohubAPITests(unittest.TestCase):
    def setUp(self):
        app = main({"DB_NAME":"test.db"})

        from webtest import TestApp
        self.testapp = TestApp(app)

        self.maxDiff = None

        self.kermit_car = {
            "id": 1,
            "owner": "Kermit the Frog",
            "name": "Silver Spur",
            "brand": "Rolls-Royce",
            "year": 1980,
            "engine": 6.75,
            "description": "This car can travel by map!",
            "picture": "http://localhost:6547/cars/1/File:Kermit%27s_car_hood_ornament.jpg"
        }

    def tearDown(self):
        delete_db("test.db")


    def test_add_car_simple(self):
        input_car = {
            "name": "Silver Spur",
            "description": "This car can travel by map!",
            "engine": 6.75,
            "brand": "Rolls-Royce",
            "year": 1980,
            "owner": "Kermit the Frog",
            "picture": "http://muppet.wikia.com/wiki/File:Kermit%27s_car_hood_ornament.jpg"
        }

        res = self.testapp.post_json('/api/cars', input_car)

        self.assertEqual(res.content_type, 'application/json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json, self.kermit_car)

    def test_add_car_non_json(self):
        res = self.testapp.post('/api/cars', {"some":"stuff"}, status=400)
        self.assertEqual(res.content_type, 'application/json')
        self.assertEqual(res.json, {"error": "Body should be JSON"})

    def test_add_car_invalid_json(self):
        res = self.testapp.post_json('/api/cars', '{"hello":"there"]',
                                     status=400)
        self.assertEqual(res.content_type, 'application/json')
        self.assertEqual(res.json, {"error": "Problems parsing JSON"})

    def test_add_car_missing_essential_fields(self):
        input_car = {
            "description": "This car can travel by map!",
            "engine": 6.75,
            "brand": "Rolls-Royce",
            "year": 1980,
            "picture": "http://muppet.wikia.com/wiki/File:Kermit%27s_car_hood_ornament.jpg"
        }

        res = self.testapp.post_json('/api/cars', input_car, status=400)
        self.assertEqual(res.content_type, 'application/json')
        self.assertEqual(res.json, {"error": "Missing field", "field": "owner"})

        input_car["owner"] = "Kermit the Frog"
        res = self.testapp.post_json('/api/cars', input_car, status=400)
        self.assertEqual(res.content_type, 'application/json')
        self.assertEqual(res.json, {"error": "Missing field", "field": "name"})

    def test_add_car_missing_nonessential_fields(self):
        input_car = {
            "name": "Silver Spur",
            "brand": "Rolls-Royce",
            "year": 1980,
            "owner": "Kermit the Frog",
        }

        res = self.testapp.post_json('/api/cars', input_car)

        self.assertEqual(res.content_type, 'application/json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json["description"], "")
        self.assertEqual(res.json["engine"], -1)
        self.assertEqual(res.json["picture"], "")

    # def test_add_car_non_unique_owner_name(self):
    #     input_car1 = {
    #         "name": "Silver Spur",
    #         "description": "This car can travel by map!",
    #         "engine": 6.75,
    #         "brand": "Rolls-Royce",
    #         "year": 1980,
    #         "owner": "Kermit the Frog",
    #         "picture": "http://muppet.wikia.com/wiki/File:Kermit%27s_car_hood_ornament.jpg"
    #     }

    #     input_car2 = {
    #         "name": "Silver Spur",
    #         "owner": "Kermit the Frog",
    #     }

    #     res = self.testapp.post_json('/api/cars', input_car1, status=200)

    #     res = self.testapp.post_json('/api/cars', input_car2, 400)
    #     self.assertEqual(res.content_type, 'application/json')
    #     self.assertEqual(res.json, expected_json)

    # def test_add_car_invalid_fields(self):
    #     input_car = {
    #             "name": "Silver Spur",
    #             "description": "This car can travel by map!",
    #             "engine": 6.75,
    #             "brand": "Rolls-Royce",
    #             "year": 1980,
    #             "owner": "Kermit the Frog",
    #             "picture": "http://muppet.wikia.com/wiki/File:Kermit%27s_car_hood_ornament.jpg"
    #                 }

    #     res = self.testapp.post_json('/api/cars', input_car)

    #     self.assertEqual(res.content_type, 'application/json')
    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(res.json, expected_json)


    # def test_list_car(self):
        # res = self.testapp.get('/api/cars/1', status=200)
        # self.assertEqual(res.content_type, 'application/json')
        # res_car = json.loads(res.body)
        # self.assertEqual(kermit_car, res_car)

    # def test_list_cars(self):
    #     res = self.testapp.get('/api/list_car', status=200)
    #     self.assertEqual(res.content_type, 'application/json')

    #     self.assertEqual(json_car, res.body["response"])
    #     #multiple json objects


    # def test_update_car(self):
    #     res = self.testapp.get('/api/add_car', status=200)
    #     self.assertEqual(res.content_type, 'application/json')
    #     self.assertEqual("{'version':1.0.0, 'response':true}", res.body)


    # def test_delete_car(self):
    #     res = self.testapp.get('/api/add_car', status=200)
    #     self.assertEqual(res.content_type, 'application/json')
    #     self.assertEqual("{'version':1.0.0, 'response':true}", res.body)
    #     #list it
