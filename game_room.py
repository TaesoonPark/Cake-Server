import threading

from custom_message import *
from worker_thread import WorkerManager, IOWorkerManager
from game import Game

# 게임룸 클래스
class GameRoom:
  def __init__(cls, title, nickname, channel_id):
    cls.title = title;
    cls.owner_nickname = nickname;
    cls.sessions_lock = threading.Lock();
    cls.sessions = dict();
    cls.timer = None;

    cls.game_lock = threading.Lock();
    cls.game = None;

    cls.game_config_lock = threading.Lock();
    cls.game_config = dict();
    cls.game_config["game_type"] = 0;
    # 2인 게임이라 가정
    cls.game_config["max_user"] = 2;
    cls.game_config["frame_rate"] = 4;
    cls.game_config["frame_interval"] = 1 / cls.game_config["frame_rate"];

    message = make_message(INTERNAL_PROCESS_GAME_UPDATE);
    message["channel_id"] = channel_id;
    message["game_title"] = title;
    cls.game_config["update_message"] = json.dumps(message).encode();



  # 게임룸에 유저 추가
  def add_user(cls, session_id, nickname):
    result = True;
    cls.game_lock.acquire();
    if cls.game is not None:
      result = False;
    cls.game_lock.release();

    if not result:
      return result;

    cls.sessions_lock.acquire();
    cls.game_config_lock.acquire();
    if len(cls.sessions) >= cls.game_config["max_user"]:
      result = False;

    if session_id in cls.sessions:
      result = False;

    if result:
      cls.sessions[session_id] = nickname;

    cls.game_config_lock.release();
    cls.sessions_lock.release();

    if result:
      cls.notify_room_status();
    return True;

  # 게임룸에서 유저 제거. 방장일 경우 임의로 방장 이관
  def remove_user(cls, session_id):
    cls.sessions_lock.acquire();
    if session_id in cls.sessions:
      nickname = cls.sessions[session_id];
      del cls.sessions[session_id];

      if nickname == cls.owner_nickname:
        for sid, nick in cls.sessions.items():
          cls.owner_nickname = nick;
          break;

    cls.sessions_lock.release();
    cls.notify_room_status();

  # 현재 게임룸 상황 업데이트
  def notify_room_status(cls):
    msg = make_message(MSG_ROOM_STATUS);
    msg["session_list"].clear();
    cls.sessions_lock.acquire();
    for session_id, nickname in cls.sessions.items():
      entry = dict();
      entry["session_id"] = session_id;
      entry["nickname"] = nickname;
      msg["session_list"].append(entry);

    for session_id in cls.sessions:
      IOWorkerManager().push_io_message(session_id, msg);
    cls.sessions_lock.release();

  # 메시지를 방 인원 전체에게 전송
  def send_to_all(cls, msg):
    cls.sessions_lock.acquire();
    for session_id in cls.sessions:
      IOWorkerManager().push_io_message(session_id, msg);
    cls.sessions_lock.release();

  # game_room_list에서 쓰기위한 요약 정보
  def get_room_summary(cls):
    return (cls.title, cls.owner_nickname, cls.get_session_count());

  # 게임룸에 진입시 유저가 확인할 정보
  def get_room_info(cls):
    sessions = dict();
    cls.sessions_lock.acquire();
    sessions = cls.sessions;
    cls.sessions_lock.release();
    return sessions;

  # 현재 세션 수
  def get_session_count(cls):
    cls.sessions_lock.acquire();
    count = len(cls.sessions);
    cls.sessions_lock.release();
    return count;

  # 인게임 종료시 갈무리
  def game_finished(cls, result_data):
    cls.game_lock.acquire();
    cls.game = None;
    cls.game_lock.release();

  # 게임 시작
  def start_game(cls, session_id):
    result = True;
    cls.sessions_lock.acquire();
    cls.game_config_lock.acquire();
    if len(cls.sessions) != cls.game_config["max_user"]:
      print("cannot start game not enough player");
      result = False;
    cls.game_config_lock.release();

    if cls.sessions[session_id] != cls.owner_nickname:
      print("cannot start game not owner");
      result = False;

    if result:
      cls.game_lock.acquire();
      cls.make_game();
      if cls.game is not None:
        cls.game.start_game();
        if cls.timer is not None:
          cls.timer.start();
      else:
        print("start_game() cannot find game object");
        result = False;
      cls.game_lock.release();

    cls.sessions_lock.release();

    return result;

  # 게임 클래스 팩토리
  def make_game(cls):
    cls.game_config_lock.acquire();
    game_type = cls.game_config["game_type"];
    if game_type == 0:
      cls.game = Game(cls.sessions, cls.game_finished);
    else:
      print("cannot create wrong game type", game_type);

    if cls.game_config["frame_interval"] != 0:
      cls.timer = threading.Timer(cls.game_config["frame_interval"], cls.push_update_message);

    cls.game_config_lock.release();

  # 게임 업데이트 메시지를 큐에 넣는다.
  def push_update_message(cls):
    cls.game_lock.acquire();
    if cls.game is not None:
      cls.game_config_lock.acquire();
      message = cls.game_config["update_message"];
      WorkerManager().push_message(message);
      cls.game_config_lock.release();
      cls.timer = threading.Timer(cls.game_config["frame_interval"], cls.push_update_message);
      cls.timer.start();
    else:
      print("cannot find game");
    cls.game_lock.release();

  # 게임 주기적 업데이트
  def process_game_update(cls):
    cls.game_lock.acquire();
    if cls.game is not None:
      cls.game.process_update();
    cls.game_lock.release();
