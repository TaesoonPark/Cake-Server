import threading

from custom_message import *
from worker_thread import IOWorkerManager
from game import *

# 게임룸 클래스
class GameRoom:
  def __init__(self, title, nickname):
    self.title = title;
    self.owner_nickname = nickname;
    self.sessions_lock = threading.Lock();
    self.sessions = dict();
    # 2인 게임이라 가정
    self.player_limit = 2;

    self.game_lock = threading.Lock();
    self.game = None;

  # 게임룸에 유저 추가
  def addUser(self, session_id, nickname):
    result = True;
    self.game_lock.acquire();
    if self.game is not None:
      result = False;
    self.game_lock.release();

    if not result:
      return result;

    self.sessions_lock.acquire();
    if len(self.sessions) >= self.player_limit:
      result = False;

    if session_id in self.sessions:
      result = False;

    if result:
      self.sessions[session_id] = nickname;

    self.sessions_lock.release();

    if result:
      self.notifyRoomStatus();
    return True;

  # 게임룸에서 유저 제거. 방장일 경우 임의로 방장 이관
  def removeUser(self, session_id):
    self.sessions_lock.acquire();
    if session_id in self.sessions:
      nickname = self.sessions[session_id];
      del self.sessions[session_id];

      if nickname == self.owner_nickname:
        for sid, nick in self.sessions.items():
          self.owner_nickname = nick;
          break;

    self.sessions_lock.release();
    self.notifyRoomStatus();

  # 현재 게임룸 상황 업데이트
  def notifyRoomStatus(self):
    msg = makeMessage(MSG_ROOM_STATUS);
    msg["session_list"].clear();
    self.sessions_lock.acquire();
    for session_id, nickname in self.sessions.items():
      entry = dict();
      entry["session_id"] = session_id;
      entry["nickname"] = nickname;
      msg["session_list"].append(entry);

    for session_id in self.sessions:
      IOWorkerManager().push_io_message(session_id, msg);
    self.sessions_lock.release();

  # 메시지를 방 인원 전체에게 전송
  def sendToAll(self, msg):
    self.sessions_lock.acquire();
    for session_id in self.sessions:
      IOWorkerManager().push_io_message(session_id, msg);
    self.sessions_lock.release();

  # gameRoomList에서 쓰기위한 요약 정보
  def getRoomSummary(self):
    return (self.title, self.owner_nickname, self.getSessionCount());

  # 게임룸에 진입시 유저가 확인할 정보
  def getRoomInfo(self):
    sessions = dict();
    self.sessions_lock.acquire();
    sessions = self.sessions;
    self.sessions_lock.release();
    return sessions;

  # 현재 세션 수
  def getSessionCount(self):
    self.sessions_lock.acquire();
    count = len(self.sessions);
    self.sessions_lock.release();
    return count;

  # 인게임 종료시 갈무리
  def gameFinished(self, result_data):
    self.game_lock.acquire();
    del self.game;
    self.game_lock.release();

  # 게임 시작
  def startGame(self, session_id):
    result = True;
    self.sessions_lock.acquire();
    if len(self.sessions) != self.player_limit:
      print("cannot start game not enough player");
      result = False;

    if self.sessions[session_id] != self.owner_nickname:
      print("cannot start game not owner");
      result = False;

    if result:
      self.game = Game(self.sessions, self.gameFinished);
      self.game.startGame();
    self.sessions_lock.release();

    return result;
