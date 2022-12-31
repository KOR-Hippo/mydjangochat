from django.db import models
from django.conf import settings  # HMM...


# Create your models here.
class Room(models.Model):
    # 한글 채팅방 이름 필드로써 사용
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_room_set",
    )
    name = models.CharField(max_length=100)

    @property
    def chat_group_name(self):
        return self.make_chat_group_name(room=self)

    @staticmethod
    def make_chat_group_name(room=None, room_pk=None):
        return "chat-%s" % (room_pk or room.pk)
    
    class Meta:
        ordering = ["-pk"]
