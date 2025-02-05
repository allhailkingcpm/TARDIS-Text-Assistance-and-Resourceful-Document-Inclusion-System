import customtkinter as ctk
import re
from math_parser import MathParser
from tkinter import filedialog
import json
import os
from datetime import datetime
import threading
import time
from PIL import Image, ImageTk
import os.path
from typing import Dict, Optional
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import datetime

class TabManager:
    def __init__(self, parent_frame, colors):
        self.parent = parent_frame
        self.colors = colors  # Store colors locally
        self.tabs_frame = ctk.CTkFrame(parent_frame)
        self.tabs_frame.pack(fill="x", padx=5, pady=(5,0))
        
        self.content_frame = ctk.CTkFrame(parent_frame)
        self.content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.tabs: Dict[str, Dict] = {}
        self.active_tab: Optional[str] = None
        
        # Add new tab button with local colors
        self.add_tab_btn = ctk.CTkButton(
            self.tabs_frame,
            text="+",
            width=30,
            fg_color=self.colors["light_blue"],
            hover_color=self.colors["tardis_blue"],
            command=self.create_new_tab
        )
        self.add_tab_btn.pack(side="left", padx=2, pady=2)

    def create_new_tab(self, title="Untitled", content=None):
        tab_id = f"tab_{len(self.tabs)}"
        
        # Create tab button
        tab_frame = ctk.CTkFrame(self.tabs_frame)
        tab_frame.pack(side="left", padx=2, pady=2)
        
        tab_button = ctk.CTkButton(
            tab_frame,
            text=title,
            fg_color=self.colors["light_blue"],
            hover_color=self.colors["tardis_blue"],
            command=lambda: self.switch_tab(tab_id)
        )
        tab_button.pack(side="left", padx=1)
        
        close_button = ctk.CTkButton(
            tab_frame,
            text="×",
            width=20,
            command=lambda: self.close_tab(tab_id)
        )
        close_button.pack(side="left", padx=1)
        
        # Create content
        content_frame = ctk.CTkFrame(self.content_frame)
        
        # Save tab info
        self.tabs[tab_id] = {
            'frame': tab_frame,
            'content': content_frame,
            'title': title,
            'file_path': None,
            'input_text': None,
            'output_text': None,
            'modified': False
        }
        
        self.setup_tab_content(tab_id)
        self.switch_tab(tab_id)
        return tab_id

    def setup_tab_content(self, tab_id):
        content_frame = self.tabs[tab_id]['content']
        
        # Configure grid
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        
        # Input panel
        input_panel = ctk.CTkFrame(content_frame)
        input_panel.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        input_label = ctk.CTkLabel(input_panel, text="Input Expression", font=("Arial", 16, "bold"))
        input_label.pack(pady=5)
        
        input_text = ctk.CTkTextbox(
            input_panel,
            width=500,
            height=600,
            font=("Arial", 14)
        )
        input_text.pack(padx=10, pady=5, fill="both", expand=True)
        
        # Output panel
        output_panel = ctk.CTkFrame(content_frame)
        output_panel.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        output_label = ctk.CTkLabel(output_panel, text="Rendered Output", font=("Arial", 16, "bold"))
        output_label.pack(pady=5)
        
        output_text = ctk.CTkTextbox(
            output_panel,
            width=500,
            height=600,
            font=("Arial", 14)
        )
        output_text.pack(padx=10, pady=5, fill="both", expand=True)
        output_text.configure(state="disabled")
        
        # Store text widgets
        self.tabs[tab_id]['input_text'] = input_text
        self.tabs[tab_id]['output_text'] = output_text
        
        # Bind input changes
        input_text.bind('<KeyRelease>', lambda e: self.on_tab_input_change(tab_id))

    def switch_tab(self, tab_id):
        if self.active_tab:
            self.tabs[self.active_tab]['content'].pack_forget()
            self.tabs[self.active_tab]['frame'].configure(fg_color="transparent")
        
        self.tabs[tab_id]['content'].pack(fill="both", expand=True)
        self.tabs[tab_id]['frame'].configure(fg_color=self.parent.cget("fg_color"))
        self.active_tab = tab_id

    def close_tab(self, tab_id):
        if self.tabs[tab_id]['modified']:
            # Prompt for save
            pass
        
        self.tabs[tab_id]['frame'].destroy()
        self.tabs[tab_id]['content'].destroy()
        
        if self.active_tab == tab_id:
            remaining_tabs = [t for t in self.tabs if t != tab_id]
            if remaining_tabs:
                self.switch_tab(remaining_tabs[0])
        
        del self.tabs[tab_id]

