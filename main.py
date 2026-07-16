import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk, ImageDraw
from datetime import datetime

import database
import styles
import exporter

class BankApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # 1. Window Configuration
        self.title("Apex Bank Management System")
        self.geometry("1150x700")
        self.minsize(1050, 650)
        self.configure(bg=styles.BG_DARK)
        
        # 2. Database & Assets initialization
        database.initialize_db()
        self.ensure_assets()
        
        # 3. GUI styling configuration
        styles.setup_ttk_styles()
        
        # 4. Variables
        self.current_panel = None
        self.uploaded_photo_path = None
        self.view_account_photo = None # To prevent garbage collection of image
        self.default_photo = None
        self.active_sidebar_tab = None
        
        # Load default photo
        self.load_default_photo()
        
        # 5. UI Layout
        # Master grid weights
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Sidebar Frame
        self.sidebar_frame = tk.Frame(self, bg=styles.BG_SIDEBAR, width=220)
        self.sidebar_frame.grid(row=0, column=0, sticky="ns")
        self.sidebar_frame.grid_propagate(False)
        self.setup_sidebar()
        
        # Main Content Container
        self.content_container = tk.Frame(self, bg=styles.BG_DARK)
        self.content_container.grid(row=0, column=1, sticky="nsew", padx=25, pady=25)
        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)
        
        # Notification Banner
        self.toast_label = tk.Label(self, text="", bg=styles.BG_CARD, fg=styles.TEXT_PRIMARY, font=styles.FONT_BOLD, relief="flat", highlightthickness=1, highlightbackground=styles.ACCENT_PRIMARY)
        # We will pack it using place dynamically when triggered
        
        # Setup Panels
        self.panels = {}
        self.setup_panels()
        
        # Show initial Dashboard panel
        self.show_panel("dashboard")

    def ensure_assets(self):
        """Create folders and generate default avatar image if missing."""
        os.makedirs('profile_pictures', exist_ok=True)
        os.makedirs('assets', exist_ok=True)
        
        avatar_path = os.path.join('assets', 'default_avatar.png')
        if not os.path.exists(avatar_path):
            try:
                # Generate custom stylish user silhouette avatar
                img = Image.new('RGB', (150, 150), color=styles.BG_CARD)
                draw = ImageDraw.Draw(img)
                # Outer circle frame
                draw.ellipse([15, 15, 135, 135], fill="#334155", outline=styles.ACCENT_PRIMARY, width=3)
                # Head
                draw.ellipse([60, 35, 90, 65], fill=styles.TEXT_SECONDARY)
                # Shoulders/Body
                draw.chord([35, 80, 115, 130], start=180, end=360, fill=styles.TEXT_SECONDARY)
                img.save(avatar_path)
            except Exception as e:
                print(f"Error creating default profile avatar: {e}")

    def load_default_photo(self):
        avatar_path = os.path.join('assets', 'default_avatar.png')
        if os.path.exists(avatar_path):
            try:
                img = Image.open(avatar_path)
                img = img.resize((120, 120), Image.Resampling.LANCZOS)
                self.default_photo = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Error loading default photo: {e}")

    def show_toast(self, message, is_success=True):
        """Display a fading notification toast at the bottom center of the window."""
        color = styles.ACCENT_SUCCESS if is_success else styles.ACCENT_DANGER
        self.toast_label.config(text=message, fg=styles.TEXT_PRIMARY, bg=styles.BG_CARD, highlightbackground=color)
        
        # Position toast centered at bottom of application window
        self.toast_label.place(relx=0.5, rely=0.92, anchor="s", height=45, width=450)
        
        # Automatically hide after 3.5 seconds
        self.after(3500, self.toast_label.place_forget)

    def setup_sidebar(self):
        """Create Sidebar layout with branding logo and navigation menu."""
        # Top Logo Header
        logo_canvas = tk.Canvas(self.sidebar_frame, width=200, height=80, bg=styles.BG_SIDEBAR, highlightthickness=0)
        logo_canvas.pack(pady=20)
        
        # Styled logo shield icon using Canvas
        styles.draw_rounded_rect(logo_canvas, 10, 10, 190, 70, 12, fill=styles.BG_CARD, outline=styles.ACCENT_PRIMARY, width=1.5)
        logo_canvas.create_text(100, 40, text="APEX BANK", fill=styles.TEXT_PRIMARY, font=("Segoe UI", 14, "bold"))
        
        # Navigation Buttons definition
        menu_items = [
            ("dashboard", "Dashboard"),
            ("accounts", "Accounts Central"),
            ("transactions", "Transactions"),
            ("export", "Export Ledger")
        ]
        
        self.sidebar_btns = {}
        for panel_name, label_text in menu_items:
            btn = tk.Button(
                self.sidebar_frame,
                text=f"  {label_text}",
                font=styles.FONT_BOLD,
                fg=styles.TEXT_SECONDARY,
                bg=styles.BG_SIDEBAR,
                activeforeground=styles.TEXT_PRIMARY,
                activebackground=styles.BG_CARD,
                relief="flat",
                bd=0,
                anchor="w",
                padx=25,
                pady=12,
                cursor="hand2",
                command=lambda name=panel_name: self.show_panel(name)
            )
            btn.pack(fill="x", pady=2)
            self.sidebar_btns[panel_name] = btn
            
            # Hover animations
            btn.bind("<Enter>", lambda e, b=btn: self.on_sidebar_hover(b))
            btn.bind("<Leave>", lambda e, b=btn, n=panel_name: self.on_sidebar_leave(b, n))

        # Bottom System Info
        version_label = tk.Label(self.sidebar_frame, text="System: v1.0.0", bg=styles.BG_SIDEBAR, fg=styles.TEXT_SECONDARY, font=styles.FONT_SMALL)
        version_label.pack(side="bottom", pady=20)

    def on_sidebar_hover(self, button):
        if button != self.sidebar_btns.get(self.active_sidebar_tab):
            button.config(bg=styles.BG_CARD, fg=styles.TEXT_PRIMARY)

    def on_sidebar_leave(self, button, panel_name):
        if panel_name != self.active_sidebar_tab:
            button.config(bg=styles.BG_SIDEBAR, fg=styles.TEXT_SECONDARY)

    def select_sidebar_tab(self, selected_name):
        self.active_sidebar_tab = selected_name
        for name, btn in self.sidebar_btns.items():
            if name == selected_name:
                btn.config(bg=styles.ACCENT_PRIMARY, fg=styles.TEXT_PRIMARY)
            else:
                btn.config(bg=styles.BG_SIDEBAR, fg=styles.TEXT_SECONDARY)

    def setup_panels(self):
        """Create and place all container frames for different application features."""
        # Dashboard Panel
        self.panels["dashboard"] = tk.Frame(self.content_container, bg=styles.BG_DARK)
        self.setup_dashboard_panel()
        
        # Accounts Panel
        self.panels["accounts"] = tk.Frame(self.content_container, bg=styles.BG_DARK)
        self.setup_accounts_panel()
        
        # Transactions Panel
        self.panels["transactions"] = tk.Frame(self.content_container, bg=styles.BG_DARK)
        self.setup_transactions_panel()
        
        # Export Panel
        self.panels["export"] = tk.Frame(self.content_container, bg=styles.BG_DARK)
        self.setup_export_panel()

    def show_panel(self, panel_name):
        """Switch current visible view container and refresh contents."""
        if self.current_panel:
            self.current_panel.grid_forget()
            
        self.select_sidebar_tab(panel_name)
        
        self.current_panel = self.panels[panel_name]
        self.current_panel.grid(row=0, column=0, sticky="nsew")
        
        # Call panel-specific refresh methods to load updated data
        if panel_name == "dashboard":
            self.refresh_dashboard()
        elif panel_name == "accounts":
            self.refresh_accounts_list()
        elif panel_name == "transactions":
            self.clear_transaction_forms()

    # ==========================================
    # DASHBOARD PANEL
    # ==========================================
    def setup_dashboard_panel(self):
        panel = self.panels["dashboard"]
        panel.grid_columnconfigure(0, weight=2)
        panel.grid_columnconfigure(1, weight=1)
        panel.grid_rowconfigure(1, weight=1)
        
        # Top Header Area
        header_frame = tk.Frame(panel, bg=styles.BG_DARK)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        
        title_label = tk.Label(header_frame, text="Financial Command Center", font=styles.FONT_TITLE, fg=styles.TEXT_PRIMARY, bg=styles.BG_DARK)
        title_label.pack(side="left")
        
        self.time_label = tk.Label(header_frame, text="", font=styles.FONT_BOLD, fg=styles.TEXT_SECONDARY, bg=styles.BG_DARK)
        self.time_label.pack(side="right", pady=10)
        self.update_clock()
        
        # Metrics Cards Container
        metrics_frame = tk.Frame(panel, bg=styles.BG_DARK)
        metrics_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        for i in range(3):
            metrics_frame.grid_columnconfigure(i, weight=1)
            
        # Metric Card 1: Total Users
        self.card_accounts = styles.ModernCard(metrics_frame)
        self.card_accounts.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        tk.Label(self.card_accounts, text="TOTAL ACCOUNTS", font=styles.FONT_SMALL, fg=styles.TEXT_SECONDARY, bg=styles.BG_CARD).pack(anchor="w")
        self.val_accounts = tk.Label(self.card_accounts, text="0", font=("Segoe UI", 24, "bold"), fg=styles.ACCENT_PRIMARY, bg=styles.BG_CARD)
        self.val_accounts.pack(anchor="w", pady=(5, 0))
        
        # Metric Card 2: Total Balance
        self.card_balance = styles.ModernCard(metrics_frame)
        self.card_balance.grid(row=0, column=1, padx=5, sticky="nsew")
        tk.Label(self.card_balance, text="TOTAL DEPOSITS (USD)", font=styles.FONT_SMALL, fg=styles.TEXT_SECONDARY, bg=styles.BG_CARD).pack(anchor="w")
        self.val_balance = tk.Label(self.card_balance, text="$0.00", font=("Segoe UI", 24, "bold"), fg=styles.ACCENT_SUCCESS, bg=styles.BG_CARD)
        self.val_balance.pack(anchor="w", pady=(5, 0))
        
        # Metric Card 3: Total Transactions
        self.card_tx = styles.ModernCard(metrics_frame)
        self.card_tx.grid(row=0, column=2, padx=(10, 0), sticky="nsew")
        tk.Label(self.card_tx, text="TOTAL TRANSACTIONS LOGGED", font=styles.FONT_SMALL, fg=styles.TEXT_SECONDARY, bg=styles.BG_CARD).pack(anchor="w")
        self.val_tx = tk.Label(self.card_tx, text="0", font=("Segoe UI", 24, "bold"), fg="#a855f7", bg=styles.BG_CARD)
        self.val_tx.pack(anchor="w", pady=(5, 0))
        
        # Lower Content Section (Table & Graph)
        lower_frame = tk.Frame(panel, bg=styles.BG_DARK)
        lower_frame.grid(row=2, column=0, columnspan=2, sticky="nsew")
        lower_frame.grid_columnconfigure(0, weight=3) # Ledger Table
        lower_frame.grid_columnconfigure(1, weight=2) # Chart Visualizer
        
        # Recent Ledger Card
        ledger_card = styles.ModernCard(lower_frame)
        ledger_card.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        
        tk.Label(ledger_card, text="Recent Transactions Ledger", font=styles.FONT_SUBTITLE, fg=styles.TEXT_PRIMARY, bg=styles.BG_CARD).pack(anchor="w", pady=(0, 10))
        
        # Transaction Treeview (List view table)
        table_frame = tk.Frame(ledger_card, bg=styles.BG_CARD)
        table_frame.pack(fill="both", expand=True)
        
        columns = ("acc", "type", "amount", "ref", "time")
        self.dash_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
        self.dash_tree.pack(side="left", fill="both", expand=True)
        
        self.dash_tree.heading("acc", text="Account No")
        self.dash_tree.heading("type", text="Type")
        self.dash_tree.heading("amount", text="Amount")
        self.dash_tree.heading("ref", text="Ref Acc")
        self.dash_tree.heading("time", text="Timestamp")
        
        self.dash_tree.column("acc", width=95, anchor="center")
        self.dash_tree.column("type", width=95, anchor="center")
        self.dash_tree.column("amount", width=90, anchor="e")
        self.dash_tree.column("ref", width=90, anchor="center")
        self.dash_tree.column("time", width=140, anchor="center")
        
        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.dash_tree.yview)
        scroll.pack(side="right", fill="y")
        self.dash_tree.configure(yscrollcommand=scroll.set)
        
        # Analytics Chart Card
        chart_card = styles.ModernCard(lower_frame)
        chart_card.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        
        self.chart_canvas = tk.Canvas(chart_card, bg=styles.BG_CARD, highlightthickness=0, height=220)
        self.chart_canvas.pack(fill="both", expand=True)

    def update_clock(self):
        """Live timestamp updater for main header."""
        now = datetime.now().strftime("%A, %d %B %Y | %I:%M:%S %p")
        self.time_label.config(text=now)
        self.after(1000, self.update_clock)

    def refresh_dashboard(self):
        """Query statistics and update metrics labels + transactions list."""
        stats = database.get_stats()
        self.val_accounts.config(text=f"{stats['total_accounts']}")
        self.val_balance.config(text=f"${stats['total_balance']:,.2f}")
        self.val_tx.config(text=f"{stats['total_transactions']}")
        
        # Clear & reload transactions table
        for r in self.dash_tree.get_children():
            self.dash_tree.delete(r)
            
        recent_txs = database.get_transactions(limit=8)
        for tx in recent_txs:
            amount_str = f"${tx['amount']:,.2f}"
            ref_acc = tx['reference_account'] if tx['reference_account'] else "None"
            self.dash_tree.insert("", "end", values=(
                tx['account_number'],
                tx['type'],
                amount_str,
                ref_acc,
                tx['timestamp']
            ))
            
        # Redraw chart
        accounts = database.get_all_accounts()
        self.draw_dashboard_chart(accounts)

    def draw_dashboard_chart(self, accounts):
        canvas = self.chart_canvas
        canvas.delete("all")
        
        if not accounts:
            canvas.create_text(150, 110, text="Register accounts to view distributions", fill=styles.TEXT_SECONDARY, font=styles.FONT_BOLD)
            return
            
        savings = sum(1 for a in accounts if a['account_type'] == 'Savings')
        current = sum(1 for a in accounts if a['account_type'] == 'Current')
        total = savings + current
        
        canvas.create_text(10, 20, anchor="w", text="Account Portfolio Type", fill=styles.TEXT_PRIMARY, font=styles.FONT_SUBTITLE)
        
        start_y = 60
        max_bar_width = 170
        bar_height = 20
        value_x_start = 85
        
        # Savings
        canvas.create_text(10, start_y + 10, anchor="w", text="Savings", fill=styles.TEXT_SECONDARY, font=styles.FONT_REGULAR)
        s_width = (savings / total) * max_bar_width if total > 0 else 0
        styles.draw_rounded_rect(canvas, value_x_start, start_y, value_x_start + max_bar_width, start_y + bar_height, 6, fill=styles.BORDER_COLOR, outline="")
        if s_width > 0:
            styles.draw_rounded_rect(canvas, value_x_start, start_y, value_x_start + s_width, start_y + bar_height, 6, fill=styles.ACCENT_PRIMARY, outline="")
        canvas.create_text(value_x_start + max_bar_width + 10, start_y + 10, anchor="w", text=f"{savings} ({savings/total*100:.0f}%)" if total > 0 else "0", fill=styles.TEXT_PRIMARY, font=styles.FONT_BOLD)
        
        # Current
        canvas.create_text(10, start_y + 60, anchor="w", text="Current", fill=styles.TEXT_SECONDARY, font=styles.FONT_REGULAR)
        c_width = (current / total) * max_bar_width if total > 0 else 0
        styles.draw_rounded_rect(canvas, value_x_start, start_y + 50, value_x_start + max_bar_width, start_y + 50 + bar_height, 6, fill=styles.BORDER_COLOR, outline="")
        if c_width > 0:
            styles.draw_rounded_rect(canvas, value_x_start, start_y + 50, value_x_start + c_width, start_y + 50 + bar_height, 6, fill=styles.ACCENT_SUCCESS, outline="")
        canvas.create_text(value_x_start + max_bar_width + 10, start_y + 60, anchor="w", text=f"{current} ({current/total*100:.0f}%)" if total > 0 else "0", fill=styles.TEXT_PRIMARY, font=styles.FONT_BOLD)
        
        # Summary text
        canvas.create_text(10, 160, anchor="w", text=f"Active System Portfolio Count: {total}", fill=styles.TEXT_SECONDARY, font=styles.FONT_SMALL)

    # ==========================================
    # ACCOUNTS CENTRAL PANEL
    # ==========================================
    def setup_accounts_panel(self):
        panel = self.panels["accounts"]
        
        # Main Notebook configuration
        self.accounts_notebook = ttk.Notebook(panel)
        self.accounts_notebook.pack(fill="both", expand=True)
        
        # Tab 1: All Accounts
        self.tab_all_acc = tk.Frame(self.accounts_notebook, bg=styles.BG_DARK)
        self.accounts_notebook.add(self.tab_all_acc, text="  Account Registry  ")
        self.setup_all_accounts_tab()
        
        # Tab 2: Create Account
        self.tab_create_acc = tk.Frame(self.accounts_notebook, bg=styles.BG_DARK)
        self.accounts_notebook.add(self.tab_create_acc, text="  Open New Account  ")
        self.setup_create_account_tab()

    def setup_all_accounts_tab(self):
        tab = self.tab_all_acc
        tab.grid_columnconfigure(0, weight=3) # Table view
        tab.grid_columnconfigure(1, weight=2) # Details slide
        tab.grid_rowconfigure(1, weight=1)
        
        # Search panel
        search_card = styles.ModernCard(tab, pady=8)
        search_card.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        
        tk.Label(search_card, text="Search Portfolio:", font=styles.FONT_BOLD, fg=styles.TEXT_PRIMARY, bg=styles.BG_CARD).pack(side="left", padx=(0, 10))
        
        self.search_entry = ttk.Entry(search_card, font=styles.FONT_REGULAR, width=28)
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_accounts_list())
        
        btn_search = styles.ModernButton(search_card, text="Search", command=self.refresh_accounts_list, width=80, height=28)
        btn_search.pack(side="left", padx=5)
        
        btn_clear = styles.ModernButton(search_card, text="Reset", command=self.clear_search, bg_color=styles.BORDER_COLOR, hover_color="#475569", width=80, height=28)
        btn_clear.pack(side="left", padx=5)
        
        # Accounts list card
        list_card = styles.ModernCard(tab)
        list_card.grid(row=1, column=0, padx=(0, 10), sticky="nsew")
        
        tk.Label(list_card, text="Registered Accounts Ledger", font=styles.FONT_SUBTITLE, fg=styles.TEXT_PRIMARY, bg=styles.BG_CARD).pack(anchor="w", pady=(0, 10))
        
        # Treeview table
        tbl_frame = tk.Frame(list_card, bg=styles.BG_CARD)
        tbl_frame.pack(fill="both", expand=True)
        
        columns = ("acc", "name", "type", "balance", "status")
        self.acc_tree = ttk.Treeview(tbl_frame, columns=columns, show="headings", height=12)
        self.acc_tree.pack(side="left", fill="both", expand=True)
        
        self.acc_tree.heading("acc", text="Account No")
        self.acc_tree.heading("name", text="Holder Name")
        self.acc_tree.heading("type", text="Type")
        self.acc_tree.heading("balance", text="Balance")
        self.acc_tree.heading("status", text="Status")
        
        self.acc_tree.column("acc", width=110, anchor="center")
        self.acc_tree.column("name", width=140, anchor="w")
        self.acc_tree.column("type", width=90, anchor="center")
        self.acc_tree.column("balance", width=100, anchor="e")
        self.acc_tree.column("status", width=90, anchor="center")
        
        scroll = ttk.Scrollbar(tbl_frame, orient="vertical", command=self.acc_tree.yview)
        scroll.pack(side="right", fill="y")
        self.acc_tree.configure(yscrollcommand=scroll.set)
        
        # Bind row selection event
        self.acc_tree.bind("<<TreeviewSelect>>", self.on_account_select)
        
        # Side detailed profile panel
        self.profile_card = styles.ModernCard(tab)
        self.profile_card.grid(row=1, column=1, padx=(10, 0), sticky="nsew")
        
        self.setup_profile_details_panel()

    def setup_profile_details_panel(self):
        parent = self.profile_card
        
        # Container showing detailed instruction when no account is selected
        self.empty_profile_label = tk.Label(parent, text="Select a client record from the list\nto view their comprehensive profile", font=styles.FONT_REGULAR, fg=styles.TEXT_SECONDARY, bg=styles.BG_CARD)
        self.empty_profile_label.pack(fill="both", expand=True)
        
        # Master detail view layout
        self.details_container = tk.Frame(parent, bg=styles.BG_CARD)
        
        # Photo and Core metadata row
        photo_header_frame = tk.Frame(self.details_container, bg=styles.BG_CARD)
        photo_header_frame.pack(fill="x", anchor="n", pady=(0, 15))
        
        self.profile_image_label = tk.Label(photo_header_frame, bg=styles.BG_CARD)
        self.profile_image_label.pack(side="left", padx=(0, 15))
        
        meta_sub_frame = tk.Frame(photo_header_frame, bg=styles.BG_CARD)
        meta_sub_frame.pack(side="left", fill="both", expand=True)
        
        self.lbl_profile_name = tk.Label(meta_sub_frame, text="Client Name", font=styles.FONT_TITLE, fg=styles.TEXT_PRIMARY, bg=styles.BG_CARD, anchor="w")
        self.lbl_profile_name.pack(fill="x", pady=(5, 2))
        
        self.lbl_profile_type = tk.Label(meta_sub_frame, text="Savings Account", font=styles.FONT_BOLD, fg=styles.ACCENT_PRIMARY, bg=styles.BG_CARD, anchor="w")
        self.lbl_profile_type.pack(fill="x")
        
        self.lbl_profile_status = tk.Label(meta_sub_frame, text="ACTIVE", font=styles.FONT_SMALL, fg=styles.TEXT_PRIMARY, bg=styles.ACCENT_SUCCESS, padx=6, pady=2)
        # Status pill pack below inside frame
        self.lbl_profile_status.pack(anchor="w", pady=(8, 0))
        
        # Information Grid Frame
        info_grid = tk.Frame(self.details_container, bg=styles.BG_CARD)
        info_grid.pack(fill="x", pady=10)
        info_grid.grid_columnconfigure(1, weight=1)
        
        fields = [
            ("Account No:", "acc_no"),
            ("IFSC Code:", "ifsc"),
            ("Address:", "address"),
            ("Balance:", "balance"),
            ("Joined Date:", "created_at")
        ]
        
        self.profile_lbls = {}
        for idx, (label_text, key) in enumerate(fields):
            tk.Label(info_grid, text=label_text, font=styles.FONT_BOLD, fg=styles.TEXT_SECONDARY, bg=styles.BG_CARD, anchor="w").grid(row=idx, column=0, pady=5, padx=(0, 15), sticky="w")
            lbl_val = tk.Label(info_grid, text="", font=styles.FONT_REGULAR, fg=styles.TEXT_PRIMARY, bg=styles.BG_CARD, anchor="w", wraplength=200)
            lbl_val.grid(row=idx, column=1, pady=5, sticky="ew")
            self.profile_lbls[key] = lbl_val
            
        # Action controls container
        actions_frame = tk.Frame(self.details_container, bg=styles.BG_CARD)
        actions_frame.pack(fill="x", pady=(20, 10))
        
        btn_edit = styles.ModernButton(actions_frame, text="Modify Profile", command=self.open_edit_profile_dialog, width=120, height=32)
        btn_edit.pack(side="left", padx=(0, 10))
        
        btn_statement = styles.ModernButton(actions_frame, text="Export Statement", command=self.export_selected_statement, bg_color=styles.ACCENT_SUCCESS, hover_color=styles.ACCENT_SUCCESS_HOVER, width=140, height=32)
        btn_statement.pack(side="left")

    def refresh_accounts_list(self):
        """Query DB with optional search filters and load to Account Registry treeview."""
        query = self.search_entry.get().strip()
        accounts = database.get_all_accounts(search_query=query if query else None)
        
        # Clear Treeview
        for r in self.acc_tree.get_children():
            self.acc_tree.delete(r)
            
        for acc in accounts:
            bal_str = f"${acc['balance']:,.2f}"
            self.acc_tree.insert("", "end", values=(
                acc['account_number'],
                acc['name'],
                acc['account_type'],
                bal_str,
                acc['status']
            ))
            
        # Hide details pane by default
        self.details_container.pack_forget()
        self.empty_profile_label.pack(fill="both", expand=True)

    def clear_search(self):
        self.search_entry.delete(0, tk.END)
        self.refresh_accounts_list()

    def on_account_select(self, event):
        """Event listener for account ledger row click to display details card."""
        sel = self.acc_tree.selection()
        if not sel:
            return
            
        acc_num = self.acc_tree.item(sel[0], "values")[0]
        acc = database.get_account(acc_num)
        if not acc:
            return
            
        # Hide placeholder label & render card detail frame
        self.empty_profile_label.pack_forget()
        self.details_container.pack(fill="both", expand=True)
        
        # Update metadata details
        self.lbl_profile_name.config(text=acc['name'])
        self.lbl_profile_type.config(text=f"{acc['account_type']} Portfolio")
        
        # Set status pill appearance
        if acc['status'] == 'Active':
            self.lbl_profile_status.config(text="ACTIVE", bg=styles.ACCENT_SUCCESS, fg=styles.TEXT_PRIMARY)
        else:
            self.lbl_profile_status.config(text=acc['status'].upper(), bg=styles.ACCENT_DANGER, fg=styles.TEXT_PRIMARY)
            
        self.profile_lbls["acc_no"].config(text=acc['account_number'])
        self.profile_lbls["ifsc"].config(text=acc['ifsc'])
        self.profile_lbls["address"].config(text=acc['address'])
        self.profile_lbls["balance"].config(text=f"${acc['balance']:,.2f}", fg=styles.ACCENT_SUCCESS, font=styles.FONT_BOLD)
        self.profile_lbls["created_at"].config(text=acc['created_at'])
        
        # Setup profile image loading
        photo_path = acc['photo_path']
        if photo_path and os.path.exists(photo_path):
            try:
                img = Image.open(photo_path)
                img = img.resize((120, 120), Image.Resampling.LANCZOS)
                self.view_account_photo = ImageTk.PhotoImage(img)
                self.profile_image_label.config(image=self.view_account_photo)
            except Exception as e:
                print(f"Error viewing profile picture: {e}")
                self.profile_image_label.config(image=self.default_photo)
        else:
            self.profile_image_label.config(image=self.default_photo)

    def export_selected_statement(self):
        """Export CSV statement for selected client account."""
        sel = self.acc_tree.selection()
        if not sel:
            return
            
        acc_num = self.acc_tree.item(sel[0], "values")[0]
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"Statement_{acc_num}.csv",
            title="Export Account Statement"
        )
        if not filepath:
            return
            
        success, msg = exporter.export_statement_to_csv(acc_num, filepath)
        self.show_toast(msg if success else f"Export failed: {msg}", is_success=success)

    def open_edit_profile_dialog(self):
        """Launch styled popup dialog to modify profile details."""
        sel = self.acc_tree.selection()
        if not sel:
            return
            
        acc_num = self.acc_tree.item(sel[0], "values")[0]
        acc = database.get_account(acc_num)
        if not acc:
            return
            
        dialog = tk.Toplevel(self)
        dialog.title("Edit Account Profile")
        dialog.geometry("450x520")
        dialog.configure(bg=styles.BG_DARK)
        dialog.transient(self)
        dialog.grab_set()
        
        # Form Container Card
        card = styles.ModernCard(dialog)
        card.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(card, text=f"Update Account #{acc_num}", font=styles.FONT_SUBTITLE, fg=styles.TEXT_PRIMARY, bg=styles.BG_CARD).pack(anchor="w", pady=(0, 15))
        
        # Input Rows Helper
        def create_dialog_field(label_text, val):
            row = tk.Frame(card, bg=styles.BG_CARD)
            row.pack(fill="x", pady=6)
            tk.Label(row, text=label_text, font=styles.FONT_BOLD, fg=styles.TEXT_SECONDARY, bg=styles.BG_CARD, width=12, anchor="w").pack(side="left")
            entry = ttk.Entry(row, font=styles.FONT_REGULAR)
            entry.pack(side="left", fill="x", expand=True)
            entry.insert(0, val)
            return entry
            
        entry_name = create_dialog_field("Full Name:", acc['name'])
        entry_ifsc = create_dialog_field("IFSC Code:", acc['ifsc'])
        
        # Address box
        row_addr = tk.Frame(card, bg=styles.BG_CARD)
        row_addr.pack(fill="x", pady=6)
        tk.Label(row_addr, text="Address:", font=styles.FONT_BOLD, fg=styles.TEXT_SECONDARY, bg=styles.BG_CARD, width=12, anchor="nw").pack(side="left")
        txt_address = tk.Text(row_addr, height=3, font=styles.FONT_REGULAR, bg=styles.BG_INPUT, fg=styles.TEXT_PRIMARY, insertbackground=styles.TEXT_PRIMARY, bd=1, relief="solid", highlightthickness=0)
        txt_address.pack(side="left", fill="x", expand=True)
        txt_address.insert("1.0", acc['address'])
        
        # Status dropdown
        row_status = tk.Frame(card, bg=styles.BG_CARD)
        row_status.pack(fill="x", pady=6)
        tk.Label(row_status, text="Status:", font=styles.FONT_BOLD, fg=styles.TEXT_SECONDARY, bg=styles.BG_CARD, width=12, anchor="w").pack(side="left")
        combo_status = ttk.Combobox(row_status, values=["Active", "Suspended", "Closed"], state="readonly")
        combo_status.pack(side="left", fill="x", expand=True)
        combo_status.set(acc['status'])
        
        # Photo path selection
        row_photo = tk.Frame(card, bg=styles.BG_CARD)
        row_photo.pack(fill="x", pady=8)
        tk.Label(row_photo, text="Profile Photo:", font=styles.FONT_BOLD, fg=styles.TEXT_SECONDARY, bg=styles.BG_CARD, width=12, anchor="w").pack(side="left")
        
        self.dialog_uploaded_photo_path = acc['photo_path']
        lbl_photo_status = tk.Label(row_photo, text="Current Image Saved" if acc['photo_path'] else "No Photo Uploaded", font=styles.FONT_SMALL, fg=styles.TEXT_SECONDARY, bg=styles.BG_CARD)
        lbl_photo_status.pack(side="left", padx=(0, 10))
        
        def choose_dialog_photo():
            file = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
            if file:
                self.dialog_uploaded_photo_path = file
                lbl_photo_status.config(text="New Image Selected", fg=styles.ACCENT_SUCCESS)
                
        btn_photo = styles.ModernButton(row_photo, text="Choose File", command=choose_dialog_photo, bg_color=styles.BORDER_COLOR, hover_color="#475569", width=95, height=26)
        btn_photo.pack(side="right")
        
        # Actions Row
        actions = tk.Frame(card, bg=styles.BG_CARD)
        actions.pack(side="bottom", fill="x", pady=(15, 0))
        
        def save_changes():
            name = entry_name.get().strip()
            ifsc = entry_ifsc.get().strip()
            address = txt_address.get("1.0", tk.END).strip()
            status = combo_status.get()
            
            if not name or not ifsc or not address:
                messagebox.showerror("Validation Error", "All fields must be filled!", parent=dialog)
                return
                
            photo_dest = acc['photo_path']
            # If path changed and a new local image is chosen
            if self.dialog_uploaded_photo_path and self.dialog_uploaded_photo_path != acc['photo_path']:
                photo_dest = self.save_profile_picture(acc_num, self.dialog_uploaded_photo_path)
                
            success, msg = database.update_account(acc_num, name, ifsc, address, photo_dest, status)
            if success:
                dialog.destroy()
                self.refresh_accounts_list()
                self.show_toast(msg, is_success=True)
            else:
                messagebox.showerror("Database Error", f"Failed to save: {msg}", parent=dialog)
                
        btn_save = styles.ModernButton(actions, text="Save Changes", command=save_changes, width=130, height=32)
        btn_save.pack(side="right", padx=5)
        
        btn_cancel = styles.ModernButton(actions, text="Cancel", command=dialog.destroy, bg_color=styles.BORDER_COLOR, hover_color="#475569", width=100, height=32)
        btn_cancel.pack(side="right", padx=5)

    # ==========================================
    # OPEN NEW ACCOUNT TAB
    # ==========================================
    def setup_create_account_tab(self):
        tab = self.tab_create_acc
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        # Form Container centered
        form_card = styles.ModernCard(tab)
        form_card.grid(row=0, column=0, padx=80, pady=30, sticky="nsew")
        form_card.grid_columnconfigure(1, weight=1)
        
        tk.Label(form_card, text="Registration Form", font=styles.FONT_SUBTITLE, fg=styles.TEXT_PRIMARY, bg=styles.BG_CARD).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))
        
        # Fields configuration
        def create_form_row(label_text, grid_row):
            tk.Label(form_card, text=label_text, font=styles.FONT_BOLD, fg=styles.TEXT_SECONDARY, bg=styles.BG_CARD, anchor="w").grid(row=grid_row, column=0, sticky="w", pady=8, padx=(0, 15))
            entry = ttk.Entry(form_card, font=styles.FONT_REGULAR)
            entry.grid(row=grid_row, column=1, sticky="ew", pady=8)
            return entry
            
        self.ent_acc_num = create_form_row("Account Number:", 1)
        
        # Auto generate button next to account number row
        acc_no_sub = tk.Frame(form_card, bg=styles.BG_CARD)
        self.ent_acc_num.grid_forget() # Custom positioning for account number field
        self.ent_acc_num.grid(row=1, column=1, sticky="ew", pady=8)
        
        def auto_generate_acc():
            import random
            generated = f"100{random.randint(100000, 999999)}"
            self.ent_acc_num.delete(0, tk.END)
            self.ent_acc_num.insert(0, generated)
            
        btn_gen = styles.ModernButton(form_card, text="Generate Auto", command=auto_generate_acc, bg_color=styles.BORDER_COLOR, hover_color="#475569", width=110, height=28)
        btn_gen.grid(row=1, column=2, padx=(10, 0), pady=8, sticky="w")
        
        self.ent_name = create_form_row("Holder Name:", 2)
        self.ent_ifsc = create_form_row("IFSC Code:", 3)
        
        # Address multi-line
        tk.Label(form_card, text="Address Details:", font=styles.FONT_BOLD, fg=styles.TEXT_SECONDARY, bg=styles.BG_CARD, anchor="w").grid(row=4, column=0, sticky="nw", pady=8, padx=(0, 15))
        self.txt_address = tk.Text(form_card, height=3, font=styles.FONT_REGULAR, bg=styles.BG_INPUT, fg=styles.TEXT_PRIMARY, insertbackground=styles.TEXT_PRIMARY, bd=1, relief="solid", highlightthickness=0)
        self.txt_address.grid(row=4, column=1, columnspan=2, sticky="ew", pady=8)
        
        # Account Type Combobox
        tk.Label(form_card, text="Account Type:", font=styles.FONT_BOLD, fg=styles.TEXT_SECONDARY, bg=styles.BG_CARD, anchor="w").grid(row=5, column=0, sticky="w", pady=8)
        self.combo_type = ttk.Combobox(form_card, values=["Savings", "Current"], state="readonly")
        self.combo_type.grid(row=5, column=1, sticky="ew", pady=8)
        self.combo_type.set("Savings")
        
        self.ent_balance = create_form_row("Initial Balance ($):", 6)
        self.ent_balance.insert(0, "0.00")
        
        # Image selector row
        tk.Label(form_card, text="Profile Photo:", font=styles.FONT_BOLD, fg=styles.TEXT_SECONDARY, bg=styles.BG_CARD, anchor="w").grid(row=7, column=0, sticky="w", pady=8)
        photo_select_frame = tk.Frame(form_card, bg=styles.BG_CARD)
        photo_select_frame.grid(row=7, column=1, columnspan=2, sticky="ew", pady=8)
        
        self.lbl_file_status = tk.Label(photo_select_frame, text="No picture selected", font=styles.FONT_SMALL, fg=styles.TEXT_SECONDARY, bg=styles.BG_CARD)
        self.lbl_file_status.pack(side="left", padx=(0, 15))
        
        btn_choose = styles.ModernButton(photo_select_frame, text="Browse Image", command=self.browse_create_photo, bg_color=styles.BORDER_COLOR, hover_color="#475569", width=110, height=28)
        btn_choose.pack(side="left")
        
        # Bottom Register button
        self.btn_submit = styles.ModernButton(form_card, text="Register Client Account", command=self.submit_registration, width=190, height=36)
        self.btn_submit.grid(row=8, column=1, sticky="w", pady=(20, 0))

    def browse_create_photo(self):
        file = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
        if file:
            self.uploaded_photo_path = file
            self.lbl_file_status.config(text="Photo Selected", fg=styles.ACCENT_SUCCESS)

    def save_profile_picture(self, account_number, source_path):
        if not source_path or not os.path.exists(source_path):
            return None
        try:
            dest_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'profile_pictures')
            os.makedirs(dest_dir, exist_ok=True)
            dest_path = os.path.join(dest_dir, f"{account_number}.png")
            
            img = Image.open(source_path)
            # Center crop to square
            width, height = img.size
            min_dim = min(width, height)
            img_cropped = img.crop(((width - min_dim) // 2,
                                    (height - min_dim) // 2,
                                    (width + min_dim) // 2,
                                    (height + min_dim) // 2))
            # Resize
            img_resized = img_cropped.resize((200, 200), Image.Resampling.LANCZOS)
            img_resized.save(dest_path, "PNG")
            return dest_path
        except Exception as e:
            print(f"Error resizing and saving picture: {e}")
            return None

    def submit_registration(self):
        acc_num = self.ent_acc_num.get().strip()
        name = self.ent_name.get().strip()
        ifsc = self.ent_ifsc.get().strip()
        address = self.txt_address.get("1.0", tk.END).strip()
        acc_type = self.combo_type.get()
        bal_raw = self.ent_balance.get().strip()
        
        # Validations
        if not acc_num or not name or not ifsc or not address or not bal_raw:
            messagebox.showerror("Form Error", "All form fields are mandatory!")
            return
            
        if not acc_num.isdigit():
            messagebox.showerror("Validation Error", "Account Number must contain digits only!")
            return
            
        try:
            initial_balance = float(bal_raw)
            if initial_balance < 0:
                messagebox.showerror("Validation Error", "Initial balance cannot be negative!")
                return
        except ValueError:
            messagebox.showerror("Validation Error", "Initial balance must be a valid numeric amount!")
            return
            
        # Copy and crop photo if selected
        photo_destination = None
        if self.uploaded_photo_path:
            photo_destination = self.save_profile_picture(acc_num, self.uploaded_photo_path)
            
        # Save to database
        success, msg = database.create_account(acc_num, name, ifsc, address, photo_destination, initial_balance, acc_type)
        
        if success:
            self.show_toast(msg, is_success=True)
            self.reset_create_account_form()
            # Direct redirection to the details panel
            self.show_panel("accounts")
        else:
            messagebox.showerror("Database Conflict", msg)

    def reset_create_account_form(self):
        self.ent_acc_num.delete(0, tk.END)
        self.ent_name.delete(0, tk.END)
        self.ent_ifsc.delete(0, tk.END)
        self.txt_address.delete("1.0", tk.END)
        self.ent_balance.delete(0, tk.END)
        self.ent_balance.insert(0, "0.00")
        self.lbl_file_status.config(text="No picture selected", fg=styles.TEXT_SECONDARY)
        self.uploaded_photo_path = None

    # ==========================================
    # TRANSACTIONS PANEL
    # ==========================================
    def setup_transactions_panel(self):
        panel = self.panels["transactions"]
        
        self.trans_notebook = ttk.Notebook(panel)
        self.trans_notebook.pack(fill="both", expand=True)
        
        # Sub-panels for Deposit, Withdraw, Transfer
        self.tab_deposit = tk.Frame(self.trans_notebook, bg=styles.BG_DARK)
        self.trans_notebook.add(self.tab_deposit, text="   Cash Deposit   ")
        self.setup_deposit_tab()
        
        self.tab_withdraw = tk.Frame(self.trans_notebook, bg=styles.BG_DARK)
        self.trans_notebook.add(self.tab_withdraw, text="   Cash Withdrawal   ")
        self.setup_withdraw_tab()
        
        self.tab_transfer = tk.Frame(self.trans_notebook, bg=styles.BG_DARK)
        self.trans_notebook.add(self.tab_transfer, text="   Account Transfer   ")
        self.setup_transfer_tab()

    def create_live_lookup_widget(self, parent_frame, entry_widget):
        """Helper to append a live metadata status label below an entry field."""
        lbl_status = tk.Label(parent_frame, text="", font=styles.FONT_SMALL, fg=styles.TEXT_SECONDARY, bg=styles.BG_CARD)
        lbl_status.pack(fill="x", anchor="w", pady=(2, 0))
        
        def trigger_lookup(event):
            acc_num = entry_widget.get().strip()
            if not acc_num:
                lbl_status.config(text="")
                return
            acc = database.get_account(acc_num)
            if acc:
                lbl_status.config(text=f"Client: {acc['name']} | Bal: ${acc['balance']:.2f} | Status: {acc['status']}",
                                 fg=styles.ACCENT_SUCCESS if acc['status'] == 'Active' else styles.ACCENT_DANGER)
            else:
                lbl_status.config(text="Account not registered!", fg=styles.ACCENT_DANGER)
                
        entry_widget.bind("<KeyRelease>", trigger_lookup)
        return lbl_status

    def setup_deposit_tab(self):
        tab = self.tab_deposit
        tab.grid_columnconfigure(0, weight=1)
        
        card = styles.ModernCard(tab)
        card.grid(row=0, column=0, padx=120, pady=50, sticky="nsew")
        card.grid_columnconfigure(1, weight=1)
        
        tk.Label(card, text="Deposit Funds", font=styles.FONT_SUBTITLE, fg=styles.TEXT_PRIMARY, bg=styles.BG_CARD).pack(anchor="w", pady=(0, 15))
        
        # Fields
        def create_tx_field(label_text):
            row = tk.Frame(card, bg=styles.BG_CARD)
            row.pack(fill="x", pady=8)
            tk.Label(row, text=label_text, font=styles.FONT_BOLD, fg=styles.TEXT_SECONDARY, bg=styles.BG_CARD, width=15, anchor="w").pack(side="left")
            entry = ttk.Entry(row, font=styles.FONT_REGULAR)
            entry.pack(side="left", fill="x", expand=True)
            return row, entry
            
        row_acc, self.dep_acc_entry = create_tx_field("Account Number:")
        self.dep_status = self.create_live_lookup_widget(row_acc, self.dep_acc_entry)
        
        _, self.dep_amount_entry = create_tx_field("Amount ($):")
        _, self.dep_desc_entry = create_tx_field("Description:")
        self.dep_desc_entry.insert(0, "Cash Deposit")
        
        # Button
        btn_frame = tk.Frame(card, bg=styles.BG_CARD)
        btn_frame.pack(fill="x", pady=(20, 0))
        btn = styles.ModernButton(btn_frame, text="Confirm Deposit", command=self.execute_deposit, width=150, height=34)
        btn.pack(side="right")

    def execute_deposit(self):
        acc = self.dep_acc_entry.get().strip()
        amount_raw = self.dep_amount_entry.get().strip()
        desc = self.dep_desc_entry.get().strip()
        
        if not acc or not amount_raw:
            messagebox.showerror("Transaction Error", "Account and Amount are required fields!")
            return
            
        try:
            amount = float(amount_raw)
            if amount <= 0:
                messagebox.showerror("Transaction Error", "Deposit amount must be positive!")
                return
        except ValueError:
            messagebox.showerror("Transaction Error", "Amount must be a numeric value!")
            return
            
        success, msg = database.deposit(acc, amount, desc)
        if success:
            self.show_toast(msg, is_success=True)
            self.clear_transaction_forms()
        else:
            messagebox.showerror("Transaction Failed", msg)

    def setup_withdraw_tab(self):
        tab = self.tab_withdraw
        tab.grid_columnconfigure(0, weight=1)
        
        card = styles.ModernCard(tab)
        card.grid(row=0, column=0, padx=120, pady=50, sticky="nsew")
        card.grid_columnconfigure(1, weight=1)
        
        tk.Label(card, text="Withdraw Funds", font=styles.FONT_SUBTITLE, fg=styles.TEXT_PRIMARY, bg=styles.BG_CARD).pack(anchor="w", pady=(0, 15))
        
        # Fields
        def create_tx_field(label_text):
            row = tk.Frame(card, bg=styles.BG_CARD)
            row.pack(fill="x", pady=8)
            tk.Label(row, text=label_text, font=styles.FONT_BOLD, fg=styles.TEXT_SECONDARY, bg=styles.BG_CARD, width=15, anchor="w").pack(side="left")
            entry = ttk.Entry(row, font=styles.FONT_REGULAR)
            entry.pack(side="left", fill="x", expand=True)
            return row, entry
            
        row_acc, self.wdr_acc_entry = create_tx_field("Account Number:")
        self.wdr_status = self.create_live_lookup_widget(row_acc, self.wdr_acc_entry)
        
        _, self.wdr_amount_entry = create_tx_field("Amount ($):")
        _, self.wdr_desc_entry = create_tx_field("Description:")
        self.wdr_desc_entry.insert(0, "ATM Withdrawal")
        
        # Button
        btn_frame = tk.Frame(card, bg=styles.BG_CARD)
        btn_frame.pack(fill="x", pady=(20, 0))
        btn = styles.ModernButton(btn_frame, text="Confirm Withdrawal", command=self.execute_withdraw, bg_color=styles.ACCENT_DANGER, hover_color=styles.ACCENT_DANGER_HOVER, width=160, height=34)
        btn.pack(side="right")

    def execute_withdraw(self):
        acc = self.wdr_acc_entry.get().strip()
        amount_raw = self.wdr_amount_entry.get().strip()
        desc = self.wdr_desc_entry.get().strip()
        
        if not acc or not amount_raw:
            messagebox.showerror("Transaction Error", "Account and Amount are required fields!")
            return
            
        try:
            amount = float(amount_raw)
            if amount <= 0:
                messagebox.showerror("Transaction Error", "Withdrawal amount must be positive!")
                return
        except ValueError:
            messagebox.showerror("Transaction Error", "Amount must be a numeric value!")
            return
            
        # Fetch status check
        db_acc = database.get_account(acc)
        if not db_acc:
            messagebox.showerror("Transaction Failed", "Account not found!")
            return
        if db_acc['balance'] < amount:
            messagebox.showerror("Transaction Failed", "Insufficient balance available!")
            return
            
        success, msg = database.withdraw(acc, amount, desc)
        if success:
            self.show_toast(msg, is_success=True)
            self.clear_transaction_forms()
        else:
            messagebox.showerror("Transaction Failed", msg)

    def setup_transfer_tab(self):
        tab = self.tab_transfer
        tab.grid_columnconfigure(0, weight=1)
        
        card = styles.ModernCard(tab)
        card.grid(row=0, column=0, padx=120, pady=30, sticky="nsew")
        card.grid_columnconfigure(1, weight=1)
        
        tk.Label(card, text="Funds Transfer", font=styles.FONT_SUBTITLE, fg=styles.TEXT_PRIMARY, bg=styles.BG_CARD).pack(anchor="w", pady=(0, 15))
        
        # Fields
        def create_tx_field(label_text):
            row = tk.Frame(card, bg=styles.BG_CARD)
            row.pack(fill="x", pady=6)
            tk.Label(row, text=label_text, font=styles.FONT_BOLD, fg=styles.TEXT_SECONDARY, bg=styles.BG_CARD, width=18, anchor="w").pack(side="left")
            entry = ttk.Entry(row, font=styles.FONT_REGULAR)
            entry.pack(side="left", fill="x", expand=True)
            return row, entry
            
        row_src, self.xfer_src_entry = create_tx_field("Sender Account Number:")
        self.xfer_src_status = self.create_live_lookup_widget(row_src, self.xfer_src_entry)
        
        row_dst, self.xfer_dst_entry = create_tx_field("Receiver Account Number:")
        self.xfer_dst_status = self.create_live_lookup_widget(row_dst, self.xfer_dst_entry)
        
        _, self.xfer_amount_entry = create_tx_field("Amount ($):")
        _, self.xfer_desc_entry = create_tx_field("Description:")
        self.xfer_desc_entry.insert(0, "Funds Transfer")
        
        # Button
        btn_frame = tk.Frame(card, bg=styles.BG_CARD)
        btn_frame.pack(fill="x", pady=(15, 0))
        btn = styles.ModernButton(btn_frame, text="Execute Transfer", command=self.execute_transfer, bg_color=styles.ACCENT_PRIMARY, hover_color=styles.ACCENT_HOVER, width=150, height=34)
        btn.pack(side="right")

    def execute_transfer(self):
        src = self.xfer_src_entry.get().strip()
        dst = self.xfer_dst_entry.get().strip()
        amount_raw = self.xfer_amount_entry.get().strip()
        desc = self.xfer_desc_entry.get().strip()
        
        if not src or not dst or not amount_raw:
            messagebox.showerror("Transaction Error", "Sender, Receiver, and Amount are required fields!")
            return
            
        if src == dst:
            messagebox.showerror("Transaction Error", "Sender and Receiver accounts must be different!")
            return
            
        try:
            amount = float(amount_raw)
            if amount <= 0:
                messagebox.showerror("Transaction Error", "Transfer amount must be positive!")
                return
        except ValueError:
            messagebox.showerror("Transaction Error", "Amount must be a numeric value!")
            return
            
        # Safety validations
        src_acc = database.get_account(src)
        if not src_acc:
            messagebox.showerror("Transaction Failed", "Sender account not found!")
            return
        if src_acc['balance'] < amount:
            messagebox.showerror("Transaction Failed", "Insufficient sender account balance!")
            return
            
        dst_acc = database.get_account(dst)
        if not dst_acc:
            messagebox.showerror("Transaction Failed", "Receiver account not found!")
            return
            
        success, msg = database.transfer(src, dst, amount, desc)
        if success:
            self.show_toast(msg, is_success=True)
            self.clear_transaction_forms()
        else:
            messagebox.showerror("Transaction Failed", msg)

    def clear_transaction_forms(self):
        # Clear entries
        for ent in [self.dep_acc_entry, self.dep_amount_entry, 
                    self.wdr_acc_entry, self.wdr_amount_entry,
                    self.xfer_src_entry, self.xfer_dst_entry, self.xfer_amount_entry]:
            ent.delete(0, tk.END)
            
        # Default description inserts
        self.dep_desc_entry.delete(0, tk.END)
        self.dep_desc_entry.insert(0, "Cash Deposit")
        self.wdr_desc_entry.delete(0, tk.END)
        self.wdr_desc_entry.insert(0, "ATM Withdrawal")
        self.xfer_desc_entry.delete(0, tk.END)
        self.xfer_desc_entry.insert(0, "Funds Transfer")
        
        # Reset live statuses
        for lbl in [self.dep_status, self.wdr_status, self.xfer_src_status, self.xfer_dst_status]:
            lbl.config(text="")

    # ==========================================
    # EXPORT LEDGER PANEL
    # ==========================================
    def setup_export_panel(self):
        panel = self.panels["export"]
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(0, weight=1)
        
        card = styles.ModernCard(panel)
        card.grid(row=0, column=0, padx=120, pady=50, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        
        tk.Label(card, text="Data Management Center", font=styles.FONT_TITLE, fg=styles.TEXT_PRIMARY, bg=styles.BG_CARD).pack(pady=(10, 5))
        tk.Label(card, text="Export system database records as formatted CSV spreadsheets.", font=styles.FONT_REGULAR, fg=styles.TEXT_SECONDARY, bg=styles.BG_CARD).pack(pady=(0, 30))
        
        # Inner grid of options
        options_frame = tk.Frame(card, bg=styles.BG_CARD)
        options_frame.pack(fill="x", padx=40)
        options_frame.grid_columnconfigure(0, weight=1)
        options_frame.grid_columnconfigure(1, weight=1)
        
        # Left Export Box (Accounts)
        box_acc = tk.LabelFrame(options_frame, text=" Accounts portfolio ", bg=styles.BG_CARD, fg=styles.TEXT_PRIMARY, font=styles.FONT_BOLD, padx=20, pady=20, relief="solid", bd=1)
        box_acc.grid(row=0, column=0, padx=(0, 15), sticky="nsew")
        
        tk.Label(box_acc, text="Download database profile list including accounts, registration dates, types, and current balance states.", font=styles.FONT_SMALL, fg=styles.TEXT_SECONDARY, bg=styles.BG_CARD, wraplength=200, justify="left").pack(pady=(0, 15))
        
        btn_exp_acc = styles.ModernButton(box_acc, text="Export Accounts", command=self.export_all_accounts, width=150, height=32)
        btn_exp_acc.pack()
        
        # Right Export Box (Transactions)
        box_tx = tk.LabelFrame(options_frame, text=" Transactions Ledger ", bg=styles.BG_CARD, fg=styles.TEXT_PRIMARY, font=styles.FONT_BOLD, padx=20, pady=20, relief="solid", bd=1)
        box_tx.grid(row=0, column=1, padx=(15, 0), sticky="nsew")
        
        tk.Label(box_tx, text="Download comprehensive transactional ledger records including deposits, withdrawals, and account-to-account transfers.", font=styles.FONT_SMALL, fg=styles.TEXT_SECONDARY, bg=styles.BG_CARD, wraplength=200, justify="left").pack(pady=(0, 15))
        
        btn_exp_tx = styles.ModernButton(box_tx, text="Export Transactions", command=self.export_all_transactions, bg_color=styles.ACCENT_SUCCESS, hover_color=styles.ACCENT_SUCCESS_HOVER, width=150, height=32)
        btn_exp_tx.pack()

    def export_all_accounts(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="accounts_ledger.csv",
            title="Save Accounts Ledger"
        )
        if not filepath:
            return
            
        success, msg = exporter.export_accounts_to_csv(filepath)
        self.show_toast(msg if success else f"Export failed: {msg}", is_success=success)

    def export_all_transactions(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="transactions_ledger.csv",
            title="Save Transaction Ledger"
        )
        if not filepath:
            return
            
        success, msg = exporter.export_transactions_to_csv(filepath)
        self.show_toast(msg if success else f"Export failed: {msg}", is_success=success)

if __name__ == "__main__":
    app = BankApp()
    app.mainloop()
