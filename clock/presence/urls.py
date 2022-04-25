from django.urls import path
from .views import HomeView, PushTimecard, PresenceRecords


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('push', PushTimecard.as_view(), name='push'),
    path('records', PresenceRecords.as_view(), name='records'),
]

