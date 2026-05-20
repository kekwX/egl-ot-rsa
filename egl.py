import tkinter as tk
from tkinter import ttk, messagebox
import time
import secrets
import sys

# Mathematical Functions

def is_prime(n, k=40):
    """Miller-Rabin primality test"""
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0: return False
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    for _ in range(k):
        a = secrets.randbelow(n - 4) + 2
        x = pow(a, d, n)
        if x == 1 or x == n - 1: continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1: break
        else: return False
    return True

def generate_prime(bits=512):
    """Generates a secure prime number"""
    while True:
        p = secrets.randbits(bits)
        if p % 2 != 0 and is_prime(p):
            return p

def get_size(obj):
    """Estimates data size in bytes"""
    if isinstance(obj, int):
        # Number of bytes required to represent the integer
        return (obj.bit_length() + 7) // 8
    if isinstance(obj, str):
        return len(obj.encode('utf-8'))
    return sys.getsizeof(obj)

class EGLProtocolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EGL 1-out-of-2 Oblivious Transfer")
        self.root.geometry("950x880")
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Input Fields
        ttk.Label(main_frame, text="Alice's Messages (Input Data)", font=("Arial", 10, "bold")).pack(anchor="w")
        self.m0_entry = ttk.Entry(main_frame, width=80)
        self.m0_entry.insert(0, "Message 1 (Secret Index 0)")
        self.m0_entry.pack(pady=2)
        self.m1_entry = ttk.Entry(main_frame, width=80)
        self.m1_entry.insert(0, "Message 2 (Secret Index 1)")
        self.m1_entry.pack(pady=2)

        # Bob's Choice
        choice_frame = ttk.Frame(main_frame)
        choice_frame.pack(fill=tk.X, pady=10)
        ttk.Label(choice_frame, text="Bob selects bit b:").pack(side=tk.LEFT)
        self.choice_var = tk.IntVar(value=0)
        ttk.Radiobutton(choice_frame, text="0", variable=self.choice_var, value=0).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(choice_frame, text="1", variable=self.choice_var, value=1).pack(side=tk.LEFT)

        ttk.Button(main_frame, text="EXECUTE PROTOCOL", command=self.run_protocol).pack(pady=10)

        # Log Window
        self.log_text = tk.Text(main_frame, height=28, state=tk.DISABLED, font=("Consolas", 9), bg="#fdfdfd")
        self.log_text.pack(pady=5, fill=tk.BOTH, expand=True)

        # Footer Metrics
        self.status_label = ttk.Label(main_frame, text="Ready", font=("Arial", 9, "italic"))
        self.status_label.pack(side=tk.LEFT)

    def log(self, sender, msg, size=None):
        self.log_text.config(state=tk.NORMAL)
        prefix = f"[{sender}] "
        self.log_text.insert(tk.END, prefix, sender)
        
        main_msg = f"{msg}"
        self.log_text.insert(tk.END, main_msg)
        
        if size is not None:
            size_msg = f" | Size: {size} bytes\n"
            self.log_text.insert(tk.END, size_msg, "size")
        else:
            self.log_text.insert(tk.END, "\n")
            
        # Tags for styling
        self.log_text.tag_config("Alice", foreground="#0056b3", font=("Consolas", 9, "bold"))
        self.log_text.tag_config("Bob", foreground="#28a745", font=("Consolas", 9, "bold"))
        self.log_text.tag_config("System", foreground="#6c757d", font=("Consolas", 9, "italic"))
        self.log_text.tag_config("size", foreground="#dc3545", font=("Consolas", 9, "bold"))
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def run_protocol(self):
        try:
            self.log_text.config(state=tk.NORMAL)
            self.log_text.delete(1.0, tk.END)
            self.log_text.config(state=tk.DISABLED)
            
            total_start = time.perf_counter()

            # INPUT DATA
            txt0 = self.m0_entry.get()
            txt1 = self.m1_entry.get()
            self.log("System", f"Input M0: '{txt0}'", get_size(txt0))
            self.log("System", f"Input M1: '{txt1}'", get_size(txt1))
            
            m0 = int.from_bytes(txt0.encode(), 'big')
            m1 = int.from_bytes(txt1.encode(), 'big')
            b = self.choice_var.get()

            #KEY GENERATION (ALICE)
            t_s = time.perf_counter()
            p, q = generate_prime(512), generate_prime(512)
            n, e = p * q, 65537
            d = pow(e, -1, (p-1)*(q-1))
            t_keygen = (time.perf_counter() - t_s) * 1000
            self.log("Alice", f"RSA-1024 generation completed in {t_keygen:.2f} ms")

            # PARAMETER TRANSFER (ALICE -> BOB)
            x0, x1 = secrets.randbelow(n), secrets.randbelow(n)
            # Packet size: n + e + x0 + x1
            pkg1_size = get_size(n) + get_size(e) + get_size(x0) + get_size(x1)
            self.log("Alice", "PACKET 1: Sending (n, e, x0, x1) to Bob", pkg1_size)

            #BLINDING (BOB)
            t_s = time.perf_counter()
            k = secrets.randbelow(n)
            xb = x0 if b == 0 else x1
            v = (xb + pow(k, e, n)) % n
            t_bob = (time.perf_counter() - t_s) * 1000
            
            pkg2_size = get_size(v)
            self.log("Bob", f"Selected index M{b}. Processed in {t_bob:.2f} ms")
            self.log("Bob", "PACKET 2: Sending blinded V to Alice", pkg2_size)

            # ENCRYPTION (ALICE)
            t_s = time.perf_counter()
            # Alice recovers two potential keys
            k0_p = pow((v - x0) % n, d, n)
            k1_p = pow((v - x1) % n, d, n)
            # Mask messages (C = M + K)
            c0, c1 = (m0 + k0_p) % n, (m1 + k1_p) % n
            t_alice_enc = (time.perf_counter() - t_s) * 1000
            
            pkg3_size = get_size(c0) + get_size(c1)
            self.log("Alice", f"Encryption completed in {t_alice_enc:.2f} ms")
            self.log("Alice", "PACKET 3: Sending (C0, C1) to Bob", pkg3_size)

            # DECRYPTION (BOB)
            cb = c0 if b == 0 else c1
            # Bob removes his secret k
            res_int = (cb - k) % n
            res_txt = res_int.to_bytes((res_int.bit_length() + 7) // 8, 'big').decode(errors='ignore')
            
            self.log("Bob", "Message decrypted successfully")
            self.log("System", f"OUTPUT: '{res_txt}'", get_size(res_txt))

            total_time = (time.perf_counter() - total_start) * 1000
            total_traffic = pkg1_size + pkg2_size + pkg3_size
            
            self.log("System", f"TOTAL: Time {total_time:.2f} ms | Total Traffic {total_traffic} bytes")
            self.status_label.config(text=f"Success: {total_traffic} bytes transferred in {total_time:.2f} ms")

        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = EGLProtocolApp(root)
    root.mainloop()