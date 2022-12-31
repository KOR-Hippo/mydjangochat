import json

from channels.generic.websocket import JsonWebsocketConsumer


class LiveblogConsumer(JsonWebsocketConsumer):
    # 메세지를 받을 그룹을 명시합니다.
    groups = ["liveblog"]

    # 그룹을 통해 받은 메세지를 그대로 웹소켓 클라이언트에게 전달합니다. (self.send(전달할_메세지))
    # 메세지의 type 값과 같은 이름의 메서드가 호출됩니다.

    # ex) type "liveblog.post.created" ➡ "liveblog_post_created" 메서드 호출 ➡ 마침표(.)를 언더바(_)로 바꿉니다.
    def liveblog_post_created(self, event_dict):
        self.send_json(event_dict)
        # self.send(json.dumps(event_dict))

    def liveblog_post_updated(self, event_dict):
        self.send_json(event_dict)
        # self.send(json.dumps(event_dict))

    def liveblog_post_deleted(self, event_dict):
        self.send_json(event_dict)
        # self.send(json.dumps(event_dict))


class EchoConsumer(JsonWebsocketConsumer):

    def receive_json(self, content, **kwargs):
        print("수신 :", content)
        self.send_json({
            "content": content["content"],
            "user": content["user"],
        })


        # WebsocketConsumer -> JsonWebsocketConsumer로 바꾸면서 코드가 더욱 간결해짐
        # 우리가 따로 JSON 인코딩/디코딩 수행할 필요 없어져서!
        # def receive(self, text_data=None, bytes_data=None):
        # self.send(f"You said : {text_data}")
        # obj = json.loads(text_data)
        # print("수신 :", obj)
        # json_string = json.dumps({
        #     "content": obj["content"],
        #     "user": obj["user"],
        # })
        # self.send(json_string)
