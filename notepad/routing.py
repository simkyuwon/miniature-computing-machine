from django.urls import path

from notepadDB import consumers

websocket_urlpatterns = [
    path('ws/edit/', consumers.EditConsumer.as_asgi()),
]
