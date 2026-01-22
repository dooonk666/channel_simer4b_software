import socket
import time


#  创建客户端
soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#  连接
#  soc.connect(('192.168.43.141', 8087))
soc.connect(('192.168.1.10', 7))
send_data = b'\xfd\xb1\x85\x40\x05\x00\x0e\x01\x00\x00\x03\xae\x86'

soc.send(send_data)

time.sleep(1)

recv_data=soc.recv(1024)
print(recv_data)



soc.close()
