"""
Receipt Scanner - Simple & Perfect UI
Upload receipt images, extract text (OCR), organize
Works without extra installs (manual mode).
Optional: pip install pillow pytesseract
Optional OCR engine: Tesseract-OCR installed on system
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import json
import os
from datetime import datetime

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    Image = None
    ImageTk = None
    PIL_AVAILABLE = False

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    pytesseract = None
    TESSERACT_AVAILABLE = False

class ReceiptScanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Receipt Scanner")
        self.root.geometry("1100x700")
        self.root.configure(bg='white')
        self.root.resizable(True, True)
        self.root.minsize(900, 600)

        # Data
        self.receipts_file = "receipts.json"
        self.receipts = []
        self.current_receipt = None
        self.load_receipts()

        # Header
        header = tk.Frame(root, bg='#FF9800', height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="🧾 Receipt Scanner",
            font=('Arial', 24, 'bold'),
            bg='#FF9800',
            fg='white'
        ).pack(pady=18)

        # Main container
        main_container = tk.Frame(root, bg='white')






