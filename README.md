With the rapid growth of digital communication and cloud storage, securing sensitive data has become essential. Traditional symmetric encryption (e.g., AES) provides efficient and fast encryption for large files but requires a secure way of exchanging the secret key. On the other hand, asymmetric encryption (e.g., RSA) offers secure key distribution but is computationally expensive for encrypting large data.

A hybrid cryptosystem combines the strengths of both approaches:

AES (Advanced Encryption Standard): Used to encrypt the actual file data quickly.

RSA (Rivest–Shamir–Adleman): Used to encrypt (wrap) the AES session key securely.

Modes of AES (GCM, CBC, CTR): Provide different trade-offs in terms of confidentiality, integrity, and performance.

AES-GCM: Provides authenticated encryption with integrity checking.

AES-CBC: A classic block cipher mode that requires padding.

AES-CTR: A stream cipher mode, efficient for parallelization.

This project demonstrates a secure file transfer system using Hybrid AES + RSA encryption and evaluates performance using different parameters.

Key highlights:

RSA key generation (2048, 3072 bits).

AES encryption in GCM, CBC, and CTR modes.

Hybrid encryption package stored in JSON format (includes encrypted AES key, nonce, ciphertext, tag).

File decryption using RSA private key.

Benchmarking for encryption/decryption speed and ciphertext size.
