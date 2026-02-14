import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import ChatThread, ChatMessage
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return

        self.thread_id = self.scope['url_route']['kwargs']['thread_id']
        self.room_group_name = f'chat_{self.thread_id}'

        # Verify user is participant in thread
        if not await self.is_participant():
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        
        # Mark all previous messages as delivered if recipient just connected
        await self.mark_delivered()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'message':
            content = data.get('message')
            reply_to_id = data.get('reply_to_id')
            print(f"Message received: {content} from {self.user}, reply_to: {reply_to_id}")
            if content:
                msg = await self.save_message(content, reply_to_id)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': content,
                        'sender': self.user.username,
                        'sender_id': self.user.id,
                        'message_id': msg.id,
                        'temp_id': data.get('temp_id'),
                        'attachment_url': msg.attachment.url if msg.attachment else None,
                        'timestamp': msg.timestamp.strftime('%H:%M'),
                        'is_delivered': msg.is_delivered,
                        'is_read': msg.is_read,
                        'reply_to': {
                            'id': msg.reply_to.id,
                            'content': msg.reply_to.content,
                            'sender': msg.reply_to.sender.username
                        } if msg.reply_to else None
                    }
                )
        elif action == 'typing':
            print(f"User typing: {self.user.username} is_typing: {data.get('is_typing')}")
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_typing',
                    'username': self.user.username,
                    'is_typing': data.get('is_typing', False)
                }
            )
        elif action == 'read_receipt':
            msg_id = data.get('message_id')
            if msg_id:
                await self.mark_read(msg_id)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'message_status',
                        'message_id': msg_id,
                        'status': 'read'
                    }
                )
        elif action == 'edit_message':
            msg_id = data.get('message_id')
            new_content = data.get('message')
            if msg_id and new_content:
                success = await self.edit_message(msg_id, new_content)
                if success:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'message_edited',
                            'message_id': msg_id,
                            'message': new_content
                        }
                    )
        elif action == 'delete_message':
            msg_id = data.get('message_id')
            if msg_id:
                success = await self.delete_message(msg_id)
                if success:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'message_deleted',
                            'message_id': msg_id
                        }
                    )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    async def user_typing(self, event):
        await self.send(text_data=json.dumps(event))

    async def message_status(self, event):
        await self.send(text_data=json.dumps(event))

    async def message_edited(self, event):
        await self.send(text_data=json.dumps(event))

    async def message_deleted(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def is_participant(self):
        return ChatThread.objects.filter(id=self.thread_id, participants=self.user).exists()

    @database_sync_to_async
    def save_message(self, content, reply_to_id=None):
        thread = ChatThread.objects.get(id=self.thread_id)
        reply_to = None
        if reply_to_id:
            try:
                reply_to = ChatMessage.objects.get(id=reply_to_id)
            except ChatMessage.DoesNotExist:
                pass
                
        msg = ChatMessage.objects.create(
            thread=thread,
            sender=self.user,
            content=content,
            reply_to=reply_to
        )
        # Update thread's updated_at
        thread.save()
        return msg

    @database_sync_to_async
    def mark_delivered(self):
        # Mark messages sent by others as delivered when this user connects
        ChatMessage.objects.filter(thread_id=self.thread_id, is_delivered=False).exclude(sender=self.user).update(is_delivered=True, delivered_at=timezone.now())

    @database_sync_to_async
    def mark_read(self, msg_id):
        try:
            msg = ChatMessage.objects.get(id=msg_id)
            if msg.sender != self.user:
                msg.mark_as_read()
        except ChatMessage.DoesNotExist:
            pass

    @database_sync_to_async
    def edit_message(self, msg_id, new_content):
        try:
            msg = ChatMessage.objects.get(id=msg_id, sender=self.user)
            msg.content = new_content
            msg.is_edited = True
            msg.save()
            return True
        except ChatMessage.DoesNotExist:
            return False

    @database_sync_to_async
    def delete_message(self, msg_id):
        try:
            msg = ChatMessage.objects.get(id=msg_id, sender=self.user)
            msg.delete()
            return True
        except ChatMessage.DoesNotExist:
            return False
