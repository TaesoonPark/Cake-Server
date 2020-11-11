import threading

# 게임룸 클래스
class Room:
  def __init__(self, title, nickname):
    self.title = title;
    self.owner_nickname = nickname;
    self.sessions_lock = threading.Lock();
    self.sessions = dict();
    self.session_count = 0;

  # 게임룸에 유저 추가
  def addUser(self, session_id, nickname):
    self.sessions_lock.acquire();
    if session_id in self.sessions:
      self.sessions_lock.release();
      return False;

    self.sessions[session_id] = nickname;
    self.session_count += 1;
    self.sessions_lock.release();
    return True;

  # 게임룸에서 유저 제거. 방장일 경우 임의로 방장 이관
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

  # gameRoomList에서 쓰기위한 요약 정보
  def getRoomSummary(self):
    return (self.title, self.owner_nickname, self.session_count);

  # 룸에 진입시 유저가 확인할 정보
  def getRoomInfo(self):
    sessions = dict();
    self.sessions_lock.acquire();
    sessions = self.sessions;
    self.sessions_lock.release();
    return sessions;
