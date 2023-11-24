import json

from channels.db import database_sync_to_async
from django.core.exceptions import ValidationError

from summery_creator.summery.models import Lesson
from summery_creator.utils.channels import BaseConsumer


class LessonConsumer(BaseConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.id = None
        self.room_group_name = None
        self.lesson = None

    @database_sync_to_async
    def get_lesson(self) -> bool:
        try:
            self.lesson = Lesson.objects.get(id=self.id)
        except (Lesson.DoesNotExist, ValidationError):
            return False
        return True

    async def connect(self):
        try:
            self.id = self.scope["url_route"]["kwargs"]["uuid"]
        except KeyError:
            return

        self.room_group_name = f"lesson_{self.id}"

        await self.accept()
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        session_status = await self.get_lesson()
        if not session_status:
            await self.send_error("not found")
            await self.disconnect(close_code=None)
            return

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.close()

    # async def receive(self, text_data=None, bytes_data=None, **kwargs):
    #     if type(text_data) is not str:
    #         await self.send_error("Validation error")
    #     else:
    #         send_message.apply_async(kwargs={"id": self.id, "question": text_data})
    #     return text_data

    @classmethod
    async def encode_json(cls, content):
        return json.dumps(content, ensure_ascii=False)

    async def message(self, event):
        data = event["data"]
        await self.send_json(data)
