import threading
import socket
import json

from custom_message import *
from session_manager import *
from worker_thread import initWorkers, pushMessage, pushIOMessage
from message_handlers import initHandlers
from channel_handlers import initChannels, removeUserFromChannel


# 소켓이 연결되면 호출하는 콜백.
def socketHandler(client_socket, addr):
  port_no = addr[1];

  result = addSession(port_no, client_socket);
  if not result:
    return;

  res = makeMessage(MSG_CONNECTED);
  res["session_id"] = port_no;
  pushIOMessage(port_no, res);

  try:
    while True:
      data = client_socket.recv(4);
      
      if len(data) == 0:
        break;

      length = int.from_bytes(data, byteorder='little');
      data = client_socket.recv(length);
      msg = data.decode();

      print ("recv message= ", msg);

      pushMessage(msg);

  except Exception as e:
    print("socket except", e);

  finally:
    removeSession(addr[1]);
    removeUserFromChannel(addr[1]);


# 메인 함수
if __name__ == '__main__':
  initCustomMessage();
  initHandlers();
  initWorkers();
  initChannels();

  server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
  server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1);
  server_socket.bind(("", 9999));
  server_socket.listen();
  print("socket listen");

  try:
    while True:
      client_socket, addr = server_socket.accept();
      th = threading.Thread(target=socketHandler, args=(client_socket, addr));
      th.start();

  except:
    print("error");

  finally:
    server_socket.close();
