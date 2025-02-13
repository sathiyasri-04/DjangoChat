from channels.generic.websocket import AsyncWebsocketConsumer 
from channels.db import database_sync_to_async
import json
from django.contrib.auth import get_user_model
from groups.models import Group
from chat.models import Message

class ChatGroupConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.group_name = self.scope['url_route']['kwargs']['group_name']
        self.room_group_name = 'chat_%s' % self.group_name

        print(self.group_name)

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        messages = await self.get_messages() #getting previous messages
        await self.send(text_data=json.dumps({
            'type': 'history_messages',
            'messages': messages
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard( 
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json.get('message', '').strip()
            user = text_data_json.get('user', '').strip()

            if not message or not user:
                print("Error: Empty message or user")
                return

            await self.save_message(message, user)

            # Format the message with username
            formatted_message = f"{user}: {message}"

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'groupchat_message',
                    'message': formatted_message
                }
            )
        except json.JSONDecodeError:
            print("Error: Invalid JSON received")

    async def groupchat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'chat_message',  # Explicitly define the type
            'message': message
        }))
        

    @database_sync_to_async
    def save_message(self, message_text, username):
        User = get_user_model()
        user = User.objects.get(username=username)
        group = Group.objects.get(id=self.group_name)
        
        message = Message.objects.create(
            group=group,
            sender=user,
            text=message_text
        )
        return message
    
    @database_sync_to_async
    def get_messages(self):
        messages = Message.objects.filter(
            group_id=self.group_name,
            deleted_at__isnull=True
        ).order_by('created_at')
        
        message_list = []
        for message in messages:
            message_list.append({
                'id': message.id,
                'text': message.text,
                'sender': {
                    'id': message.sender.id if message.sender else None,
                    'username': message.sender.username if message.sender else 'Deleted User'
                },
            })
        return message_list
