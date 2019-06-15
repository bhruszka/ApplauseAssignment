from django.core.management import call_command, CommandError
from django.test import TestCase
from django.utils import timezone

from .models import Device, Tester, Bug


class PopulateDbTest(TestCase):
    def test_command(self):
        call_command('populate_db')
        self.assertEqual(Device.objects.count(), 10)
        self.assertEqual(Tester.objects.count(), 9)
        self.assertEqual(Bug.objects.count(), 1000)
        self.assertEqual(Device.testers.through.objects.all().count(), 36)

    def test_command_non_empty_device(self):
        Device.objects.create(description='IPhone 3G')
        with self.assertRaises(CommandError):
            call_command('populate_db')

    def test_command_non_empty_tester(self):
        Tester.objects.create(first_name='John', last_name='Smith', country='GB', last_login=timezone.now())
        with self.assertRaises(CommandError):
            call_command('populate_db')

    def test_command_non_empty(self):
        device = Device.objects.create(description='IPhone 3G')
        tester = Tester.objects.create(first_name='John', last_name='Smith', country='GB', last_login=timezone.now())
        Bug.objects.create(device=device, tester=tester)
        with self.assertRaises(CommandError):
            call_command('populate_db')
