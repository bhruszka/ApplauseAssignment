import csv
import datetime
import pytz

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from testers.models import Device, Tester, Bug


class Command(BaseCommand):

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

        self._DATA_TIMEZONE = pytz.utc

        self._INITIAL_DATA_PATH = 'testers/initial_data/'
        self._DEVICES_FILE_PATH = self._INITIAL_DATA_PATH + 'devices.csv'
        self._TESTERS_FILE_PATH = self._INITIAL_DATA_PATH + 'testers.csv'
        self._BUGS_FILE_PATH = self._INITIAL_DATA_PATH + 'bugs.csv'
        self._TESTER_DEVICE_FILE_PATH = self._INITIAL_DATA_PATH + 'tester_device.csv'

    @transaction.atomic
    def handle(self, *args, **options):
        if Device.objects.exists() or Tester.objects.exists() or Bug.objects.exists():
            raise CommandError('Device, Tester and Bug tables are not empty')

        # Populating device table
        new_devices = self._read_data(self._DEVICES_FILE_PATH, self._map_device)
        self.stdout.write('Adding {} devices'.format(len(new_devices)))
        Device.objects.bulk_create(new_devices)

        # Populating tester table
        new_testers = self._read_data(self._TESTERS_FILE_PATH, self._map_testers)
        self.stdout.write('Adding {} testers'.format(len(new_testers)))
        Tester.objects.bulk_create(new_testers)

        # Populating bug table
        new_bugs = self._read_data(self._BUGS_FILE_PATH, self._map_bugs)
        self.stdout.write('Adding {} bugs'.format(len(new_bugs)))
        Bug.objects.bulk_create(new_bugs)

        # Populating tester and device relation
        device_tester_relations = self._read_device_tester_data()
        for tester_id, devices in device_tester_relations.items():
            self.stdout.write('Adding {} device tester relations'.format(len(devices)))
            t = Tester.objects.get(id=tester_id)
            t.devices.add(*devices)
            t.save()

    @staticmethod
    def _read_data(path, map_func):
        new_objects = []
        with open(path) as f:
            reader = csv.reader(f)

            # Skipping header
            next(reader, None)
            for row in reader:
                if row:
                    new_obj = map_func(row)
                    new_objects.append(new_obj)

        return new_objects

    @staticmethod
    def _map_device(row):
        return Device(id=row[0], description=row[1])

    def _map_testers(self, row):
        last_login = datetime.datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S").replace(tzinfo=self._DATA_TIMEZONE)
        return Tester(id=row[0], first_name=row[1], last_name=row[2], country=row[3], last_login=last_login)

    @staticmethod
    def _map_bugs(row):
        return Bug(id=row[0], device_id=row[1], tester_id=row[2])

    def _read_device_tester_data(self):
        relations = {}
        with open(self._TESTER_DEVICE_FILE_PATH) as f:
            reader = csv.reader(f)

            # Skipping header
            next(reader, None)
            for row in reader:
                if row:
                    relations.setdefault(row[0], []).append(row[1])

        return relations
