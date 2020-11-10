from worker_thread import addMessageHandler
from custom_message import *
from session_manager import *
from channel_handlers import addUserToChannel, sendChannelChat

def handleLogin(message):
  print("handleLogin", message);
  if message["message_id"] != MSG_LOGIN:
    return;

  session_id = message["session_id"];
  nickname = message["nickname"];

  result = addUserToChannel(session_id, nickname);

  res = makeMessage(MSG_LOGIN_RES);
  res["result"] = result[0];
  if result[0] == True:
    res["channel_id"] = result[1];
    res["nickname"] = nickname;
  else:
    res["channel_id"] = -1;
    res["nickname"] = "";

  sendMessage(session_id, res);


def handleChat(message):
  print("handleChat", message);
  if message["message_id"] != MSG_SEND_CHAT:
    return;
  
  session_id = message["session_id"];
  text = message["text"];

  channel_chat = makeMessage(MSG_RECV_CHAT);
  channel_chat["text"] = text;
  sendChannelChat(session_id, channel_chat);


def initHandlers():
  addMessageHandler(MSG_LOGIN, handleLogin);
  addMessageHandler(MSG_SEND_CHAT, handleChat);
