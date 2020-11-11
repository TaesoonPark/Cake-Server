import json

# 메시지 아이디 선언. 상세 스펙은 messages.json 참조
MSG_CONNECTED = 0;
MSG_LOGIN = 1;
MSG_LOGIN_RES = 2;
MSG_SEND_CHAT = 3;
MSG_RECV_CHAT = 4;
MSG_MAKE_ROOM = 5;
MSG_MAKE_ROOM_ACK = 6;
MSG_ROOM_LIST = 7;
MSG_ROOM_LIST_ACK = 8;
MSG_JOIN_ROOM = 9;
MSG_JOIN_ROOM_ACK = 10;
MSG_LEAVE_ROOM = 11;
MSG_LEAVE_ROOM_ACK = 12;

message_template = [];

# 메시지 기본형 생성
def makeMessage(message_id):
  #print("make message", message_id);
  return json.loads(message_template[message_id]);


# messages.json 파일 로드. 기본형 적재
def initCustomMessage():
  with open('messages.json') as text:
    json_object = json.load(text);

    for obj in json_object:
      text_data = str(obj).replace("'", '"');
      message_template.append(text_data);

    print("message load complate", message_template);
