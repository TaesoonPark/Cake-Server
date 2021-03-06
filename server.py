import threading
import socket
import json

from custom_message import *
from message_handlers import init_handlers
from channel_handlers import init_channels, remove_user_from_channel

from session_manager import SessionManager
from worker_thread import WorkerManager, IOWorkerManager


# 소켓이 연결되면 호출하는 콜백.
def socket_handler(client_socket, addr):
  port_no = addr[1];

  result = SessionManager().add_session(port_no, client_socket);
  if not result:
    return;

  res = make_message(MSG_CONNECTED);
  res["session_id"] = port_no;
  IOWorkerManager().push_io_message(port_no, res);

  try:
    while True:
      data = client_socket.recv(4);
      
      if len(data) == 0:
        break;

      length = int.from_bytes(data, byteorder='little');
      data = client_socket.recv(length);
      msg = data.decode();

      print ("recv message= ", msg);

      WorkerManager().push_message(msg);

  except Exception as e:
    print("socket except", e);

  finally:
    SessionManager().remove_session(addr[1]);
    remove_user_from_channel(addr[1]);


# 메인 함수
if __name__ == '__main__':
  init_custom_message();
  init_handlers();
  init_channels();

  server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
  server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1);
  server_socket.bind(("", 9999));
  server_socket.listen();
  print("socket listen");

  try:
    while True:
      client_socket, addr = server_socket.accept();
      th = threading.Thread(target=socket_handler, args=(client_socket, addr));
      th.start();

  except:
    print("error");

  finally:
    server_socket.close();
