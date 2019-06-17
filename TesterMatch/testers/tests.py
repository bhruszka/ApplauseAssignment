from django.core.management import call_command, CommandError
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework.utils import json

from .models import Device, Tester, Bug


class PopulateDbTest(TestCase):
    def test_command(self):
        call_command('populate_db')
        self.assertEqual(Device.objects.count(), 10)
        self.assertEqual(Tester.objects.count(), 9)
        self.assertEqual(Bug.objects.count(), 1000)
        self.assertEqual(Tester.devices.through.objects.all().count(), 36)

    def test_command_non_empty_device(self):
        Device.objects.create(description='IPhone 3G')
        with self.assertRaises(CommandError):
            call_command('populate_db')
        self.assertEqual(Device.objects.count(), 1)
        self.assertEqual(Tester.objects.count(), 0)
        self.assertEqual(Bug.objects.count(), 0)

    def test_command_non_empty_tester(self):
        Tester.objects.create(first_name='John', last_name='Smith', country='GB', last_login=timezone.now())
        with self.assertRaises(CommandError):
            call_command('populate_db')
        self.assertEqual(Device.objects.count(), 0)
        self.assertEqual(Tester.objects.count(), 1)
        self.assertEqual(Bug.objects.count(), 0)

    def test_command_non_empty(self):
        device = Device.objects.create(description='IPhone 3G')
        tester = Tester.objects.create(first_name='John', last_name='Smith', country='GB', last_login=timezone.now())
        Bug.objects.create(device=device, tester=tester)
        with self.assertRaises(CommandError):
            call_command('populate_db')
        self.assertEqual(Device.objects.count(), 1)
        self.assertEqual(Tester.objects.count(), 1)
        self.assertEqual(Bug.objects.count(), 1)


