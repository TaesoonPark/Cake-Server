import threading

class Room:
  def __init__(self, title, nickname):
    self.title = title;
    self.owner_nickname = nickname;
    self.sessions_lock = threading.Lock();
    self.sessions = dict();
    self.session_count = 0;


  def addUser(self, session_id, nickname):
    self.sessions_lock.acquire();
    if session_id in self.sessions:
      self.sessions_lock.release();
      return False;

    self.sessions[session_id] = nickname;
    self.session_count += 1;
    self.sessions_lock.release();
    return True;


  def removeUser(self, session_id):
    self.sessions_lock.acquire();
    if session_id in self.sessions:
      nickname = self.sessions[session_id];
      del self.sessions[session_id];
      self.session_count -= 1;

      if nickname == self.owner_nickname:
        for sid, nick in self.sessions.items():
          self.owner_nickname = nick;
          break;

    self.sessions_lock.release();


  def getRoomSummary(self):
    return (self.title, self.owner_nickname, self.session_count);


  def getRoomInfo(self):
    sessions = dict();
    self.sessions_lock.acquire();
    sessions = self.sessions;
    self.sessions_lock.release();
    return sessions;
