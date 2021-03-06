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

        self.count_car = {
            "id": 2,
            "owner": "Count von Count",
            "name": "Steamer",
            "brand": "Stanley Motor",
            "year": -1,
            "engine": -1.0,
            "description": "Can hold up to 99 bats!",
            "picture": ""
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
        self.assertEqual(res.json, {"error": "Missing field", "field": "name"})

        input_car["name"] = "Silver Spur"
        res = self.testapp.post_json('/api/cars', input_car, status=400)
        self.assertEqual(res.content_type, 'application/json')
        self.assertEqual(res.json, {"error": "Missing field", "field": "owner"})

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

    def test_add_car_non_unique_owner_name(self):
        input_car1 = {
            "name": "Silver Spur",
            "description": "This car can travel by map!",
            "engine": 6.75,
            "brand": "Rolls-Royce",
            "year": 1980,
            "owner": "Kermit the Frog",
            "picture": "http://muppet.wikia.com/wiki/File:Kermit%27s_car_hood_ornament.jpg"
        }

        input_car2 = {
            "name": "Silver Spur",
            "owner": "Kermit the Frog",
        }

        res = self.testapp.post_json('/api/cars', input_car1, status=200)

        res = self.testapp.post_json('/api/cars', input_car2, status=400)
        self.assertEqual(res.content_type, 'application/json')
        self.assertEqual(res.json, {"error": "Already existing car"})

    def test_add_car_invalid_fields(self):
        input_car = {
            "name": "Silver Spur",
            "owner": "Kermit the Frog",
            "description": 1,
            "engine": "6.75",
            "brand": "Rolls-Royce",
            "year": 1980,
        }

        res = self.testapp.post_json('/api/cars', input_car, status=400)

        self.assertEqual(res.content_type, 'application/json')
        self.assertEqual(res.json, {"error": "Invalid field format",
                                    "field": "engine"})


    def test_list_cars_simple(self):
        input_car1 = {
            "name": "Silver Spur",
            "description": "This car can travel by map!",
            "engine": 6.75,
            "brand": "Rolls-Royce",
            "year": 1980,
            "owner": "Kermit the Frog",
            "picture": "http://muppet.wikia.com/wiki/File:Kermit%27s_car_hood_ornament.jpg"
        }

        input_car2 = {
            "name": "Steamer",
            "owner": "Count von Count",
            "brand": "Stanley Motor",
            "description": "Can hold up to 99 bats!",
        }

        res = self.testapp.post_json('/api/cars', input_car1)
        res = self.testapp.post_json('/api/cars', input_car2)

        res = self.testapp.get('/api/cars')
        self.assertEqual(res.content_type, 'application/json')
        self.assertEqual(len(res.json), 2)
        self.assertEqual(res.json[0], self.kermit_car)
        self.assertEqual(res.json[1], self.count_car)

    def test_list_car_empty(self):
        res = self.testapp.get('/api/cars')
        self.assertEqual(res.content_type, 'application/json')
        self.assertEqual(len(res.json), 0)
        self.assertEqual(res.json, [])

    def test_list_car_simple(self):
        input_car1 = {
            "name": "Silver Spur",
            "description": "This car can travel by map!",
            "engine": 6.75,
            "brand": "Rolls-Royce",
            "year": 1980,
            "owner": "Kermit the Frog",
            "picture": "http://muppet.wikia.com/wiki/File:Kermit%27s_car_hood_ornament.jpg"
        }

        res = self.testapp.post_json('/api/cars', input_car1)
        res = self.testapp.get('/api/cars/1')
        self.assertEqual(res.content_type, 'application/json')
        self.assertEqual(res.json, self.kermit_car)

    def test_list_car_not_there(self):
        res = self.testapp.get('/api/cars/1', status=404)
        self.assertEqual(res.content_type, 'application/json')
        self.assertEqual(res.json, {"error": "Car not found"})

    def test_update_car(self):
        input_car = {
            "name": "Steamer",
            "owner": "Count von Count",
        }

        mod_car = {
            "brand": "Stanley Motor",
            "description": "Can hold up to 99 bats!",
        }

        res = self.testapp.post_json('/api/cars', input_car)

        res = self.testapp.put_json('/api/cars/{}'.format(res.json["id"]),
                                    mod_car)
        self.assertEqual(res.content_type, 'application/json')
        self.count_car["id"] = 1
        self.assertEqual(res.json, self.count_car)

    def test_update_car_not_there(self):

        mod_car = {
            "brand": "Stanley Motor",
            "description": "Can hold up to 99 bats!",
        }

        res = self.testapp.put_json('/api/cars/{}'.format(1),
                                    mod_car, status=404)
        self.assertEqual(res.content_type, 'application/json')
        self.assertEqual(res.json, {"error": "Car not found"})

    def test_update_car_not_unique(self):

        input_car1 = {
            "name": "Silver Spur",
            "description": "This car can travel by map!",
            "engine": 6.75,
            "brand": "Rolls-Royce",
            "year": 1980,
            "owner": "Kermit the Frog",
            "picture": "http://muppet.wikia.com/wiki/File:Kermit%27s_car_hood_ornament.jpg"
        }

        input_car2 = {
            "name": "Steamer",
            "owner": "Count von Count",
            "brand": "Stanley Motor",
            "description": "Can hold up to 99 bats!",
        }

        mod_car = {
            "name": "Steamer",
            "owner": "Count von Count",
        }

        res = self.testapp.post_json('/api/cars', input_car1)
        res = self.testapp.post_json('/api/cars', input_car2)

        res = self.testapp.put_json('/api/cars/1', mod_car, status=400)
        self.assertEqual(res.content_type, 'application/json')
        self.assertEqual(res.json, {"error": "Already existing car"})

    def test_delete_car_simple(self):
        input_car = {
            "name": "Steamer",
            "owner": "Count von Count",
        }
        res = self.testapp.post_json('/api/cars', input_car)
        res = self.testapp.delete('/api/cars/1', status=200)
        self.assertEqual(res.content_type, 'application/json')
        self.assertEqual(res.json, {"Message": "Deleted car 1"})
        res = self.testapp.get('/api/cars/1', status=404)


    def test_delete_car_not_there(self):
        res = self.testapp.delete('/api/cars/1', status=404)
        self.assertEqual(res.content_type, 'application/json')
        self.assertEqual(res.json, {"error": "Car not found"})