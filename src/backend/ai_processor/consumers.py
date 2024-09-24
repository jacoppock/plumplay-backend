import json

from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        text = data.get("text", "")

        # Call the process_voice_memo method
        response = await self.process_voice_memo(text)

        # Send the response back to the WebSocket
        await self.send(text_data=json.dumps({"response": response}))

    async def process_voice_memo(self, text):
        # Simulate calling the process_voice_memo method
        # You can import the method and call it directly if needed
        from channels.db import database_sync_to_async
        from django.http import HttpRequest

        from .views import process_voice_memo

        request = HttpRequest()
        request.method = "POST"
        request.POST = {"text": text}

        response = await database_sync_to_async(process_voice_memo)(request)
        return response.content.decode()
