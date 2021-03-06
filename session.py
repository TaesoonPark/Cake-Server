import threading
import json

class Session():
  def __init__(cls, session_id, client_socket):
    cls.session_id = session_id;
    cls.client_socket = client_socket;
    cls.context = dict();
    cls.context_lock = threading.Lock();

  # 세션 컨텍스트에 데이터 저장
  def add_context(cls, key, value):
    cls.context_lock.acquire();
    cls.context[key] = value;
    cls.context_lock.release();

  # 세션 컨텍스트에서 데이터 가져오기
  def get_context(cls, key):
    cls.context_lock.acquire();
    result = (False, None);
    if key in cls.context:
      result = (True, cls.context[key]);

    cls.context_lock.release();
    return result;

  # 명시적 소켓 종료
  def close_socket(cls):
    cls.client_socket.close();

  # 이 세션에 메시지 보내기
  def send_message(cls, message):
    msg = json.dumps(message);
    print("session_id:", cls.session_id, "send message=", msg);
    bytes = msg.encode();
    msg_len = len(bytes);

    cls.client_socket.sendall(msg_len.to_bytes(4, byteorder="little"));
    cls.client_socket.sendall(bytes);
