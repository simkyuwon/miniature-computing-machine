import json
import tempfile

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.core.files.base import ContentFile

from .models import File


class EditConsumer(WebsocketConsumer):
    def connect(self):
        self.room_group_name = None
        self.file_handler_list = FileHandlerList()
        self.file_handler = None
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if text_data_json['command'] == "join":
            if self.file_handler is not None:
                self.file_handler_list.del_file_handler(self.room_group_name)
                async_to_sync(self.channel_layer.group_discard)(
                    self.room_group_name,
                    self.channel_name
                )

            self.room_group_name = text_data_json['id']

            self.file_handler = self.file_handler_list.new_file_handler(self.room_group_name)
            if self.file_handler is None:
                self.send(text_data=f"file id({self.room_group_name}) not exist")
                pass

            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )
        elif text_data_json['command'] == "append":
            if self.room_group_name is None or self.file_handler is None:
                pass
            text = text_data_json['text']
            self.file_handler.append_text(text)
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'read_file',
                    'text': str(self.file_handler.read_file())
                }
            )
        elif text_data_json['command'] == "insert":
            if self.room_group_name is None or self.file_handler is None:
                pass
            text = text_data_json['text']
            seek_index = int(text_data_json['seek'])
            self.file_handler.insert_text(text, seek_index)
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'read_file',
                    'text': str(self.file_handler.read_file())
                }
            )
        elif text_data_json['command'] == "delete":
            if self.room_group_name is None or self.file_handler is None:
                pass
            seek_index = int(text_data_json['seek'])
            length = int(text_data_json['length'])
            self.file_handler.delete_text(seek_index, length)
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'read_file',
                    'text': str(self.file_handler.read_file())
                }
            )

    def read_file(self, event):
        self.send(text_data=json.dumps({'message': event['text']}, ensure_ascii=False))


class FileHandler:
    def __init__(self, file_id):
        self.file_id = file_id
        file_object = File.objects.get(id=file_id)
        if file_object is None:
            self.file = None
            pass

        if file_object.contents.name == '':
            file_object.contents = ContentFile("", file_object.title)
            file_object.save()
        file_object.contents.open('rb+')
        self.file = file_object.contents.file
        self.count = 0

    def append_text(self, text):
        self.file.seek(0, 2)
        self.file.write(bytes(text, encoding="utf-8"))

    def insert_text(self, text, seek_index):
        temp = tempfile.TemporaryFile("rb+")
        self.file.seek(0)
        temp.write(self.file.read(seek_index))
        temp.write(bytes(text, encoding="utf-8"))
        temp.write(self.file.read())
        self.file = temp

    def delete_text(self, seek_index, length):
        temp = tempfile.TemporaryFile('rb+')
        self.file.seek(0)
        temp.write(self.file.read(seek_index))
        self.file.seek(length, 1)
        temp.write(self.file.read())
        self.file = temp

    def read_file(self):
        self.file.seek(0)
        return self.file.read().decode('utf-8').split('\n')


class FileHandlerList(object):
    file_handler = {}

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    def new_file_handler(self, file_id):
        if file_id not in self.file_handler:
            self.file_handler[file_id] = FileHandler(file_id)
            if self.file_handler[file_id].file is None:
                self.file_handler.pop(file_id)
                return None
        file_handler = self.file_handler[file_id]
        file_handler.count += 1
        return self.file_handler[file_id]

    def del_file_handler(self, file_id):
        if file_id not in self.file_handler:
            pass
        file_handler = self.file_handler[file_id]
        file_handler.count -= 1
        if file_handler.count == 0:
            file_object = File.objects.get(id=file_id)
            file_object.contents = file_handler.file
            file_object.save()
            self.file_handler.pop(file_id)
