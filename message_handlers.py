from worker_thread import addMessageHandler
from custom_message import *
from session_manager import *

def handleLogin(message):
  print("handleLogin", message);
  if message["message_id"] != MSG_LOGIN:
    return;

  session_id = message["session_id"];
  res = makeMessage(MSG_LOGIN_RES);
  print("makemessage");
  res["result"] = True;

  sendMessage(session_id, res);

def initHandlers():
  addMessageHandler(MSG_LOGIN, handleLogin);

