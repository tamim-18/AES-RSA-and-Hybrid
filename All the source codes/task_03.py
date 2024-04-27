import streamlit as st
import socket
import aes
import rsa
import base64
import random

KEY_SIZE = 16

def getRandomAesKey(size=16):
    key_chars = [chr(random.randint(48, 255)) for i in range(size)]
    return "".join(key_chars)

def encrypt(message, key):
    aes_key = key
    cipher_text = aes.encrypt(message, aes_key, KEY_SIZE)
    
    with open("Don't Open This/puk", "r") as file:
        puk = tuple(int (i) for i in file.readlines()[0].split())
        aes_key = rsa.encrypt(aes_key, puk)
    
    return cipher_text, aes_key

def storingMsgAndKey(enc_msg, enc_key):
    with open("Don't Open This/msg", "w") as file:
        file.write(base64.b64encode(enc_msg.encode('utf-8')).decode('utf-8'))
    with open("Don't Open This/key", "w") as file:
        file.write("#".join([str(n) for n in enc_key]))

def retrieve_enc_msg():
    enc_msg = ""
    with open("Don't Open This/msg", "r") as file:
        enc_msg = file.readlines()[0]
    return base64.b64decode(enc_msg.encode('utf-8')).decode('utf-8')

def decrypt(enc_msg):
    aes_key = []
    prk = ()
    with open("Don't Open This/prk", "r") as file:
        prk = tuple(int(i) for i in file.readlines()[0].split())
    with open("Don't Open This/key", "r") as file:
        aes_key = [int(i) for i in file.readlines()[0].split("#")]
        aes_key = rsa.decrypt(aes_key, prk)
    plain_text = aes.decrypt(enc_msg, aes_key, KEY_SIZE)
    return plain_text

def initServerAndClient(ip_addr, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((ip_addr, port))
    server.listen(0)
    client_socket, client_address = server.accept()
    return server, client_socket

def store_key():
    puk, prk = rsa.key_gen(96)
    puk_e, puk_n = puk
    prk_e, prk_n = prk
    with open("Don't Open This/puk", "w") as file:
        file.write(f"{puk_e} {puk_n}")
    with open("Don't Open This/prk", "w") as file:
        file.write(f"{prk_e} {prk_n}")

st.title("Hybrid Cryptosystem Simulation")

option = st.selectbox("Select Role", ("Alice", "Bob"))

if option == "Alice":
    message = st.text_area("Enter message (max 4096 characters):")
    if st.button("Send Message"):
        enc_msg, enc_key = encrypt(message, getRandomAesKey())
        storingMsgAndKey(enc_msg, enc_key)
        st.write("Message sent successfully!")
elif option == "Bob":
    store_key()
    server, client_socket = initServerAndClient("127.0.0.1", 4096)
    while True:
        req = client_socket.recv(4096).decode('utf-8')
        if req == "Sent":
            enc_msg = retrieve_enc_msg()
            msg = decrypt(enc_msg)
            st.write(f"Received Message: {msg}")
            client_socket.send("Success".encode('utf-8'))
            break
    client_socket.close()
    server.close()
