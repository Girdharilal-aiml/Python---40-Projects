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
        main_container.pack(fill=tk.BOTH, expand=True)

        # Left sidebar - Receipt list
        sidebar = tk.Frame(main_container, bg='#f5f5f5', width=250, relief=tk.SOLID, bd=1)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        # Sidebar header
        tk.Label(
            sidebar,
            text="Receipts",
            font=('Arial', 14, 'bold'),
            bg='#f5f5f5',
            fg='#333'
        ).pack(pady=15)

        # Search
        search_frame = tk.Frame(sidebar, bg='#f5f5f5')
        search_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', lambda *args: self.filter_receipts())

        tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=('Arial', 10),
            bg='white',
            fg='#333',
            relief=tk.SOLID,
            bd=1
        ).pack(fill=tk.X, ipady=5)

        # Receipt list
        list_frame = tk.Frame(sidebar, bg='#f5f5f5')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        scroll = tk.Scrollbar(list_frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.receipts_listbox = tk.Listbox(
            list_frame,
            font=('Arial', 10),
            bg='white',
            fg='#333',
            selectbackground='#FF9800',
            selectforeground='white',
            bd=1,
            relief=tk.SOLID,
            yscrollcommand=scroll.set
        )
        self.receipts_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.config(command=self.receipts_listbox.yview)
        self.receipts_listbox.bind('<<ListboxSelect>>', self.select_receipt)

        # Buttons
        tk.Button(
            sidebar,
            text="📷 Scan Receipt",
            command=self.scan_receipt,
            font=('Arial', 10, 'bold'),
            bg='#4CAF50',
            fg='white',
            bd=0,
            cursor='hand2',
            pady=8
        ).pack(fill=tk.X, padx=10, pady=2)

        tk.Button(
            sidebar,
            text="🗑️ Delete",
            command=self.delete_receipt,
            font=('Arial', 10, 'bold'),
            bg='#f44336',
            fg='white',
            bd=0,
            cursor='hand2',
            pady=8
        ).pack(fill=tk.X, padx=10, pady=2)

        # Center - Image preview
        center_frame = tk.Frame(main_container, bg='white')
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(
            center_frame,
            text="Receipt Image",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#333'
        ).pack(pady=(0, 10))

        # Image canvas
        self.image_canvas = tk.Canvas(
            center_frame,
            bg='#f5f5f5',
            relief=tk.SOLID,
            bd=1,
            highlightthickness=0
        )
        self.image_canvas.pack(fill=tk.BOTH, expand=True)

        # Right side - Details
        details_frame = tk.Frame(main_container, bg='#f5f5f5', width=350, relief=tk.SOLID, bd=1)
        details_frame.pack(side=tk.RIGHT, fill=tk.Y)
        details_frame.pack_propagate(False)

        tk.Label(
            details_frame,
            text="Receipt Details",
            font=('Arial', 12, 'bold'),
            bg='#f5f5f5',
            fg='#333'
        ).pack(pady=15)

        # Form fields
        form_container = tk.Frame(details_frame, bg='#f5f5f5')
        form_container.pack(fill=tk.BOTH, expand=True, padx=10)

        # Store
        tk.Label(
            form_container,
            text="Store:",
            font=('Arial', 10, 'bold'),
            bg='#f5f5f5',
            fg='#333',
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 2))

        self.store_entry = tk.Entry(
            form_container,
            font=('Arial', 10),
            bg='white',
            fg='#333',
            relief=tk.SOLID,
            bd=1
        )
        self.store_entry.pack(fill=tk.X, ipady=5, pady=(0, 10))

        # Date
        tk.Label(
            form_container,
            text="Date:",
            font=('Arial', 10, 'bold'),
            bg='#f5f5f5',
            fg='#333',
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 2))

        self.date_entry = tk.Entry(
            form_container,
            font=('Arial', 10),
            bg='white',
            fg='#333',
            relief=tk.SOLID,
            bd=1
        )
        self.date_entry.pack(fill=tk.X, ipady=5, pady=(0, 10))

        # Amount
        tk.Label(
            form_container,
            text="Total Amount:",
            font=('Arial', 10, 'bold'),
            bg='#f5f5f5',
            fg='#333',
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 2))

        self.amount_entry = tk.Entry(
            form_container,
            font=('Arial', 10),
            bg='white',
            fg='#333',
            relief=tk.SOLID,
            bd=1
        )
        self.amount_entry.pack(fill=tk.X, ipady=5, pady=(0, 10))

        # Category
        tk.Label(
            form_container,
            text="Category:",
            font=('Arial', 10, 'bold'),
            bg='#f5f5f5',
            fg='#333',
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 2))

        categories = ['Food', 'Shopping', 'Transport', 'Entertainment', 'Bills', 'Other']
        self.category_var = tk.StringVar(value='Other')
        
        category_menu = tk.OptionMenu(form_container, self.category_var, *categories)
        category_menu.config(
            font=('Arial', 10),
            bg='white',
            fg='#333',
            bd=1,
            relief=tk.SOLID,
            cursor='hand2'
        )
        category_menu.pack(fill=tk.X, pady=(0, 10))

        # Notes
        tk.Label(
            form_container,
            text="Notes:",
            font=('Arial', 10, 'bold'),
            bg='#f5f5f5',
            fg='#333',
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 2))

        self.notes_text = tk.Text(
            form_container,
            font=('Arial', 9),
            bg='white',
            fg='#333',
            relief=tk.SOLID,
            bd=1,
            height=4,
            wrap=tk.WORD
        )
        self.notes_text.pack(fill=tk.X, pady=(0, 10))

        # OCR Text
        tk.Label(
            form_container,
            text="Extracted Text:",
            font=('Arial', 10, 'bold'),
            bg='#f5f5f5',
            fg='#333',
            anchor='w'
        ).pack(fill=tk.X, pady=(10, 2))

        ocr_scroll = tk.Scrollbar(form_container)
        ocr_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.ocr_text = tk.Text(
            form_container,
            font=('Consolas', 8),
            bg='#f9f9f9',
            fg='#333',
            relief=tk.SOLID,
            bd=1,
            height=8,
            wrap=tk.WORD,
            yscrollcommand=ocr_scroll.set,
            state='disabled'
        )
        self.ocr_text.pack(fill=tk.BOTH, expand=True)
        ocr_scroll.config(command=self.ocr_text.yview)

        # Save button
        tk.Button(
            details_frame,
            text="💾 Save Receipt",
            command=self.save_receipt,
            font=('Arial', 11, 'bold'),
            bg='#4CAF50',
            fg='white',
            bd=0,
            cursor='hand2',
            padx=20,
            pady=10
        ).pack(pady=15)

        # Status bar
        self.status_label = tk.Label(
            root,
            text=f"{len(self.receipts)} receipts | Total: $0.00",
            font=('Arial', 9),
            bg='#f5f5f5',
            fg='#666',
            anchor='w'
        )
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM)

        # Display receipts
        self.display_receipts()
        self.update_stats()

        # Check for Tesseract
        if not TESSERACT_AVAILABLE:
            messagebox.showwarning(
                "Missing Library",
                "pytesseract is not installed.\n"
                "OCR features will be disabled.\n\n"
                "Optional install:\n"
                "pip install pytesseract\n\n"
                "Also install Tesseract-OCR from:\n"
                "https://github.com/tesseract-ocr/tesseract"
            )
        if not PIL_AVAILABLE:
            messagebox.showwarning(
                "Missing Library",
                "Pillow is not installed.\n"
                "Image preview will be disabled.\n\n"
                "Optional install:\n"
                "pip install pillow"
            )

    def _show_image_placeholder(self, text):
        self.image_canvas.delete('all')
        self.image_canvas.create_text(
            self.image_canvas.winfo_width() // 2,
            self.image_canvas.winfo_height() // 2,
            text=text,
            fill='#666',
            font=('Arial', 11),
            justify='center'
        )

    def load_receipts(self):
        if os.path.exists(self.receipts_file):


        
        
