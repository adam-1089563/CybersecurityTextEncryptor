import base64
import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def encrypt_text(plaintext: str, password: str) -> str:
    salt = os.urandom(16)
    key = derive_key(password, salt)
    f = Fernet(key)
    token = f.encrypt(plaintext.encode())
    # Voeg salt en ciphertext samen, salt is geen geheim en kan samen met de ciphertext worden opgeslagen/verzonden
    return base64.urlsafe_b64encode(salt).decode() + ":" + token.decode()

def decrypt_text(ciphertext_with_salt: str, password: str) -> str:
    salt_b64, token = ciphertext_with_salt.split(":", 1)
    salt = base64.urlsafe_b64decode(salt_b64)
    key = derive_key(password, salt)
    f = Fernet(key)
    return f.decrypt(token.encode()).decode()

class CryptoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Text Encryptor / Decryptor")
        self.root.geometry("700x650")
        self.root.minsize(600, 550)

        # Password frame
        pw_frame = ttk.Frame(root, padding=10)
        pw_frame.pack(fill="x")

        ttk.Label(pw_frame, text="Password:").pack(side="left")
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(pw_frame, textvariable=self.password_var, show="*", width=40)
        self.password_entry.pack(side="left", padx=8, fill="x", expand=True)

        self.show_pw_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            pw_frame, text="Show", variable=self.show_pw_var, command=self.toggle_password
        ).pack(side="left")

        # Notebook with two tabs
        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True, padx=10, pady=8)

        # Encrypt tab
        enc_frame = ttk.Frame(notebook, padding=10)
        notebook.add(enc_frame, text="Encrypt")
        self.build_encrypt_tab(enc_frame)

        # Decrypt tab
        dec_frame = ttk.Frame(notebook, padding=10)
        notebook.add(dec_frame, text="Decrypt")
        self.build_decrypt_tab(dec_frame)

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(root, textvariable=self.status_var, relief="sunken", anchor="w").pack(
            fill="x", side="bottom"
        )

    # ---------- Helpers ----------
    def toggle_password(self):
        self.password_entry.config(show="" if self.show_pw_var.get() else "*")

    def get_password(self) -> str:
        pw = self.password_var.get()
        if not pw:
            messagebox.showwarning("Missing password", "Please enter a password first.")
            return ""
        return pw

    def copy_to_clipboard(self, text: str):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.status_var.set("Copied to clipboard.")

    # ---------- Encrypt tab ----------
    def build_encrypt_tab(self, parent):
        ttk.Label(parent, text="Plaintext to encrypt:").pack(anchor="w")
        self.plaintext_box = scrolledtext.ScrolledText(parent, wrap="word", height=10)
        self.plaintext_box.pack(fill="both", expand=True, pady=4)

        btn_row = ttk.Frame(parent)
        btn_row.pack(fill="x", pady=4)
        ttk.Button(btn_row, text="Encrypt", command=self.do_encrypt).pack(side="left")
        ttk.Button(btn_row, text="Clear", command=self.clear_encrypt).pack(side="left", padx=6)

        ttk.Label(parent, text="Encrypted output (salt:ciphertext):").pack(anchor="w", pady=(8, 0))
        self.ciphertext_box = scrolledtext.ScrolledText(parent, wrap="word", height=10)
        self.ciphertext_box.pack(fill="both", expand=True, pady=4)

        btn_row2 = ttk.Frame(parent)
        btn_row2.pack(fill="x")
        ttk.Button(
            btn_row2, text="Copy encrypted",
            command=lambda: self.copy_from(self.ciphertext_box)
        ).pack(side="left")

    def do_encrypt(self):
        pw = self.get_password()
        if not pw:
            return
        plaintext = self.plaintext_box.get("1.0", "end-1c")
        if not plaintext:
            messagebox.showwarning("No text", "Please enter text to encrypt.")
            return
        try:
            result = encrypt_text(plaintext, pw)
        except Exception as e:
            messagebox.showerror("Encryption failed", str(e))
            return
        self.ciphertext_box.delete("1.0", "end")
        self.ciphertext_box.insert("1.0", result)
        self.status_var.set("Encryption successful.")

    def clear_encrypt(self):
        self.plaintext_box.delete("1.0", "end")
        self.ciphertext_box.delete("1.0", "end")
        self.status_var.set("Cleared.")

    # ---------- Decrypt tab ----------
    def build_decrypt_tab(self, parent):
        ttk.Label(parent, text="Encrypted text (salt:ciphertext):").pack(anchor="w")
        self.enc_input_box = scrolledtext.ScrolledText(parent, wrap="word", height=10)
        self.enc_input_box.pack(fill="both", expand=True, pady=4)

        btn_row = ttk.Frame(parent)
        btn_row.pack(fill="x", pady=4)
        ttk.Button(btn_row, text="Decrypt", command=self.do_decrypt).pack(side="left")
        ttk.Button(btn_row, text="Clear", command=self.clear_decrypt).pack(side="left", padx=6)

        ttk.Label(parent, text="Decrypted plaintext:").pack(anchor="w", pady=(8, 0))
        self.decrypted_box = scrolledtext.ScrolledText(parent, wrap="word", height=10)
        self.decrypted_box.pack(fill="both", expand=True, pady=4)

        btn_row2 = ttk.Frame(parent)
        btn_row2.pack(fill="x")
        ttk.Button(
            btn_row2, text="Copy decrypted",
            command=lambda: self.copy_from(self.decrypted_box)
        ).pack(side="left")

    def do_decrypt(self):
        pw = self.get_password()
        if not pw:
            return
        ciphertext = self.enc_input_box.get("1.0", "end-1c").strip()
        if not ciphertext:
            messagebox.showwarning("No text", "Please paste encrypted text first.")
            return
        try:
            result = decrypt_text(ciphertext, pw)
        except Exception:
            messagebox.showerror(
                "Decryption failed",
                "Could not decrypt. Check the password and encrypted text."
            )
            return
        self.decrypted_box.delete("1.0", "end")
        self.decrypted_box.insert("1.0", result)
        self.status_var.set("Decryption successful.")

    def clear_decrypt(self):
        self.enc_input_box.delete("1.0", "end")
        self.decrypted_box.delete("1.0", "end")
        self.status_var.set("Cleared.")

    # ---------- Misc ----------
    def copy_from(self, text_widget):
        text = text_widget.get("1.0", "end-1c")
        if text:
            self.copy_to_clipboard(text)


if __name__ == "__main__":
    root = tk.Tk()
    try:
        ttk.Style().theme_use("clam")
    except tk.TclError:
        pass
    CryptoApp(root)
    root.mainloop()