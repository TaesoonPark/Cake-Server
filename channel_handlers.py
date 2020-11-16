import threading

from session_manager import SessionManager
from game_room import *
from worker_thread import IOWorkerManager

#TODO 채널 유저 수 조절
class Channel:
  def __init__(self, channel_id):
    self.channel_id = channel_id;
    self.sessions_lock = threading.Lock();
    self.sessions = dict();
    self.rooms_lock = threading.Lock();
    self.rooms = dict();
    self.session_to_room_lock = threading.Lock();
    self.session_to_room = dict();

  # 채널에 유저 세션을 추가
  def add_user(self, session_id, nickname):
    self.sessions_lock.acquire();
    if session_id in self.sessions:
      print("duplicate session in channel", self.channel_id);
      return False;

    session = SessionManager().get_session(session_id);
    if session == None:
      self.sessions_lock.release();
      print("cannot find session", session_id);
      return False;

    self.sessions[session_id] = session;
    self.sessions_lock.release();
    return True;

  # 채널에서 유저 세션을 제거
  def remove_user(self, session_id):
    self.sessions_lock.acquire();
    if session_id in self.sessions:
      del self.sessions[session_id];
    self.sessions_lock.release();

  # 현재 채널에 유저가 있는지 검사.
  def find_user(self, session_id):
    self.sessions_lock.acquire();
    result = None;
    if session_id in self.sessions:
      result = self.sessions[session_id];
    self.sessions_lock.release();
    return result;

  # 현재 채널에 있는 모든 세션에 메시지 전송
  def send_to_all(self, msg):
    self.sessions_lock.acquire();
    for session_id in self.sessions:
      IOWorkerManager().push_io_message(session_id, msg);
    self.sessions_lock.release();

  # 게임룸을 생성. title을 key로 사용하여 중복생성 불가
  def create_room(self, title, nickname):
    self.rooms_lock.acquire();
    result = (False, None);
    if title not in self.rooms:
      new_room = GameRoom(title, nickname);
      self.rooms[title] = new_room;
      result = (True, new_room);

    self.rooms_lock.release()
    return result;

  # 게임룸 제거. 남은 유저가 없을때만 호출된다.
  def delete_room(self, title):
    self.rooms_lock.acquire();
    if title in self.rooms:
      del self.rooms[title];
    self.rooms_lock.release();
    return;

  # 현재 채널의 전체 게임룸 정보 획득
  def get_room_list(self):
    room_list = [];
    self.rooms_lock.acquire();
    for title, room in self.rooms.items():
      room_list.append(room.get_room_summary());
    self.rooms_lock.release();
    return room_list;

  # 게임룸에 유저 진입
  def join_room(self, session_id, nickname, title):
    self.rooms_lock.acquire();
    join_result = (False, dict());
    if title in self.rooms:
      result = self.rooms[title].add_user(session_id, nickname);
      if result == True:
        info = self.rooms[title].get_room_info();
        join_result = (result, info);
        self.session_to_room_lock.acquire();
        self.session_to_room[session_id] = title;
        self.session_to_room_lock.release();
    self.rooms_lock.release();
    return join_result;

  # 게임룸에서 유저 제거
  def remove_user_from_room(self, session_id):
    result = False;
    self.session_to_room_lock.acquire();
    if session_id in self.session_to_room:
      room_title = self.session_to_room[session_id];

      self.rooms_lock.acquire();
      self.rooms[room_title].remove_user(session_id);
      if self.rooms[room_title].get_session_count() == 0:
        del self.rooms[room_title];
      self.rooms_lock.release();

      del self.session_to_room[session_id];
      result = True;
    self.session_to_room_lock.release();
    return result;

  # 게임 시작
  def start_game(self, session_id):
    result = False;
    self.session_to_room_lock.acquire();
    if session_id in self.session_to_room:
      room_title = self.session_to_room[session_id];
      self.rooms_lock.acquire();
      result = self.rooms[room_title].start_game(session_id);
      self.rooms_lock.release();
    self.session_to_room_lock.release();
    return result;


active_channels = [];


# 채널 리스트 초기화
def init_channels(channel_count=1):
  print("init_channels", channel_count);

  global active_channels;
  for channel_id in range(0, channel_count):
    active_channels.append(Channel(channel_id));


# 이하 message_handlers에서 호출하기 위한 함수들
def add_user_to_channel(session_id, nickname, channel_id=0):
  global active_channels;

  if channel_id >= len(active_channels):
    return (False, -1);

  channel = active_channels[channel_id];
  result = channel.add_user(session_id, nickname);

  return (result, channel_id);


def remove_user_from_channel(session_id):
  global active_channels;
  for active_channel in active_channels:
    active_channel.remove_user(session_id);
    active_channel.remove_user_from_room(session_id);


def send_channel_chat(session_id, channel_chat):
  global active_channels;

  for active_channel in active_channels:
    session = active_channel.find_user(session_id);
    if session == None:
      continue;

    context_result = session.get_context("nickname");
    if not context_result[0]:
      print("invalid session. cannot find nickname context");
      continue;

    channel_chat["nickname"] = context_result[1];
    active_channel.send_to_all(channel_chat);
    break;


def create_room(session_id, title):
  global active_channels;
  
  for active_channel in active_channels:
    session = active_channel.find_user(session_id);
    if session == None:
      continue;

    context_result = session.get_context("nickname");
    if not context_result[0]:
      print("invalid session. cannot find nickname context");
      continue;

    room_result = active_channel.create_room(title, context_result[1]);
    if room_result[0] == False:
      return False;

    result = join_room(session_id, title);
    if result == False:
      print("wrong process create_room");
      active_channel.delete_room(title);
      return False;

    return True;


def get_room_list(session_id):
  global active_channels;

  for active_channel in active_channels:
    session = active_channel.find_user(session_id);
    if session == None:
      continue;

    return active_channel.get_room_list();


def join_room(session_id, title):
  global active_channels;

  for active_channel in active_channels:
    session = active_channel.find_user(session_id);
    if session == None:
      continue;

    context_result = session.get_context("nickname");
    if not context_result[0]:
      print("invalid session. cannot find nickname context");
      continue;

    return active_channel.join_room(session_id, context_result[1], title);


def leave_room(session_id):
  global active_channels;

  for active_channel in active_channels:
    session = active_channel.find_user(session_id);
    if session == None:
      continue;

    return active_channel.remove_user_from_room(session_id);


def start_game(session_id):
  global active_channels;

  for active_channel in active_channels:
    session = active_channel.find_user(session_id);
    if session == None:
      continue;

    return active_channel.start_game(session_id);
