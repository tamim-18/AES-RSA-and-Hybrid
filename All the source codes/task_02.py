import streamlit as st
import rsa
import time

def generate_keys(bit_length):
    start_time = time.time()
    puk, prk = rsa.key_gen(bit_length)
    end_time = time.time()
    key_gen_duration = end_time - start_time
    return puk, prk, key_gen_duration

def encrypt_text(plain_text, public_key):
    start_time = time.time()
    encrypted_text = rsa.encrypt(plain_text, public_key)
    end_time = time.time()
    encryption_duration = end_time - start_time
    return encrypted_text, encryption_duration

def decrypt_text(encrypted_text, private_key):
    start_time = time.time()
    decrypted_text = rsa.decrypt(encrypted_text, private_key)
    end_time = time.time()
    decryption_duration = end_time - start_time
    return decrypted_text, decryption_duration

st.title("RSA Encryption and Decryption")

option = st.sidebar.selectbox("Select Operation", ["Generate Keys", "Encrypt Text", "Decrypt Text"])

if option == "Generate Keys":
    bit_length = st.sidebar.select_slider("Select Bit Length", options=[16, 32, 64, 96], value=64)
    key_gen_button = st.sidebar.button("Generate Keys")

    if key_gen_button:
        puk, prk, key_gen_duration = generate_keys(bit_length)
        st.session_state["public_key"] = puk
        st.session_state["private_key"] = prk
        st.write("Public Key: (e,n) = ", puk)
        st.write("Private Key: (d,n) = ", prk)
        st.write("")
        st.info(f"Key Generation Time: {key_gen_duration:.10f} sec")

elif option == "Encrypt Text":
    plain_text = st.text_area("Enter Plain Text")
    encrypt_button = st.button("Encrypt")

    if encrypt_button:
        if "public_key" in st.session_state:
            encrypted_text, encryption_duration = encrypt_text(plain_text, st.session_state["public_key"])
            st.write("Encrypted Text (ASCII): ", encrypted_text)
            st.info(f"Encryption Time: {encryption_duration:.10f} sec")
        else:
            st.error("Please generate keys first")

elif option == "Decrypt Text":
    encrypted_text = st.text_area("Enter Encrypted Text (ASCII)")
    decrypt_button = st.button("Decrypt")

    if decrypt_button:
        if "private_key" in st.session_state:
            encrypted_text_list = eval(encrypted_text)
            decrypted_text, decryption_duration = decrypt_text(encrypted_text_list, st.session_state["private_key"])
            st.write("Decrypted Text: ", decrypted_text)
            st.info(f"Decryption Time: {decryption_duration:.10f} sec")
        else:
            st.error("Please generate keys first")
