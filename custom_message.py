import json

MSG_CONNECTED = 0;
MSG_LOGIN = 1;
MSG_LOGIN_RES = 2;

message_template = [];

def makeMessage(message_id):
  print("make message", message_id);
  return json.loads(message_template[message_id]);

def initCustomMessage():
  with open('messages.json') as text:
    json_object = json.load(text);

    for obj in json_object:
      text_data = str(obj).replace("'", '"');
      message_template.append(text_data);

    print("message load complate", message_template);
