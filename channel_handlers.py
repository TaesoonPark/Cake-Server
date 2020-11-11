import threading

from session_manager import *
from room_handlers import *

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


  def addUser(self, session_id, nickname):
    self.sessions_lock.acquire();
    if session_id in self.sessions:
      print("duplicate session in channel", self.channel_id);
      return False;

    client_socket = getSession(session_id);
    if client_socket == None:
      self.sessions_lock.release();
      print("cannot find session", session_id);
      return False;

    self.sessions[session_id] = (client_socket, nickname);
    self.sessions_lock.release();
    return True;


  def removeUser(self, session_id):
    self.sessions_lock.acquire();
    del self.sessions[session_id];
    self.sessions_lock.release();


  def findUser(self, session_id):
    self.sessions_lock.acquire();
    result = (None, "");
    if session_id in self.sessions:
      result = self.sessions[session_id];
    self.sessions_lock.release();
    return result;


  def sendToAll(self, msg):
    self.sessions_lock.acquire();
    for session_id in self.sessions:
      sendMessage(session_id, msg);
    self.sessions_lock.release();


  def createRoom(self, title, nickname):
    self.rooms_lock.acquire();
    result = (False, None);
    if title not in self.rooms:
      new_room = Room(title, nickname);
      self.rooms[title] = new_room;
      result = (True, new_room);

    self.rooms_lock.release()
    return result;


  def deleteRoom(self, title):
    self.rooms_lock.acquire();
    if title in self.rooms:
      del self.rooms[title];
    self.rooms_lock.release();
    return;


  def getRoomList(self):
    room_list = [];
    self.rooms_lock.acquire();
    for title, room in self.rooms.items():
      room_list.append(room.getRoomSummary());

    self.rooms_lock.release();
    return room_list;


  def joinRoom(self, session_id, nickname, title):
    self.rooms_lock.acquire();
    join_result = (False, []);
    if title in self.rooms:
      result = self.rooms[title].addUser(session_id, nickname);
      if result == True:
        info = self.rooms[title].getRoomInfo();
        join_result = (result, info);
        self.session_to_room_lock.acquire();
        self.session_to_room[session_id] = title;
        self.session_to_room_lock.release();

    self.rooms_lock.release();
    return join_result;


  def removeUserFromRoom(self, session_id):
    result = False;
    self.session_to_room_lock.acquire();
    if session_id in self.session_to_room:
      room_title = self.session_to_room[session_id];

      self.rooms_lock.acquire();
      self.rooms[room_title].removeUser(session_id);
      if self.rooms[room_title].session_count == 0:
        del self.rooms[room_title];
      self.rooms_lock.release();

      del self.session_to_room[session_id];
      result = True;
    self.session_to_room_lock.release();
    return result;


active_channels = [];


def initChannels(channel_count=1):
  print("initChannels", channel_count);

  global active_channels;
  for channel_id in range(0, channel_count):
    active_channels.append(Channel(channel_id));


def addUserToChannel(session_id, nickname, channel_id=0):
  global active_channels;

  if channel_id >= len(active_channels):
    return (False, -1);

  channel = active_channels[channel_id];
  result = channel.addUser(session_id, nickname);

  return (result, channel_id);


def removeUserFromChannel(session_id):
  global active_channels;
  for active_channel in active_channels:
    active_channel.removeUser(session_id);
    active_channel.removeUserFromRoom(session_id);


def sendChannelChat(session_id, channel_chat):
  global active_channels;

  for active_channel in active_channels:
    info = active_channel.findUser(session_id);
    if info[0] == None:
      continue;

    channel_chat["nickname"] = info[1];
    active_channel.sendToAll(channel_chat);
    break;


def createRoom(session_id, title):
  global active_channels;
  
  for active_channel in active_channels:
    info = active_channel.findUser(session_id);
    if info[0] == None:
      continue;

    room_result = active_channel.createRoom(title, info[1]);
    if room_result[0] == False:
      return False;

    result = joinRoom(session_id, title);
    if result == False:
      print("wrong process createRoom");
      active_channel.deleteRoom(title);
      return False;

    return True;


def getRoomList(session_id):
  global active_channels;

  for active_channel in active_channels:
    info = active_channel.findUser(session_id);
    if info[0] == None:
      continue;

    return active_channel.getRoomList();


def joinRoom(session_id, title):
  global active_channels;

  for active_channel in active_channels:
    info = active_channel.findUser(session_id);
    if info[0] == None:
      continue;

    return active_channel.joinRoom(session_id, info[1], title);


def leaveRoom(session_id):
  global active_channels;

  for active_channel in active_channels:
    info = active_channel.findUser(session_id);
    if info[0] == None:
      continue;

    return active_channel.removeUserFromRoom(session_id);