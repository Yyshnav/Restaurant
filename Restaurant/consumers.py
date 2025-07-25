# from channels.generic.websocket import AsyncWebsocketConsumer
# import json
# from channels.db import database_sync_to_async
# # from Accountapp.models import ChatMessage, OrderTable
# from django.contrib.auth import get_user_model
# from rest_framework_simplejwt.tokens import UntypedToken
# from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
# from jwt import decode as jwt_decode
# from django.conf import settings
# @database_sync_to_async
# def save_message(self, order_id, user, sender_type, message):
#     # ✅ Import models here instead
#     from Accountapp.models import ChatMessage, OrderTable

#     order = OrderTable.objects.get(id=order_id)
#     ChatMessage.objects.create(
#         order=order,
#         user=user if sender_type == 'USER' else None,
#         delivery_boy=user if sender_type == 'DELIVERYBOY' else None,
#         sender_type=sender_type,
#         message=message
#     )

# User = get_user_model()

# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.order_id = self.scope['url_route']['kwargs']['order_id']
#         self.room_group_name = f'chat_{self.order_id}'

#         # Authenticate user using token
#         token = self.scope['query_string'].decode().split('=')[-1]
#         try:
#             validated_token = UntypedToken(token)
#             decoded_data = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
#             self.user = await database_sync_to_async(User.objects.get)(id=decoded_data['user_id'])
#             await self.channel_layer.group_add(self.room_group_name, self.channel_name)
#             await self.accept()
#         except:
#             await self.close()

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

#     async def receive(self, text_data):
#         data = json.loads(text_data)

#         message_type = data.get('message_type')
#         sender_type = data.get('sender_type')
#         text = data.get('text')
#         file_url = data.get('file_url')

#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message_type': message_type,
#                 'sender_type': sender_type,
#                 'text': text,
#                 'file_url': file_url
#             }
#         )

#     # Save to DB
#         await self.save_message(self.order_id, self.user, sender_type, text)

#     async def chat_message(self, event):
#         await self.send(text_data=json.dumps(event))

#     # @database_sync_to_async
#     # def save_message(self, order_id, user, sender_type, message):
#     #     order = OrderTable.objects.get(id=order_id)
#     #     ChatMessage.objects.create(
#     #         order=order,
#     #         user=user if sender_type == 'USER' else None,
#     #         delivery_boy=user if sender_type == 'DELIVERYBOY' else None,
#     #         sender_type=sender_type,
#     #         message=message
#     #     )


from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from jwt import decode as jwt_decode
from django.conf import settings
import json

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
        await self.save_message(self.order_id, self.user, sender_type, text)

    async def chat_message(self, event):
        # Send message to WebSocket client
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_message(self, order_id, user, sender_type, text):
        # Import models inside the method to avoid circular imports
        from Accountapp.models import ChatMessage, OrderTable

        order = OrderTable.objects.get(id=order_id)
        ChatMessage.objects.create(
            order=order,
            user=user if sender_type == 'USER' else None,
            delivery_boy=user if sender_type == 'DELIVERYBOY' else None,
            sender_type=sender_type,
            text=text
        )