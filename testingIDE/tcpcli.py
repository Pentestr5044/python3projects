import socket

target_host = input("please enter url: ")
target_port = int(input("please enter port number: "))

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((target_host,target_port))

client.send(b"GET / http:/1.1\r\nHost: google.com\r\n\r\n")
response = client.recv(4096)
print(response)