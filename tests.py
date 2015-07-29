import unittest


class AutohubAPITests(unittest.TestCase):
    def setUp(self):
        from autohub import main
        app = main()

        from webtest import TestApp
        self.testapp = TestApp(app)

        self.kermit_car = {
            "id": 0,
            "description": "This car can travel by map!",
            "engine": 6.75,
            "brand": "Rolls-Royce",
            "year": 1980,
            "owner": "Kermit the Frog",
            "picture": "http://localhost:6547/cars/0/File:Kermit%27s_car_hood_ornament.jpg"
        }


    def test_add_car(self):
        input_car = {
                        "description": "This car can travel by map!",
                        "engine": 6.75,
                        "brand": "Rolls-Royce",
                        "year": 1980,
                        "owner": "Kermit the Frog",
                        "picture": "http://muppet.wikia.com/wiki/File:Kermit%27s_car_hood_ornament.jpg"
                    }

        res = self.testapp.post_json('/api/add_car', input_car)

        self.assertEqual(res.content_type, 'application/json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json, self.kermit_car)

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
