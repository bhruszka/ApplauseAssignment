from django.db import models

SUPPORTED_COUNTRIES = (('GB', 'United Kingdom'), ('US', ' United States of America'), ('JP', 'Japan'))


class Tester(models.Model):
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    country = models.CharField(max_length=2, choices=SUPPORTED_COUNTRIES)
    last_login = models.DateTimeField()

    def __str__(self):
        return '{} - {} - {} - {} - {}'.format(self.id, self.first_name, self.last_name, self.country, self.last_login)


class Device(models.Model):
    description = models.CharField(max_length=280)
    testers = models.ManyToManyField(Tester)

    def __str__(self):
        return '{} - {}'.format(self.id, self.description)


class Bug(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    tester = models.ForeignKey(Tester, on_delete=models.CASCADE)

    def __str__(self):
        return '{} - {} - {}'.format(self.id, self.device_id, self.tester_id)
