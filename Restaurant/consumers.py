from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from jwt import decode as jwt_decode
from django.conf import settings
import json

# from Accountapp.models import DeliveryBoyTable

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.order_id = self.scope['url_route']['kwargs']['order_id']
        self.room_group_name = f'chat_{self.order_id}'

        # Authenticate using token from query params
        try:
            token = self.scope['query_string'].decode().split('=')[-1]
            validated_token = UntypedToken(token)
            decoded_data = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            self.user = await database_sync_to_async(User.objects.get)(id=decoded_data['user_id'])

            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
        except (InvalidToken, TokenError, Exception) as e:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)

        message_type = data.get('message_type')
        sender_type = data.get('sender_type')
        text = data.get('text')
        file_url = data.get('file_url')

        # Broadcast the message to the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message_type': message_type,
                'sender_type': sender_type,
                'text': text,
                'file_url': file_url
            }
        )

        # Save message to DB
        if text!=None or file_url!=None:
            print(f"Received message: {text}, file_url: {file_url}..Sender type: {sender_type}...Message type: {message_type}....................................")
            print(text!=None or file_url!=None)
            await self.save_message(self.order_id, self.user, sender_type, text,file_url,message_type)

    # async def chat_message(self, event):
       
    #     await self.send(text_data=json.dumps(event))
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message_type': event['message_type'],
            'sender_type': event['sender_type'],
            'text': event['text'],
            'file_url': event['file_url'],
            # 'user': event['user'],
        }))



    @database_sync_to_async
    def save_message(self, order_id, user, sender_type, text,file_url,message_type):
        from Accountapp.models import ChatMessage, OrderTable, DeliveryBoyTable, ProfileTable
        
        order = OrderTable.objects.get(id=order_id)
        chat_data = {}
        if sender_type == 'DELIVERYBOY':
            delivery = DeliveryBoyTable.objects.get(userid=user)
            chat_data = {
                'order': order,
                'delivery_boy': delivery,
                'user': None,
                'sender_type': sender_type,
                'text': text,
                'message_type': message_type
            }
           
            
        elif sender_type == 'USER':
            profile = ProfileTable.objects.get(user=user)
            chat_data = {
                'order': order,
                'delivery_boy': None,
                'user': profile,
                'sender_type': sender_type,
                'text': text,
                'message_type': message_type
            }

        # Handle file saving
        if message_type == 'IMAGE':
            from django.core.files.base import ContentFile
            import base64
            import uuid

            format, imgstr = file_url.split(';base64,')  # expects "data:image/png;base64,<base64data>"
            ext = format.split('/')[-1]
            file_name = f"{uuid.uuid4()}.{ext}"
            chat_data['image'] = ContentFile(base64.b64decode(imgstr), name=file_name)

        elif message_type == 'AUDIO':
            from django.core.files.base import ContentFile
            import base64
            import uuid

            format, audstr = file_url.split(';base64,')  # expects "data:audio/wav;base64,<base64data>"
            ext = format.split('/')[-1]
            file_name = f"{uuid.uuid4()}.{ext}"
            chat_data['audio'] = ContentFile(base64.b64decode(audstr), name=file_name)

        ChatMessage.objects.create(**chat_data)
          