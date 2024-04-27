import socket
import aes
import rsa
import base64

# desc: Initialize server and client sockets
def initServerAndClient(ip_addr, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((ip_addr, port))
    server.listen(0)    
    print(f"Listening to {ip_addr}:{port}...")
    client_socket, client_address = server.accept()
    print(f"Client address : {client_address}...")
    
    return server, client_socket
# this fubction is used to store the key
def store_key():
    puk, prk = rsa.key_gen(96)    
    puk_e, puk_n = puk
    prk_e, prk_n = prk

    with open("Don't Open This/puk", "w") as file:
        file.write(f"{puk_e} {puk_n}")

    with open("Don't Open This/prk", "w") as file:
        file.write(f"{prk_e} {prk_n}")
# this function is used to retrieve the encrypted message        
def retrieve_enc_msg():
    enc_msg = ""
    
    with open("Don't Open This/msg", "r") as file:
        enc_msg = file.readlines()[0]
        
    # return enc_msg
    return base64.b64decode(enc_msg.encode('utf-8')).decode('utf-8')

# this function is used to decrypt the message
def decrypt(enc_msg):
    aes_key = []
    prk = ()
    
    with open("Don't Open This/prk", "r") as file:
        prk = tuple(int(i) for i in file.readlines()[0].split())
    
    with open("Don't Open This/key", "r") as file:
        aes_key = [int(i) for i in file.readlines()[0].split("#")]
        # print(aes_key)
        aes_key = rsa.decrypt(aes_key, prk)
        
    plain_text = aes.decrypt(enc_msg, aes_key, 16)
    return plain_text

if __name__ == "__main__":
    # desc: Initialize the server and client
    ip_addr = "127.0.0.1"
    port = 4096

    store_key()
    server, client_socket = initServerAndClient(ip_addr, port)
    
    while True:
        req = client_socket.recv(4096).decode('utf-8')
        
        if req == "Sent":
            enc_msg = retrieve_enc_msg()
            msg = decrypt(enc_msg)
            
            if msg == "close()":
                client_socket.send("Closed".encode('utf-8'))
                break
            
            print(f"Message : {msg}")
            client_socket.send("Success".encode('utf-8'))
    # desc: Close the connection
    client_socket.close()
    print("Connection closed!")
    server.close()