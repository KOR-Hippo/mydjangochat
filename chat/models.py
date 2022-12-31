from django.db import models
from django.conf import settings  # HMM...


# Create your models here.
class Room(models.Model):
    # 한글 채팅방 이름 필드로서 사용하려 합니다.
    # name 필드에서는 유일성 체크를 하지 않으므로
    # 같은 이름의 채팅방도 만들 수 있습니다.
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
        # 쿼리셋 디폴트 정렬옵션 지정을 추천
        ordering = ["-pk"]