class MathTranslatorApp:
    def __init__(self):
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.window = ctk.CTk()
        self.window.title("TARDIS Math Translator")
        self.window.geometry("1200x800")
        
        # TARDIS colors
        self.colors = {
            "tardis_blue": "#003B6F",     # Dark TARDIS blue
            "light_blue": "#1E517B",      # Light TARDIS blue
            "police_white": "#FFFFFF",     # Police box text color
            "warning_yellow": "#FFD700",   # Warning sign color
            "interior_gold": "#B8860B",    # TARDIS interior accent
            "time_vortex": "#0F2149",     # Darker background color
            "error": "#FF4444"
        }
        
        # Configure window background
        self.window.configure(fg_color=self.colors["time_vortex"])
        
        # Save related variables
        self.current_file = None
        self.last_save_time = None
        self.auto_save_interval = 300  # 5 minutes in seconds
        self.aligned_mode = False  # Track if equations are aligned
        
        # Create main layout
        self.create_toolbar()
        self.create_main_content()
        self.create_status_bar()
        
        # Initialize notification system
        self.notification_timer = None
        
        self.parser = MathParser()
        
        # Start auto-save thread
        self.auto_save_thread = threading.Thread(target=self.auto_save_loop, daemon=True)
        self.auto_save_thread.start()

        # Register a Unicode font for math symbols
        pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))

    def create_toolbar(self):
        # Create TARDIS-style header
        header_frame = ctk.CTkFrame(
            self.window,
            fg_color=self.colors["tardis_blue"],
            corner_radius=0
        )
        header_frame.grid(row=0, column=0, columnspan=3, sticky="ew")
        
        # POLICE BOX text
        police_text = ctk.CTkLabel(
            header_frame,
            text="POLICE     BOX",
            font=("Arial Black", 24, "bold"),
            text_color=self.colors["police_white"]
        )
        police_text.pack(pady=10)
        
        # Toolbar below header
        toolbar = ctk.CTkFrame(self.window, height=40, fg_color=self.colors["light_blue"])
        toolbar.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=(0,10))
        
        # ...existing toolbar buttons with updated styling...
        self.create_tardis_button(toolbar, "🌓", "Toggle Theme", self.toggle_theme)
        ctk.CTkFrame(toolbar, width=2, height=25, fg_color=self.colors["police_white"]).pack(side="left", padx=10, pady=5)
        self.create_tardis_button(toolbar, "📁", "New File", self.new_file)
        self.create_tardis_button(toolbar, "💾", "Save", self.save_file)
        self.create_tardis_button(toolbar, "📂", "Load", self.load_file)
        ctk.CTkFrame(toolbar, width=2, height=25, fg_color=self.colors["police_white"]).pack(side="left", padx=10, pady=5)
        self.create_tardis_button(toolbar, "📄", "Export PDF", self.export_pdf)
        self.create_tardis_button(toolbar, "⇌", "Align Equations", self.toggle_alignment)
        self.create_tardis_button(toolbar, "❔", "Help", self.show_help)
        self.create_tardis_button(toolbar, "📄", "New Tab", self.new_tab)

    def create_tardis_button(self, parent, icon, tooltip, command):
        btn = ctk.CTkButton(
            parent,
            text=icon,
            width=40,
            fg_color=self.colors["tardis_blue"],
            hover_color=self.colors["light_blue"],
            command=command
        )
        btn.pack(side="left", padx=2)
        self.create_tooltip(btn, tooltip)

    def create_main_content(self):
        # TARDIS interior styling for main content
        self.main_content = ctk.CTkFrame(
            self.window,
            fg_color=self.colors["time_vortex"],
            corner_radius=15
        )
        self.main_content.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)
        
        # Add TARDIS-style border
        border_frame = ctk.CTkFrame(
            self.main_content,
            fg_color=self.colors["tardis_blue"],
            corner_radius=15
        )
        border_frame.pack(padx=2, pady=2, fill="both", expand=True)
        
        # Pass colors to TabManager
        self.tab_manager = TabManager(border_frame, self.colors)
        self.tab_manager.create_new_tab()

    def create_status_bar(self):
        # TARDIS-style status bar
        self.status_bar = ctk.CTkLabel(
            self.window,
            text="Ready for time travel...",
            height=25,
            anchor="w",
            font=("Arial", 12),
            fg_color=self.colors["tardis_blue"],
            text_color=self.colors["police_white"]
        )
        self.status_bar.grid(row=3, column=0, columnspan=3, sticky="ew", padx=10, pady=(0,10))

    def create_toolbar_button(self, parent, icon, tooltip, command):
        btn = ctk.CTkButton(
            parent,
            text=icon,
            width=40,
            command=command
        )
        btn.pack(side="left", padx=2)
        self.create_tooltip(btn, tooltip)

    def create_tooltip(self, widget, text):
        def show_tooltip(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 20
            
            self.tooltip = ctk.CTkToplevel(widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            
            label = ctk.CTkLabel(self.tooltip, text=text, bg_color=self.colors["secondary"])
            label.pack()
            
        def hide_tooltip(event):
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()
        
        widget.bind('<Enter>', show_tooltip)
        widget.bind('<Leave>', hide_tooltip)

    def toggle_theme(self):
        new_mode = "light" if ctk.get_appearance_mode() == "dark" else "dark"
        ctk.set_appearance_mode(new_mode)
        self.show_notification(f"Switched to {new_mode} mode")

    def show_notification(self, message, duration=3000):
        self.status_bar.configure(text=message)
        
        if self.notification_timer:
            self.window.after_cancel(self.notification_timer)
        
        self.notification_timer = self.window.after(duration, lambda: self.status_bar.configure(text="Ready"))

    def new_file(self):
        if self.current_file:
            # Add save prompt logic here
            pass
        self.current_file = None
        self.input_text.delete("1.0", "end")
        self.window.title("Math Expression Translator - New File")
        self.show_notification("Created new file")

    def new_tab(self):
        self.tab_manager.create_new_tab()

    def save_file(self):
        if not self.active_tab:
            return
            
        tab = self.tab_manager.tabs[self.active_tab]
        if not tab['file_path']:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".math",
                filetypes=[("Math files", "*.math"), ("All files", "*.*")]
            )
            if not file_path:
                return
            tab['file_path'] = file_path
        
        data = {
            'input_text': tab['input_text'].get("1.0", "end-1c"),
            'timestamp': datetime.now().isoformat()
        }
        
        with open(tab['file_path'], 'w') as f:
            json.dump(data, f)
        
        tab['modified'] = False
        self.window.title(f"Math Expression Translator - {os.path.basename(tab['file_path'])}")
        self.show_notification("File saved successfully")

    def load_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Math files", "*.math"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                tab_id = self.tab_manager.create_new_tab(
                    title=os.path.basename(file_path)
                )
                tab = self.tab_manager.tabs[tab_id]
                tab['file_path'] = file_path
                tab['input_text'].delete("1.0", "end")
                tab['input_text'].insert("1.0", data['input_text'])
                self.show_notification("File loaded successfully")
            except Exception as e:
                self.show_error(f"Error loading file: {str(e)}")

    def auto_save_loop(self):
        while True:
            time.sleep(10)  # Check every 10 seconds
            if (self.current_file and self.last_save_time and 
                time.time() - self.last_save_time >= self.auto_save_interval):
                self.window.after(0, self.save_file)

    def show_error(self, message):
        error_window = ctk.CTkToplevel(self.window)
        error_window.title("Error")
        error_window.geometry("300x100")
        
        label = ctk.CTkLabel(error_window, text=message)
        label.pack(padx=20, pady=20)
        
        ok_button = ctk.CTkButton(error_window, text="OK", command=error_window.destroy)
        ok_button.pack(pady=10)

    def on_input_change(self, event=None):
        input_text = self.input_text.get("1.0", "end-1c")
        translated_text = self.parser.translate(input_text)
        
        if self.aligned_mode:
            translated_text = self.align_equations(translated_text)
        
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", translated_text)
        self.output_text.configure(state="disabled")

    def toggle_alignment(self):
        self.aligned_mode = not self.aligned_mode
        self.on_input_change()  # Refresh the output

    def align_equations(self, text):
        lines = text.split('\n')
        max_left_width = 0
        
        # First pass: find the maximum width before '='
        for line in lines:
            if '=' in line:
                left_side = line.split('=')[0]
                max_left_width = max(max_left_width, len(left_side.rstrip()))
        
        # Second pass: align the equations
        aligned_lines = []
        for line in lines:
            if '=' in line:
                left_side, right_side = line.split('=', 1)
                padding = ' ' * (max_left_width - len(left_side.rstrip()))
                aligned_lines.append(f"{left_side.rstrip()}{padding} = {right_side.lstrip()}")
            else:
                aligned_lines.append(line)
        
        return '\n'.join(aligned_lines)  # Fixed the string join syntax

    def show_help(self):
        help_window = ctk.CTkToplevel(self.window)
        help_window.title("Help")
        help_window.geometry("600x800")
        
        help_text = """
        How to write mathematical expressions:
        
        Basic Operations:
        1. Square root: sqrt(x)      → √x
        2. Nth root: root(n,x)      → ∛x (cube root example)
        3. Fractions: 
           - Simple: 1/2            → ½
           - Complex: (1+x)/(2+y)   → Displays as:
             1+x
             ───
             2+y
           - Mixed: (x+1)/2 or 2/(x+1)
        
        Greek Letters:
        - Lowercase: @alpha → α, @beta → β, etc.
        - Uppercase: @ALPHA → Α, @GAMMA → Γ, etc.
        
        Operators:
        - times → ×    - div → ÷
        - +-    → ±    - -+  → ∓
        - <=    → ≤    - >=  → ≥
        - !=    → ≠    - ~=  → ≈
        
        Set Theory:
        - in      → ∈    - notin   → ∉
        - subset  → ⊂    - supset  → ⊃
        - union   → ∪    - inter   → ∩
        - empty   → ∅
        
        Calculus:
        - partial   → ∂    - nabla    → ∇
        - integral  → ∫    - oint     → ∮
        - iintegral → ∬    - iiintegral → ∭
        
        Geometry:
        - angle    → ∠    - perp     → ⊥
        - parallel → ∥    - triangle → △
        - degree   → °
        
        Logic:
        - and     → ∧    - or      → ∨
        - not     → ¬    - implies → ⇒
        - iff     → ⇔    - xor     → ⊕
        
        Equation Alignment:
        Click 'Align =' to align equations at equals signs.
        """
        
        help_text_widget = ctk.CTkTextbox(help_window, width=550, height=750)
        help_text_widget.pack(padx=20, pady=20)
        help_text_widget.insert("1.0", help_text)
        help_text_widget.configure(state="disabled")

    def export_pdf(self):
        if not self.active_tab:
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if not file_path:
            return

        try:
            # Create the PDF
            c = canvas.Canvas(file_path, pagesize=letter)
            width, height = letter
            c.setFont('DejaVuSans', 12)
            
            # Add header
            c.setFont('DejaVuSans', 16)
            c.drawString(50, height - 50, "Math Expression Output")
            c.setFont('DejaVuSans', 10)
            c.drawString(50, height - 70, f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
            
            # Add content
            c.setFont('DejaVuSans', 12)
            output_text = self.tab_manager.tabs[self.active_tab]['output_text'].get("1.0", "end-1c")
            y = height - 100
            
            for line in output_text.split('\n'):
                if y < 50:  # Start new page if near bottom
                    c.showPage()
                    y = height - 50
                c.drawString(50, y, line)
                y -= 20
            
            c.save()
            self.show_notification("PDF exported successfully")
        
        except Exception as e:
            self.show_error(f"Error exporting PDF: {str(e)}")

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = MathTranslatorApp()
    app.run()
