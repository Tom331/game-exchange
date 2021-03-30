# chat/consumers.py
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Message


from django.contrib.auth import get_user_model
User = get_user_model()
from django.conf import settings

print('~~~IN CONSUMERS.PY~~~')


class ChatConsumer(WebsocketConsumer):

    def fetch_messages(self, data):
        transaction_id = data['transaction_id']

        messages = Message.last_10_messages(self, transaction_id)
        content = {
            'command': 'messages',
            'messages': self.messages_to_json(messages)
        }
        self.send_message(content)


    def messages_to_json(self, messages):
        result = []

        for message in messages:
            result.append(self.message_to_json(message))
        return result


    def new_message(self, data):
        author = data['from']
        message = data['message']
        transaction_id = data['transaction_id']


        author_user = User.objects.filter(username=author)[0]
        message = Message.objects.create(author=author_user, content=message, transaction_id=transaction_id)
        content = {
            'command': 'new_message',
            'message': self.message_to_json(message)
        }
        return self.send_chat_message(content)


    def message_to_json(self, message):
        return {
            'author': message.author.username,
            'content': message.content,
            'timestamp': str(message.timestamp),
            'transaction_id': str(message.transaction_id) #maybe don't need
        }


    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message
    }


    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()


    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )


    # Receive message from WebSocket. self, dict
    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self, data) # either fetch_messages or new_message


    def send_chat_message(self, message):
        async_to_sync(self.channel_layer.group_send)( # Send message to room group
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def send_message(self, message):
        self.send(text_data=json.dumps(message))


    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        content1 = message['message']
        content2 = content1['content']
        #self.send(text_data=json.dumps(content2)) # Send message to WebSocket
        self.send(text_data=json.dumps(message)) # Send message to WebSocket