from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer

from chat.models import Room


# JsonWebsocketConsumer는 receive_json/send_json 메서드를 추가로 지원합니다.
class ChatConsumer(JsonWebsocketConsumer):
    # room_name에 상관없이 모든 유저들을 광장(square)을 통해 채팅토록 합니다.
    # SQUARE_GROUP_NAME = "square"
    # groups = [SQUARE_GROUP_NAME]

    def __init__(self):
        super().__init__()
        # 인스턴스 변수는 생성자 내에서 정의합니다.
        self.group_name = ""  # 인스턴스 변수 group_name 추가

    # 웹소켓 클라이언트가 접속을 요청할 때, 호출됩니다.
    def connect(self):
        # chat/routing.py 내 websocket_urlpatterns 에 따라
        # /ws/chat/test/chat/ 요청의 경우, self.scope["url_route"] 값은?
        # > {'args': (), 'kwargs': {'room_name': 'test'}}
        user = self.scope["user"]

        if not user.is_authenticated:
            self.close()
        else:
            room_pk = self.scope["url_route"]["kwargs"]["room_pk"]

            # room_name에 기반하여 그룹명 생성
            self.group_name = Room.make_chat_group_name(room_pk=room_pk)

            async_to_sync(self.channel_layer.group_add)(
                self.group_name,
                self.channel_name
            )

            # 본 웹소켓 접속을 허용합니다.
            # connect 메서드 기본 구현에서는 self.accpet() 호출부만 있습니다.
            self.accept()

    # 웹소켓 클라이언트와의 접속이 끊겼을 때, 호출됩니다.
    def disconnect(self, code):
        # 소속 그룹에서 빠져나와야합니다.
        if self.group_name:
            async_to_sync(self.channel_layer.group_discard)(
                self.group_name, self.channel_name
            )

    # 단일 클라이언트로부터 메세지를 받으면 호출됩니다.
    def receive_json(self, content, **kwargs):
        user = self.scope["user"]

        _type = content["type"]

        if _type == "chat.message":
            sender = user.username
            message = content["message"]
            # Publish 과정: "square" 그룹 내 다른 Consumer들에게 메세지를 전달합니다.
            async_to_sync(self.channel_layer.group_send)(
                self.group_name,
                {
                    "type": "chat.message",
                    "message": message,
                    "sender": sender,
                },
            )
        else:
            print(f"Invalid message type : {_type}")

    # 그룹을 통해 type="chat.message" 메세지를 받으면 호출됩니다.
    def chat_message(self, message_dict):
        # 접속되어있는 클라이언트에게 메세지를 전달합니다.
        # 클라이언트에게 전달하는 값들을 명시적으로 지정했습니다.
        # 원하는 포맷으로 메세지를 구성할 수 있습니다.
        self.send_json({
            "type": "chat.message",
            "message": message_dict["message"],
            "sender": message_dict["sender"],
        })
