"""
Author : ChungYi Fu (Kaohsiung, Taiwan)   2024/11/11 22:00
https://www.facebook.com/francefu

Python online
https://www.onlinegdb.com/
"""

def caesar_encrypt(text, shift):
    encrypted_text = ""
    for char in text:
        if char.isalpha():
            shift_base = ord('A') if char.isupper() else ord('a')
            encrypted_text += chr((ord(char) - shift_base + shift) % 26 + shift_base)
        else:
            encrypted_text += char
    return encrypted_text

def caesar_decrypt(text, shift):
    decrypted_text = ""
    for char in text:
        if char.isalpha():
            shift_base = ord('A') if char.isupper() else ord('a')
            decrypted_text += chr((ord(char) - shift_base - shift) % 26 + shift_base)
        else:
            decrypted_text += char
    return decrypted_text





# 測試範例
# Gemini Key 
GeminiKey = "12345678"
# Encrypt Shift
GeminiKeyShift = 3

# 加密
encrypted_text = caesar_encrypt(GeminiKey, GeminiKeyShift)
print(f"Encrypted text: {encrypted_text}")

# 解密
decrypted_text = caesar_decrypt(encrypted_text, GeminiKeyShift)
print(f"Decrypted text: {decrypted_text}")
