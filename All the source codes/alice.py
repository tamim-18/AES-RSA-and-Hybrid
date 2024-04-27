import socket
import random
import aes
import rsa
import base64

def getRandomAesKey(size=16):
    key_chars = [chr(random.randint(48, 255)) for i in range(size)]
    return "".join(key_chars)

def encrypt(message, key):
    aes_key = key
    cipher_text = aes.encrypt(message, aes_key, 16)
    
    with open("Don't Open This/puk", "r") as file:
        puk = tuple(int (i) for i in file.readlines()[0].split())
        # print(puk)
        aes_key = rsa.encrypt(aes_key, puk)
    
    return cipher_text, aes_key

def storingMsgAndKey(enc_msg, enc_key):
    with open("Don't Open This/msg", "w") as file:
        # file.write(enc_msg)
        file.write(base64.b64encode(enc_msg.encode('utf-8')).decode('utf-8'))
    ## desc: store the encrypted key
    with open("Don't Open This/key", "w") as file:
        file.write("#".join([str(n) for n in enc_key]))

    
# def decrypt(enc_msg):

if __name__ == "__main__":
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_ip = "127.0.0.1"
    server_port = 4096
    client.connect((server_ip, server_port))
    
    while True:
        message = input("Enter message (max 4096 characters):\n>> ")
        enc_msg, enc_key = encrypt(message, getRandomAesKey())
        storingMsgAndKey(enc_msg, enc_key)
        # print(enc_key)
        
        client.send("Sent".encode('utf-8')[:4096])
        response = client.recv(4096).decode('utf-8')

        if response == "Closed":
            break
     # close the connection   
    client.close()
    print("Connection closed!")