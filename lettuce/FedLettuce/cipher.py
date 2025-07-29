import random
import string
import json

class SimpleCipher:
    """For encrypting the raw data sent from client to server"""

    def __init__(self, seed=42):
        # Define character set (letters, numbers, spaces, common punctuation)
        self.chars = string.ascii_letters + string.digits + ' .,()-'

        # Create shuffled key using fixed seed for reproducibility
        random.seed(seed)
        self.key = list(self.chars)
        random.shuffle(self.key)

        # print(f"Original chars: {self.chars}")
        # print(f"Shuffled key:   {''.join(self.key)}")

    def encrypt(self, plain_text):
        """Encrypt a string using substitution cipher"""
        cipher_text = ''
        for letter in plain_text:
            if letter in self.chars:
                index = self.chars.index(letter)
                cipher_text += self.key[index]
            else:
                # Handle characters not in our set (just keep them as-is)
                cipher_text += letter
        return cipher_text

    def decrypt(self, cipher_text):
        """Decrypt a string using substitution cipher"""
        decrypt_text = ''
        for letter in cipher_text:
            if letter in self.key:
                index = self.key.index(letter)
                decrypt_text += self.chars[index]
            else:
                # Handle characters not in our set
                decrypt_text += letter
        return decrypt_text

    def encrypt_term_list(self, terms):
        """Encrypt a list of terms"""
        return [self.encrypt(term) for term in terms]

    def decrypt_term_list(self, encrypted_terms):
        """Decrypt a list of terms"""
        return [self.decrypt(term) for term in encrypted_terms]

if __name__ == "__main__":
    # Example usage
    cipher = SimpleCipher(seed=42)
    
    original_text = "Hello, World! 123"
    encrypted_text = cipher.encrypt(original_text)
    decrypted_text = cipher.decrypt(encrypted_text)
    
    print(f"Original: {original_text}")
    print(f"Encrypted: {encrypted_text}")
    print(f"Decrypted: {decrypted_text}")
    
    terms = ["term1", "term2", "term3"]
    encrypted_terms = cipher.encrypt_term_list(terms)
    decrypted_terms = cipher.decrypt_term_list(encrypted_terms)
    
    print(f"Terms: {terms}")
    print(f"Encrypted Terms: {encrypted_terms}")
    print(f"Decrypted Terms: {decrypted_terms}")