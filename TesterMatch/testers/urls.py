from django.conf.urls import url

from .views import match_testers

urlpatterns = [
    url(r'^match-testers/', match_testers, name='match_testers'),
]

