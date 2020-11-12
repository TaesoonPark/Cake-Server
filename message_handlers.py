from worker_thread import IOWorkerManager, WorkerManager
from custom_message import *
from channel_handlers import addUserToChannel, sendChannelChat, createRoom, getRoomList, joinRoom, startGame

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

  IOWorkerManager().push_io_message(session_id, res);


def handleChat(message):
  print("handleChat", message);
  if message["message_id"] != MSG_SEND_CHAT:
    return;
  
  session_id = message["session_id"];
  text = message["text"];

  channel_chat = makeMessage(MSG_RECV_CHAT);
  channel_chat["text"] = text;
  sendChannelChat(session_id, channel_chat);


def handleMakeRoom(message):
  print("handleMakeRoom");
  if message["message_id"] != MSG_MAKE_ROOM:
    return;

  session_id = message["session_id"];
  title = message["title"];
  result = createRoom(session_id, title);

  res = makeMessage(MSG_MAKE_ROOM_ACK);
  res["result"] = result;

  IOWorkerManager().push_io_message(session_id, res);


def handleRoomList(message):
  print("handleRoomList");
  if message["message_id"] != MSG_ROOM_LIST:
    return;

  session_id = message["session_id"];
  room_list = getRoomList(session_id);

  res = makeMessage(MSG_ROOM_LIST_ACK);
  res["room_list"].clear();
  if room_list != None:
    for room_info in room_list:
      entry = dict();
      entry["title"] = room_info[0];
      entry["owner_nickname"] = room_info[1];
      entry["session_count"] = room_info[2];
      res["room_list"].append(entry);

  IOWorkerManager().push_io_message(session_id, res);


def handleJoinRoom(message):
  print("handleJoinRoom");

  session_id = message["session_id"];
  title = message["title"];
  result = joinRoom(session_id, title);

  res = makeMessage(MSG_JOIN_ROOM_ACK);
  res["result"] = result[0];
  res["session_list"].clear();
  if result[1] != None:
    for session_id, nickname in result[1].items():
      entry = dict()
      entry["session_id"] = session_id;
      entry["nickname"] = nickname;
      res["session_list"].append(entry);

  IOWorkerManager().push_io_message(session_id, res);


def handleLeaveRoom(message):
  print("handleLeaveRoom");

  session_id = message["session_id"];

  result = leaveRoom(session_id);
  res = makeMessage(MSG_LEAVE_ROOM_ACK);
  res["result"] = result;

  IOWorkerManager().push_io_message(session_id, res);


def handleStartGame(message):
  print("handleStartGame");

  session_id = message["session_id"];

  result = startGame(session_id);
  res = makeMessage(MSG_START_GAME_ACK);
  res["result"] = result;

  IOWorkerManager().push_io_message(session_id, res);


# 메시지 핸들러 등록
def initHandlers():
  WorkerManager().add_message_handler(MSG_LOGIN, handleLogin);
  WorkerManager().add_message_handler(MSG_SEND_CHAT, handleChat);
  WorkerManager().add_message_handler(MSG_MAKE_ROOM, handleMakeRoom);
  WorkerManager().add_message_handler(MSG_ROOM_LIST, handleRoomList);
  WorkerManager().add_message_handler(MSG_JOIN_ROOM, handleJoinRoom);
  WorkerManager().add_message_handler(MSG_LEAVE_ROOM, handleLeaveRoom);
  WorkerManager().add_message_handler(MSG_START_GAME, handleStartGame);
