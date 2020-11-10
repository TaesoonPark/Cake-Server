import threading

from session_manager import *

#TODO 채널 유저 수 조절
class Channel:
  def __init__(self, channel_id):
    self.sessions = dict();
    self.channel_id = channel_id;
    self.channel_lock = threading.Lock();
    print("channel construct", channel_id);


  def addUser(self, session_id, nickname):
    self.channel_lock.acquire();
    if session_id in self.sessions:
      print("duplicate session in channel", channel_id);
      return False;

    client_socket = getSession(session_id);
    if client_socket == None:
      print("cannot find session", session_id);
      return False;

    self.sessions[session_id] = (client_socket, nickname);
    self.channel_lock.release();
    return True;


  def removeUser(self, session_id):
    self.channel_lock.acquire();
    del self.sessions[session_id];
    self.channel_lock.release();


  def findUser(self, session_id):
    self.channel_lock.acquire();
    result = (None, "");
    if session_id in self.sessions:
      result = self.sessions[session_id];
    self.channel_lock.release();
    return result;

  def sendToAll(self, msg):
    self.channel_lock.acquire();
    for session_id in self.sessions:
      sendMessage(session_id, msg);
    self.channel_lock.release();


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


def sendChannelChat(session_id, channel_chat):
  global active_channels;

  for active_channel in active_channels:
    info = active_channel.findUser(session_id);
    if info[0] == None:
      continue;

    channel_chat["nickname"] = info[1];
    active_channel.sendToAll(channel_chat);
    break;