class MatchTestersTest(APITestCase):

    def setUp(self):
        self.url = 'http://testserver/match-testers/'

    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        cls.device_iphone = Device.objects.create(description='IPhone')
        cls.device_nokia = Device.objects.create(description='Nokia')
        cls.device_android = Device.objects.create(description='Android')

        # 1. Tester with bugs reported to devices he doesn't have anymore
        cls.tester_john = Tester.objects.create(first_name='John', last_name='Smith', country='US',
                                                last_login=timezone.now())
        cls.tester_john.devices.add(cls.device_nokia, cls.device_android)
        Bug.objects.create(tester=cls.tester_john, device=cls.device_iphone)
        Bug.objects.create(tester=cls.tester_john, device=cls.device_iphone)
        Bug.objects.create(tester=cls.tester_john, device=cls.device_iphone)

        # 2. Tester with bugs reported to devices he has and he doesn't have anymore
        cls.tester_bob = Tester.objects.create(first_name='Bob', last_name='Blue', country='GB',
                                               last_login=timezone.now())
        cls.tester_bob.devices.add(cls.device_iphone)
        Bug.objects.create(tester=cls.tester_bob, device=cls.device_iphone)
        Bug.objects.create(tester=cls.tester_bob, device=cls.device_iphone)
        Bug.objects.create(tester=cls.tester_bob, device=cls.device_nokia)

        # 3. Tester with all devices
        cls.tester_kate = Tester.objects.create(first_name='Kate', last_name='Red', country='US',
                                                last_login=timezone.now())
        cls.tester_kate.devices.add(cls.device_iphone, cls.device_nokia, cls.device_android)
        Bug.objects.create(tester=cls.tester_kate, device=cls.device_iphone)
        Bug.objects.create(tester=cls.tester_kate, device=cls.device_nokia)
        Bug.objects.create(tester=cls.tester_kate, device=cls.device_android)

        # 4. Tester
        cls.tester_sara = Tester.objects.create(first_name='Sara', last_name='Green', country='US',
                                                last_login=timezone.now())
        cls.tester_sara.devices.add(cls.device_nokia, cls.device_android)
        Bug.objects.create(tester=cls.tester_sara, device=cls.device_nokia)
        Bug.objects.create(tester=cls.tester_sara, device=cls.device_nokia)
        Bug.objects.create(tester=cls.tester_sara, device=cls.device_android)
        Bug.objects.create(tester=cls.tester_sara, device=cls.device_android)

        # 5. Tester
        cls.tester_micheal = Tester.objects.create(first_name='Michael', last_name='Purple', country='JP',
                                                   last_login=timezone.now())
        cls.tester_micheal.devices.add(cls.device_iphone, cls.device_android)
        Bug.objects.create(tester=cls.tester_micheal, device=cls.device_iphone)
        Bug.objects.create(tester=cls.tester_micheal, device=cls.device_iphone)
        Bug.objects.create(tester=cls.tester_micheal, device=cls.device_android)
        Bug.objects.create(tester=cls.tester_micheal, device=cls.device_android)
        Bug.objects.create(tester=cls.tester_micheal, device=cls.device_android)

        # 6. Tester
        cls.tester_lee = Tester.objects.create(first_name='Lee', last_name='Yellow', country='US',
                                               last_login=timezone.now())
        cls.tester_lee.devices.add(cls.device_nokia)
        Bug.objects.create(tester=cls.tester_lee, device=cls.device_nokia)
        Bug.objects.create(tester=cls.tester_lee, device=cls.device_nokia)
        Bug.objects.create(tester=cls.tester_lee, device=cls.device_nokia)
        Bug.objects.create(tester=cls.tester_lee, device=cls.device_nokia)
        Bug.objects.create(tester=cls.tester_lee, device=cls.device_nokia)
        Bug.objects.create(tester=cls.tester_lee, device=cls.device_nokia)
        Bug.objects.create(tester=cls.tester_lee, device=cls.device_nokia)

        cls.fields_to_compare = ('experience', 'first_name', 'last_name')

    @classmethod
    def map_response(cls, response):
        content = json.loads(cls, response.content)
        return [cls.map_tester(c) for c in content]

    @classmethod
    def map_tester(cls, tester):
        return {k: tester[k] for k in cls.fields_to_compare}

    def test_all(self):
        expected = [{'experience': 7, 'first_name': 'Lee', 'last_name': 'Yellow', 'country': 'US'},
                    {'experience': 5, 'first_name': 'Michael', 'last_name': 'Purple', 'country': 'JP'},
                    {'experience': 4, 'first_name': 'Sara', 'last_name': 'Green', 'country': 'US'},
                    {'experience': 3, 'first_name': 'Kate', 'last_name': 'Red', 'country': 'US'},
                    {'experience': 2, 'first_name': 'Bob', 'last_name': 'Blue', 'country': 'GB'},
                    {'experience': 0, 'first_name': 'John', 'last_name': 'Smith', 'country': 'US'},
                    ]
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), expected)

    def test_all_devices_two_countries(self):
        countries = ['US', 'GB']
        expected = [{'experience': 7, 'first_name': 'Lee', 'last_name': 'Yellow', 'country': 'US'},
                    {'experience': 4, 'first_name': 'Sara', 'last_name': 'Green', 'country': 'US'},
                    {'experience': 3, 'first_name': 'Kate', 'last_name': 'Red', 'country': 'US'},
                    {'experience': 2, 'first_name': 'Bob', 'last_name': 'Blue', 'country': 'GB'},
                    {'experience': 0, 'first_name': 'John', 'last_name': 'Smith', 'country': 'US'},
                    ]
        response = self.client.get(self.url, {'countries': countries})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), expected)

    def test_two_devices_all_countries(self):
        devices = [self.device_android.id, self.device_iphone.id]
        expected = [{'experience': 5, 'first_name': 'Michael', 'last_name': 'Purple', 'country': 'JP'},
                    {'experience': 2, 'first_name': 'Bob', 'last_name': 'Blue', 'country': 'GB'},
                    {'experience': 2, 'first_name': 'Sara', 'last_name': 'Green', 'country': 'US'},
                    {'experience': 2, 'first_name': 'Kate', 'last_name': 'Red', 'country': 'US'},
                    {'experience': 0, 'first_name': 'John', 'last_name': 'Smith', 'country': 'US'},
                    {'experience': 0, 'first_name': 'Lee', 'last_name': 'Yellow', 'country': 'US'},
                    ]
        response = self.client.get(self.url, {'devices': devices})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), expected)

    def test_two_devices_two_countries(self):
        devices = [self.device_android.id, self.device_nokia.id]
        countries = ['US', 'JP']
        expected = [{'experience': 7, 'first_name': 'Lee', 'last_name': 'Yellow', 'country': 'US'},
                    {'experience': 4, 'first_name': 'Sara', 'last_name': 'Green', 'country': 'US'},
                    {'experience': 3, 'first_name': 'Michael', 'last_name': 'Purple', 'country': 'JP'},
                    {'experience': 2, 'first_name': 'Kate', 'last_name': 'Red', 'country': 'US'},
                    {'experience': 0, 'first_name': 'John', 'last_name': 'Smith', 'country': 'US'},
                    ]
        response = self.client.get(self.url, {'devices': devices, 'countries': countries})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), expected)

    def test_invalid_country(self):
        countries = ['US', 'GG', 'JP']
        response = self.client.get(self.url, {'countries': countries})
        self.assertEqual(response.status_code, 400)

    def test_invalid_device(self):
        devices = [self.device_android.id, self.device_nokia.id, 500]
        response = self.client.get(self.url, {'devices': devices})
        self.assertEqual(response.status_code, 400)
