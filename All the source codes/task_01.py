import streamlit as st
import util
import time
import base64
import aes

KEY_SIZE = 16

def main():
    st.title("AES Encryption/Decryption")

    st.subheader("Enter Key")
    key = st.text_input("Key (in ASCII):", placeholder="Enter your key")
    if key:
        hex_key = util.string_to_hex(aes.get_padded_key(key))
        st.write(f"Key (in HEX): {hex_key}")

    st.subheader("Enter Plain Text")
    plain_text = st.text_area("Plain Text (in ASCII):", placeholder="Enter your plain text")
    if plain_text:
        hex_plain_text = util.string_to_hex(plain_text)
        st.write(f"Plain Text (in HEX): {hex_plain_text}")

    if key and plain_text:
        st.subheader("Cipher Text")
        start_time = time.time()
        cipher_text = aes.encrypt(plain_text, key, KEY_SIZE)
        end_time = time.time()
        encryption_duration = end_time - start_time
        base64_cipher_text = base64.b64encode(cipher_text.encode('utf-8')).decode('utf-8')
        st.write(f"Cipher Text (in ASCII): {base64_cipher_text}")
        hex_cipher_text = util.string_to_hex(cipher_text)
        st.write(f"Cipher Text (in HEX): {hex_cipher_text}")

        st.subheader("Decipher Text")
        start_time = time.time()
        deciphered_text = aes.decrypt(cipher_text, key, KEY_SIZE)
        end_time = time.time()
        decryption_duration = end_time - start_time
        st.write(f"Decipher Text (in ASCII): {deciphered_text}")
        hex_deciphered_text = util.string_to_hex(deciphered_text)
        st.write(f"Decipher Text (in HEX): {hex_deciphered_text}")

        st.subheader("Execution Time")
        start_time = time.time()
        aes.get_round_keys(aes.get_padded_key(key))
        end_time = time.time()
        key_scheduling_duration = end_time - start_time
        st.write(f"Key Scheduling: {round(key_scheduling_duration, 20)} sec")
        st.write(f"Encryption Time: {round(encryption_duration, 20)} sec")
        st.write(f"Decryption Time: {round(decryption_duration, 20)} sec")

if __name__ == "__main__":
    main()