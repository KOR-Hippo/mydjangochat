from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from chat.models import Room


class ChatConsumer(JsonWebsocketConsumer):
    # room_name에 상관없이 모든 유저들을 square라는 그룹 안에서 채팅하도록 함
    # SQUARE_GROUP_NAME = "square"
    # groups = [SQUARE_GROUP_NAME]

    def __init__(self):
        super().__init__()
        self.group_name = ""  # 인스턴스 변수 group_name 추가

    # 웹소켓 클라이언트가 접속을 요청할 때 호출하는 함수
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

            # 본 웹소켓 접속을 허용
            self.accept()

    # 웹소켓 클라이언트와의 접속이 끊겼을 때 호출됨
    def disconnect(self, code):
        # 소속 그룹에서 빠져나와야함
        if self.group_name:
            async_to_sync(self.channel_layer.group_discard)(
                self.group_name, self.channel_name
            )

    # 단일 클라이언트로부터 메세지를 받으면 호출됨ㅁ
    def receive_json(self, content, **kwargs):
        user = self.scope["user"]

        _type = content["type"]

        if _type == "chat.message":
            sender = user.username
            message = content["message"]

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

    # 그룹을 통해 type="chat.message" 메세지를 받으면 호출됨
    def chat_message(self, message_dict):
        # 접속되어있는 클라이언트에게 메세지를 전달
        self.send_json({
            "type": "chat.message",
            "message": message_dict["message"],
            "sender": message_dict["sender"],
        })
