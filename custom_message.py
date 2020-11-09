import json

MSG_CONNECTED = 1;
MSG_LOGIN = 2;
MSG_LOGIN_RES = 3;

def makeMessage(message_idx):
  string = '{"message_id":' + str(message_idx) + '}';

  return json.loads(string);
