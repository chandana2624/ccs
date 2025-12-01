
import hashlib
import time
import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext


class Block:
    def __init__(self, index, previous_hash, timestamp, data, nonce=0):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = f"{self.index}{self.previous_hash}{self.timestamp}{self.data}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, difficulty):
        target = '0' * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
        return self.hash


class Blockchain:
    def __init__(self, difficulty=4):
        self.chain = [self.create_genesis_block()]
        self.difficulty = difficulty
        self.balances = {}

    def create_genesis_block(self):
        return Block(0, "0", time.time(), "Genesis Block")

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, new_block):
        new_block.previous_hash = self.get_latest_block().hash
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)


        sender = new_block.data["sender"]
        receiver = new_block.data["receiver"]
        amount = new_block.data["amount"]

        if sender != "SYSTEM":
            self.balances[sender] -= amount
        if receiver not in self.balances:
            self.balances[receiver] = 0
        self.balances[receiver] += amount

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            if current.hash != current.calculate_hash():
                return False
            if current.previous_hash != previous.hash:
                return False
        return True

    def create_user(self, username, initial_balance=0):
        if username not in self.balances:
            self.balances[username] = initial_balance
            return True
        return False

    def get_balance(self, username):
        return self.balances.get(username, 0)


class CryptoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Cryptocurrency Simulator")
        self.blockchain = Blockchain(difficulty=3)  # Adjust difficulty for faster mining

        # Buttons
        tk.Button(root, text="Create User", width=20, command=self.create_user).pack(pady=5)
        tk.Button(root, text="Send Transaction", width=20, command=self.send_transaction).pack(pady=5)
        tk.Button(root, text="Show Blockchain", width=20, command=self.show_blockchain).pack(pady=5)
        tk.Button(root, text="Show Balances", width=20, command=self.show_balances).pack(pady=5)
        tk.Button(root, text="Validate Blockchain", width=20, command=self.validate_blockchain).pack(pady=5)

        # Text area for output
        self.output_area = scrolledtext.ScrolledText(root, width=80, height=20)
        self.output_area.pack(pady=10)

    def create_user(self):
        username = simpledialog.askstring("Create User", "Enter username:")
        if not username:
            return
        balance = simpledialog.askfloat("Initial Balance", f"Enter initial balance for {username}:")
        if balance is None:
            balance = 0
        if self.blockchain.create_user(username, balance):
            messagebox.showinfo("Success", f"User '{username}' created with balance {balance}")
        else:
            messagebox.showwarning("Exists", f"User '{username}' already exists!")

    def send_transaction(self):
        sender = simpledialog.askstring("Transaction", "Enter sender name:")
        if not sender:
            return
        receiver = simpledialog.askstring("Transaction", "Enter receiver name:")
        if not receiver:
            return
        amount = simpledialog.askfloat("Transaction", "Enter amount to send:")
        if amount is None:
            return

        # Validation
        if sender not in self.blockchain.balances:
            messagebox.showerror("Error", f"Sender '{sender}' does not exist!")
            return
        if receiver not in self.blockchain.balances:
            messagebox.showerror("Error", f"Receiver '{receiver}' does not exist!")
            return
        if self.blockchain.get_balance(sender) < amount:
            messagebox.showerror("Error", f"Sender '{sender}' has insufficient balance!")
            return

        # Add transaction
        new_block = Block(
            index=len(self.blockchain.chain),
            previous_hash="",
            timestamp=time.time(),
            data={"sender": sender, "receiver": receiver, "amount": amount}
        )
        mined_hash = new_block.mine_block(self.blockchain.difficulty)
        self.blockchain.add_block(new_block)
        self.output_area.insert(tk.END, f"Transaction added! Block mined: {mined_hash}\n")

    def show_blockchain(self):
        self.output_area.insert(tk.END, "\n=== Blockchain ===\n")
        for block in self.blockchain.chain:
            self.output_area.insert(tk.END, f"Index: {block.index}\n")
            self.output_area.insert(tk.END, f"Data: {block.data}\n")
            self.output_area.insert(tk.END, f"Hash: {block.hash}\n")
            self.output_area.insert(tk.END, f"Previous Hash: {block.previous_hash}\n")
            self.output_area.insert(tk.END, f"Nonce: {block.nonce}\n")
            self.output_area.insert(tk.END, "-------------------------------\n")

    def show_balances(self):
        self.output_area.insert(tk.END, "\n=== User Balances ===\n")
        for user, balance in self.blockchain.balances.items():
            self.output_area.insert(tk.END, f"{user}: {balance}\n")

    def validate_blockchain(self):
        valid = self.blockchain.is_chain_valid()
        message = "Blockchain is valid!" if valid else "Blockchain has been tampered!"
        messagebox.showinfo("Validation", message)


if __name__ == "__main__":
    root = tk.Tk()
    app = CryptoGUI(root)
    root.mainloop()

