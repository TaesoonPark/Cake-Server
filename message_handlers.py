from worker_thread import IOWorkerManager, WorkerManager
from custom_message import *
from channel_handlers import add_user_to_channel, send_channel_chat, create_room, get_room_list, join_room, start_game
from session_manager import SessionManager

def handle_login(message):
  print("handle_login", message);
  if message["message_id"] != MSG_LOGIN:
    return;

  session_id = message["session_id"];
  nickname = message["nickname"];

  result = add_user_to_channel(session_id, nickname);

  res = make_message(MSG_LOGIN_RES);
  res["result"] = result[0];
  if result[0] == True:
    res["channel_id"] = result[1];
    res["nickname"] = nickname;
  else:
    res["channel_id"] = -1;
    res["nickname"] = "";

  SessionManager().add_session_context(session_id, "nickname", nickname);
  IOWorkerManager().push_io_message(session_id, res);


def handle_chat(message):
  print("handle_chat", message);
  if message["message_id"] != MSG_SEND_CHAT:
    return;
  
  session_id = message["session_id"];
  text = message["text"];

  channel_chat = make_message(MSG_RECV_CHAT);
  channel_chat["text"] = text;
  send_channel_chat(session_id, channel_chat);


def handle_make_room(message):
  print("handle_make_room");
  if message["message_id"] != MSG_MAKE_ROOM:
    return;

  session_id = message["session_id"];
  title = message["title"];
  result = create_room(session_id, title);

  res = make_message(MSG_MAKE_ROOM_ACK);
  res["result"] = result;

  IOWorkerManager().push_io_message(session_id, res);


def handle_room_list(message):
  print("handle_room_list");
  if message["message_id"] != MSG_ROOM_LIST:
    return;

  session_id = message["session_id"];
  room_list = get_room_list(session_id);

  res = make_message(MSG_ROOM_LIST_ACK);
  res["room_list"].clear();
  if room_list != None:
    for room_info in room_list:
      entry = dict();
      entry["title"] = room_info[0];
      entry["owner_nickname"] = room_info[1];
      entry["session_count"] = room_info[2];
      res["room_list"].append(entry);

  IOWorkerManager().push_io_message(session_id, res);


def handle_join_room(message):
  print("handle_join_room");

  session_id = message["session_id"];
  title = message["title"];
  result = join_room(session_id, title);

  res = make_message(MSG_JOIN_ROOM_ACK);
  res["result"] = result[0];
  res["session_list"].clear();
  if result[1] != None:
    for session_id, nickname in result[1].items():
      entry = dict()
      entry["session_id"] = session_id;
      entry["nickname"] = nickname;
      res["session_list"].append(entry);

  IOWorkerManager().push_io_message(session_id, res);


def handle_leave_room(message):
  print("handle_leave_room");

  session_id = message["session_id"];

  result = leave_room(session_id);
  res = make_message(MSG_LEAVE_ROOM_ACK);
  res["result"] = result;

  IOWorkerManager().push_io_message(session_id, res);


def handle_start_game(message):
  print("handle_start_game");

  session_id = message["session_id"];

  result = start_game(session_id);
  res = make_message(MSG_START_GAME_ACK);
  res["result"] = result;

  IOWorkerManager().push_io_message(session_id, res);


# 메시지 핸들러 등록
def init_handlers():
  WorkerManager().add_message_handler(MSG_LOGIN, handle_login);
  WorkerManager().add_message_handler(MSG_SEND_CHAT, handle_chat);
  WorkerManager().add_message_handler(MSG_MAKE_ROOM, handle_make_room);
  WorkerManager().add_message_handler(MSG_ROOM_LIST, handle_room_list);
  WorkerManager().add_message_handler(MSG_JOIN_ROOM, handle_join_room);
  WorkerManager().add_message_handler(MSG_LEAVE_ROOM, handle_leave_room);
  WorkerManager().add_message_handler(MSG_START_GAME, handle_start_game);
