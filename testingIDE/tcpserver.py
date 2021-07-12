import socket
import threading

bind_ip = "0.0.0.0"
bind_port = 4444

# set your socket tool
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# set server binder
server.bind((bind_ip,bind_port))
# set listener
server.listen(5)
# print out the listening port
print("[*] Listening on %s:%d" % (bind_ip,bind_port))
# this is our client handling thread
def handle_client(client_socket):
    request = client_socket.recv(1024)
    # print out the recieved request
    print("[*] Recieved: %s" % request)
    # send back a packet
    client_socket.send(b'ACK!')
    client_socket.close()
while True:
    client,addr = server.accept()
    print("[*] Accepted connection from: %s:%d" % (addr[0],addr[1]))
    
    # spin up our client thread to handle incoming data
    client_handler = threading.Thread(target=handle_client,args=(client,))
    client_handler.start()
    