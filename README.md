# EGL Oblivious Transfer (1-out-of-2)

*Read this in other languages: [English](README.md), [Русский](README_RU.md).*

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-Tkinter-orange.svg?style=flat-square)](https://docs.python.org/3/library/tkinter.html)

## 📌 Project Overview
This repository contains a Python implementation of the **Even-Goldreich-Lempel (EGL)** protocol for 1-out-of-2 Oblivious Transfer based on the RSA cryptosystem. 


## ✨ Key Features
- **Interactive GUI**: Built with Tkinter, featuring a real-time protocol log.
- **Detailed Metrics**: 
  - **⏱️ Time Complexity**: Precise measurement for each protocol stage (Keygen, Blinding, Encryption).
  - **📊 Data Analysis**: Size tracking for every packet transmitted (in bytes).
- **Secure Implementation**:
  - 1024-bit RSA key generation.
  - Miller-Rabin primality test.
  - Secure random numbers via `secrets` module.


## 🛠️ Installation and Run

1. Make sure you have Python 3.8 or higher installed.
2. Clone the repository:
    ```bash
    git clone https://github.com/kekwX/egl-ot-rsa.git

3. Change to the project folder:
cd egl-ot-rsa
4. Run the application (no libraries needed, the standard Python distribution is used):
python egl.py

🧬 How it works (Protocol Steps)

1. Initialization (Alice): Generates an RSA key pair (n, e, d) and two random
values ​​x_0, x_1.
2. Blinding (Bob): Chooses a message b, generates a random secret k, and
sends Alice the value V = (x_b + k^e) \pmod n.
3. Double encryption (Alice): Alice computes two potential decryption keys k_0, k_1 (without knowing which one is correct for Bob) and
masks both of her messages: C_i = M_i + k_i \pmod n.
4. Receive (Bob): Bob receives C_0, C_1 and unmasks his message by
simply subtracting the secret k.

🖥️ Screenshots



The program displays a step-by-step log, highlighting Alice's actions in blue and Bob's in green. At the end of each operation, the exact size of the transferred data in bytes is indicated.

Developed for educational purposes


