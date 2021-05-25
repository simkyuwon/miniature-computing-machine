import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import File


class EditConsumer(WebsocketConsumer):
    def connect(self):
        self.room_group_name = None
        self.accept()

    def disconnect(self, close_code):
        file_object = File.objects.get(id=self.room_group_name)
        now_group_size = file_object.group_size
        if now_group_size == 1:
            del file_handler_list[file_object.id]
        file_object.group_size = now_group_size - 1
        file_object.save()
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if text_data_json['command'] == "join":
            self.room_group_name = text_data_json['id']
            file_object = File.objects.get(id=self.room_group_name)

            if file_object is None:
                self.send(text_data="file not found")
                pass
            else:
                now_group_size = file_object.group_size
                if now_group_size == 0:
                    FileHandler(file_object.id)
                file_object.group_size = now_group_size + 1
                file_object.save()

            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )
        elif text_data_json['command'] == "edit":
            if self.room_group_name is None:
                pass
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'edit_file',
                }
            )

    def edit_file(self, event):
        self.send(text_data=json.dumps({'message': 'test message'}))


file_handler_list = {}


class FileHandler:
    file = None
    file_id = 0

    def __init__(self, file_id):
        self.file_id = file_id
        file_object = File.objects.get(id=file_id)
        self.file = file_object.contents
        file_handler_list[file_id] = self

    def __del__(self):
        file_object = File.objects.get(id=self.file_id)
        file_object.contents = self.file
        file_object.save()
