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
        print('~~~fetch_messages~~~')
        messages = Message.last_10_messages(self)
        content = {
            'command': 'messages',
            'messages': self.messages_to_json(messages)
        }
        print('content: ' + str(content))
        self.send_message(content)


    def new_message(self, data):
        print('~~~in new_message: 2~~~')
        author = data['from']
        print('author: ' + author)
        author_user = User.objects.filter(username=author)[0]
        message = Message.objects.create(author=author_user, content=data['message'])
        content = {
            'command': 'new_message',
            'message': self.message_to_json(message)
        }
        return self.send_chat_message(content)


    def messages_to_json(self, messages):
        print('~~~messages_to_json~~~')
        result = []

        for message in messages:
            result.append(self.message_to_json(message))
        return result


    def message_to_json(self, message):
        print('~~~message_to_json~~~')
        return {
            'author': message.author.username,
            'content': message.content,
            'timestamp': str(message.timestamp)
        }

    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message
    }


    def connect(self):
        print('~~~connect~~~')
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        print('~~~disconnect~~~')
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        print('~~~receive: 1~~~')
        data = json.loads(text_data)
        self.commands[data['command']](self, data) # either fetch_messages or new_message

    def send_chat_message(self, message):
        print('in send_chat_message: 3')
        async_to_sync(self.channel_layer.group_send)( # Send message to room group
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def send_message(self, message):
        print('~~~in send_message~~~')
        print('message: ' + str(message))
        self.send(text_data=json.dumps(message))

    # Receive message from room group
    def chat_message(self, event):
        print('~~~in chat_message~~~: 4')
        message = event['message']
        print('message: ' + str(message))
        content1 = message['message']
        print('content1: ' + str(content1))
        content2 = content1['content']
        print('content2: ' + content2)
        #self.send(text_data=json.dumps(content2)) # Send message to WebSocket
        self.send(text_data=json.dumps(message)) # Send message to WebSocket