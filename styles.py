import tkinter as tk
from tkinter import ttk

# Modern Dark Theme Color Palette
BG_DARK = "#0f172a"          # App deep background
BG_CARD = "#1e293b"          # Card/Frame background
BG_SIDEBAR = "#111827"       # Sidebar background
ACCENT_PRIMARY = "#6366f1"   # Indigo Primary
ACCENT_HOVER = "#4f46e5"     # Darker Indigo Hover
ACCENT_SUCCESS = "#10b981"   # Emerald Success
ACCENT_SUCCESS_HOVER = "#059669"
ACCENT_DANGER = "#f43f5e"    # Rose Danger
ACCENT_DANGER_HOVER = "#e11d48"
TEXT_PRIMARY = "#f8fafc"     # Off-white Text
TEXT_SECONDARY = "#94a3b8"   # Gray Muted Text
BORDER_COLOR = "#334155"     # Slate Border
BG_INPUT = "#1e293b"         # Entry background

# Fonts
FONT_TITLE = ("Segoe UI", 18, "bold")
FONT_SUBTITLE = ("Segoe UI", 12, "bold")
FONT_REGULAR = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_SMALL = ("Segoe UI", 9)

def draw_rounded_rect(canvas, x1, y1, x2, y2, radius, **kwargs):
    """Draw a rounded rectangle on a Tkinter Canvas using a smooth polygon."""
    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1
    ]
    return canvas.create_polygon(points, **kwargs, smooth=True)

class ModernButton(tk.Canvas):
    """A beautiful, rounded flat button with custom hover states."""
    def __init__(self, parent, text, command, bg_color=ACCENT_PRIMARY, hover_color=ACCENT_HOVER, fg_color=TEXT_PRIMARY, width=120, height=36, corner_radius=10, font=FONT_BOLD):
        # We set highlightthickness=0 so the canvas doesn't show standard borders
        super().__init__(parent, width=width, height=height, bg=parent.cget("bg"), highlightthickness=0, bd=0, cursor="hand2")
        
        self.text = text
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.fg_color = fg_color
        self.corner_radius = corner_radius
        self.font = font
        self.width = width
        self.height = height
        
        self.rect_id = None
        self.text_id = None
        
        self.draw()
        
        # Event bindings for hover and click
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)

    def draw(self):
        self.delete("all")
        # Draw background rounded rectangle
        self.rect_id = draw_rounded_rect(self, 2, 2, self.width-2, self.height-2, self.corner_radius, fill=self.bg_color, outline="")
        # Draw center text
        self.text_id = self.create_text(self.width//2, self.height//2, text=self.text, fill=self.fg_color, font=self.font, justify="center")

    def on_enter(self, event):
        self.itemconfig(self.rect_id, fill=self.hover_color)

    def on_leave(self, event):
        self.itemconfig(self.rect_id, fill=self.bg_color)

    def on_click(self, event):
        if self.command:
            self.command()

class ModernCard(tk.Frame):
    """A container frame that has background coloring and borders to look like a clean modern card."""
    def __init__(self, parent, **kwargs):
        # Default card styles
        kwargs["bg"] = kwargs.get("bg", BG_CARD)
        kwargs["highlightbackground"] = kwargs.get("highlightbackground", BORDER_COLOR)
        kwargs["highlightcolor"] = kwargs.get("highlightcolor", BORDER_COLOR)
        kwargs["highlightthickness"] = kwargs.get("highlightthickness", 1)
        kwargs["padx"] = kwargs.get("padx", 15)
        kwargs["pady"] = kwargs.get("pady", 15)
        super().__init__(parent, **kwargs)

def setup_ttk_styles():
    """Configure modern styles for basic TTK widgets."""
    style = ttk.Style()
    # Use 'clam' as a foundation so we can customize colors cleanly
    style.theme_use('clam')
    
    # Treeview Styles (Tables)
    style.configure("Treeview",
                    background=BG_CARD,
                    foreground=TEXT_PRIMARY,
                    fieldbackground=BG_CARD,
                    rowheight=32,
                    font=FONT_REGULAR,
                    borderwidth=0)
    style.map("Treeview",
              background=[('selected', ACCENT_PRIMARY)],
              foreground=[('selected', TEXT_PRIMARY)])
              
    style.configure("Treeview.Heading",
                    background=BORDER_COLOR,
                    foreground=TEXT_PRIMARY,
                    font=FONT_BOLD,
                    borderwidth=0,
                    relief="flat")
    style.map("Treeview.Heading",
              background=[('active', ACCENT_PRIMARY)])
              
    # Scrollbar Styles
    style.configure("Vertical.TScrollbar",
                    gripcount=0,
                    background=BORDER_COLOR,
                    darkcolor=BG_DARK,
                    lightcolor=BG_DARK,
                    troughcolor=BG_DARK,
                    bordercolor=BG_DARK,
                    arrowcolor=TEXT_SECONDARY)
    style.map("Vertical.TScrollbar",
              background=[('active', ACCENT_PRIMARY), ('pressed', ACCENT_HOVER)])
              
    # Combobox Styles
    style.configure("TCombobox",
                    background=BORDER_COLOR,
                    foreground=TEXT_PRIMARY,
                    arrowcolor=TEXT_PRIMARY,
                    fieldbackground=BG_INPUT,
                    bordercolor=BORDER_COLOR,
                    lightcolor=BORDER_COLOR,
                    darkcolor=BORDER_COLOR)
    
    # Notebook/Tabs Styles
    style.configure("TNotebook", background=BG_DARK, borderwidth=0)
    style.configure("TNotebook.Tab",
                    background=BORDER_COLOR,
                    foreground=TEXT_SECONDARY,
                    padding=[12, 6],
                    font=FONT_BOLD,
                    borderwidth=0)
    style.map("TNotebook.Tab",
              background=[('selected', ACCENT_PRIMARY), ('active', BORDER_COLOR)],
              foreground=[('selected', TEXT_PRIMARY), ('active', TEXT_PRIMARY)])

    # Entry styles
    style.configure("TEntry",
                    fieldbackground=BG_INPUT,
                    foreground=TEXT_PRIMARY,
                    insertcolor=TEXT_PRIMARY,
                    bordercolor=BORDER_COLOR,
                    lightcolor=BORDER_COLOR,
                    darkcolor=BORDER_COLOR)
    
    # Progressbar Styles
    style.configure("Horizontal.TProgressbar",
                    troughcolor=BORDER_COLOR,
                    background=ACCENT_PRIMARY,
                    bordercolor=BORDER_COLOR)
                    
    # Radiobutton and Checkbutton Styles
    style.configure("TRadiobutton",
                    background=BG_CARD,
                    foreground=TEXT_PRIMARY,
                    font=FONT_REGULAR)
    style.configure("TCheckbutton",
                    background=BG_CARD,
                    foreground=TEXT_PRIMARY,
                    font=FONT_REGULAR)
