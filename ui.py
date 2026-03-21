"""
HPE MSA AI Command Generator - Complete Enhanced UI
With SSH connection, real disk inventory, and command execution
"""
import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
from datetime import datetime

from command_engine import generate_command
from xml_parser import parse_xml
from data import xml_data
from ssh_connector import MSAConnector
from msa_parser import MSAResponseParser


# Load initial sample disks
disks = parse_xml(xml_data)


class MSACommandGeneratorUI:
    def __init__(self, root):
        self.root = root
        self.root.title("HPE MSA AI Command Generator v2.0")
        self.root.geometry("1200x850")
        self.root.configure(bg="#1e1e1e")
        
        self.command_history = []
        self.execution_mode = "simulation"
        self.connected = False
        self.ssh_connector = None
        self.ssh_host = None
        self.ssh_username = None
        self.array_info = {}
        
        # Disk inventory - will be updated from array
        self.disks = disks
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        
        # HEADER
        header_frame = tk.Frame(self.root, bg="#2e5fa3", height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="🤖 HPE MSA AI Command Generator v2.0",
            font=("Arial", 20, "bold"),
            fg="white",
            bg="#2e5fa3"
        ).pack(pady=20)
        
        # CONNECTION PANEL
        self.create_connection_panel()
        
        # DISK INVENTORY PANEL (will update after connection)
        self.inventory_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.inventory_frame.pack(fill='x', padx=20, pady=10)
        self.create_inventory_display()
        
        # INPUT SECTION
        input_frame = tk.Frame(self.root, bg="#1e1e1e")
        input_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            input_frame,
            text="Enter Command (Natural Language):",
            font=("Arial", 11, "bold"),
            fg="white",
            bg="#1e1e1e"
        ).pack(anchor='w')
        
        self.entry = tk.Entry(
            input_frame,
            width=100,
            font=("Arial", 12),
            bg="#2b2b2b",
            fg="white",
            insertbackground="white"
        )
        self.entry.pack(pady=5, fill='x')
        self.entry.bind('<Return>', lambda e: self.run_command())
        
        # SUGGESTION CHIPS
        chip_frame = tk.Frame(input_frame, bg="#1e1e1e")
        chip_frame.pack(fill='x', pady=5)
        
        tk.Label(
            chip_frame,
            text="Quick Examples:",
            font=("Arial", 9),
            fg="#888888",
            bg="#1e1e1e"
        ).pack(side='left', padx=(0, 10))
        
        suggestions = [
            "show disks",
            "create raid 5 with 4 HDDs",
            "create 3 volumes of 100GB in pool a",
            "expand volume myvol size 50GB"
        ]
        
        for suggestion in suggestions:
            btn = tk.Button(
                chip_frame,
                text=suggestion,
                font=("Arial", 8),
                bg="#3a3a3a",
                fg="#00ffcc",
                relief='flat',
                command=lambda s=suggestion: self.insert_suggestion(s),
                cursor="hand2"
            )
            btn.pack(side='left', padx=3)
        
        # BUTTONS
        button_frame = tk.Frame(self.root, bg="#1e1e1e")
        button_frame.pack(fill='x', padx=20, pady=5)
        
        tk.Button(
            button_frame,
            text="✨ Generate Command",
            font=("Arial", 12, "bold"),
            bg="#00cc66",
            fg="white",
            relief='flat',
            command=self.run_command,
            cursor="hand2"
        ).pack(side='left', padx=5)
        
        self.execute_btn = tk.Button(
            button_frame,
            text="▶️ Execute (Simulation)",
            font=("Arial", 11, "bold"),
            bg="#ff9500",
            fg="white",
            relief='flat',
            command=self.execute_command,
            cursor="hand2",
            state='disabled'
        )
        self.execute_btn.pack(side='left', padx=5)
        
        # Output format toggle
        self.output_format_var = tk.StringVar(value="formatted")
        
        tk.Label(
            button_frame,
            text="Output:",
            font=("Arial", 9),
            fg="#888888",
            bg="#1e1e1e"
        ).pack(side='left', padx=(15, 5))
        
        tk.Radiobutton(
            button_frame,
            text="Formatted",
            variable=self.output_format_var,
            value="formatted",
            bg="#1e1e1e",
            fg="white",
            selectcolor="#2b2b2b",
            activebackground="#1e1e1e",
            font=("Arial", 9)
        ).pack(side='left')
        
        tk.Radiobutton(
            button_frame,
            text="Raw XML",
            variable=self.output_format_var,
            value="raw",
            bg="#1e1e1e",
            fg="white",
            selectcolor="#2b2b2b",
            activebackground="#1e1e1e",
            font=("Arial", 9)
        ).pack(side='left')
        
        tk.Button(
            button_frame,
            text="🗑️ Clear",
            font=("Arial", 10),
            bg="#cc3333",
            fg="white",
            relief='flat',
            command=self.clear_output,
            cursor="hand2"
        ).pack(side='left', padx=5)
        
        tk.Button(
            button_frame,
            text="❓ Help",
            font=("Arial", 10),
            bg="#3366cc",
            fg="white",
            relief='flat',
            command=self.show_help,
            cursor="hand2"
        ).pack(side='left', padx=5)
        
        # OUTPUT SECTION
        tk.Label(
            self.root,
            text="Generated Commands & Results:",
            font=("Arial", 11, "bold"),
            fg="white",
            bg="#1e1e1e"
        ).pack(anchor='w', padx=20)
        
        self.output_box = scrolledtext.ScrolledText(
            self.root,
            width=100,
            height=16,
            font=("Consolas", 10),
            bg="#0d1117",
            fg="#00ffcc",
            insertbackground="#00ffcc",
            selectbackground="#264f78"
        )
        self.output_box.pack(padx=20, pady=5, fill='both', expand=True)
        
        # Configure text tags
        self.output_box.tag_config("error", foreground="#ff6b6b")
        self.output_box.tag_config("warning", foreground="#ffa500")
        self.output_box.tag_config("success", foreground="#00ffcc")
        self.output_box.tag_config("input", foreground="#ffffff", font=("Consolas", 10, "bold"))
        self.output_box.tag_config("timestamp", foreground="#888888", font=("Consolas", 9))
        self.output_box.tag_config("execution", foreground="#00ff00", font=("Consolas", 10, "bold"))
        self.output_box.tag_config("simulation", foreground="#ffaa00", font=("Consolas", 10))
        self.output_box.tag_config("info", foreground="#88ccff", font=("Consolas", 9))
        
        # STATUS BAR
        status_frame = tk.Frame(self.root, bg="#2e5fa3", height=30)
        status_frame.pack(fill='x', side='bottom')
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            status_frame,
            text="Ready | Mode: Simulation",
            font=("Arial", 9),
            fg="white",
            bg="#2e5fa3",
            anchor='w'
        )
        self.status_label.pack(fill='x', padx=10)
        
        self.last_command = None
    
    def create_connection_panel(self):
        """Create connection settings panel"""
        conn_frame = tk.LabelFrame(
            self.root,
            text="⚙️ Execution Mode & Connection",
            font=("Arial", 10, "bold"),
            bg="#2b2b2b",
            fg="white",
            relief='solid',
            borderwidth=1
        )
        conn_frame.pack(fill='x', padx=20, pady=10)
        
        mode_frame = tk.Frame(conn_frame, bg="#2b2b2b")
        mode_frame.pack(side='left', padx=15, pady=10)
        
        tk.Label(
            mode_frame,
            text="Execution Mode:",
            font=("Arial", 9, "bold"),
            fg="#888888",
            bg="#2b2b2b"
        ).pack(side='left', padx=(0, 10))
        
        self.mode_var = tk.StringVar(value="simulation")
        
        tk.Radiobutton(
            mode_frame,
            text="🔵 Simulation (Safe)",
            variable=self.mode_var,
            value="simulation",
            bg="#2b2b2b",
            fg="white",
            selectcolor="#1e1e1e",
            activebackground="#2b2b2b",
            command=self.on_mode_change,
            cursor="hand2"
        ).pack(side='left', padx=5)
        
        tk.Radiobutton(
            mode_frame,
            text="🔴 Live (Array)",
            variable=self.mode_var,
            value="live",
            bg="#2b2b2b",
            fg="white",
            selectcolor="#1e1e1e",
            activebackground="#2b2b2b",
            command=self.on_mode_change,
            cursor="hand2"
        ).pack(side='left', padx=5)
        
        control_frame = tk.Frame(conn_frame, bg="#2b2b2b")
        control_frame.pack(side='right', padx=15, pady=10)
        
        self.status_indicator = tk.Label(
            control_frame,
            text="● Simulation Mode",
            font=("Arial", 9, "bold"),
            fg="#00ff00",
            bg="#2b2b2b"
        )
        self.status_indicator.pack(side='left', padx=10)
        
        self.connect_btn = tk.Button(
            control_frame,
            text="🔌 Connect to Array",
            font=("Arial", 9, "bold"),
            bg="#3366cc",
            fg="white",
            relief='flat',
            command=self.show_connection_dialog,
            cursor="hand2",
            state='disabled'
        )
        self.connect_btn.pack(side='left', padx=5)
    
    def create_inventory_display(self):
        """Create or update disk inventory summary"""
        # Clear existing widgets
        for widget in self.inventory_frame.winfo_children():
            widget.destroy()
        
        total = len(self.disks)
        free = len([d for d in self.disks if d.get('status') == 'free'])
        used = total - free
        ssd_free = len([d for d in self.disks if d.get('type') == 'ssd' and d.get('status') == 'free'])
        hdd_free = len([d for d in self.disks if d.get('type') == 'hdd' and d.get('status') == 'free'])
        
        inv_container = tk.Frame(self.inventory_frame, bg="#2b2b2b", relief='solid', borderwidth=1)
        inv_container.pack(fill='x', pady=5)
        
        title_text = "📊 Disk Inventory"
        if self.connected and self.ssh_host:
            title_text += f" (Live from {self.ssh_host})"
        
        tk.Label(
            inv_container,
            text=title_text,
            font=("Arial", 10, "bold"),
            fg="#00ffcc",
            bg="#2b2b2b"
        ).pack(anchor='w', padx=10, pady=5)
        
        stats_frame = tk.Frame(inv_container, bg="#2b2b2b")
        stats_frame.pack(fill='x', padx=10, pady=5)
        
        stats = [
            ("Total Disks", str(total)),
            ("Used", str(used)),
            ("Free", str(free)),
            ("SSDs Available", str(ssd_free)),
            ("HDDs Available", str(hdd_free))
        ]
        
        for label, value in stats:
            stat_frame = tk.Frame(stats_frame, bg="#2b2b2b")
            stat_frame.pack(side='left', padx=10)
            
            tk.Label(
                stat_frame,
                text=label + ":",
                font=("Arial", 9),
                fg="#888888",
                bg="#2b2b2b"
            ).pack(side='left')
            
            tk.Label(
                stat_frame,
                text=value,
                font=("Arial", 9, "bold"),
                fg="white",
                bg="#2b2b2b"
            ).pack(side='left', padx=5)
    
    def on_mode_change(self):
        """Handle execution mode change"""
        self.execution_mode = self.mode_var.get()
        
        if self.execution_mode == "simulation":
            self.status_indicator.config(text="● Simulation Mode", fg="#00ff00")
            self.connect_btn.config(state='disabled')
            self.execute_btn.config(text="▶️ Execute (Simulation)", bg="#ff9500")
            self.status_label.config(text="Mode: Simulation - Safe testing")
        else:
            self.status_indicator.config(text="● Live Mode", fg="#ff6b00")
            self.connect_btn.config(state='normal')
            self.execute_btn.config(text="▶️ Execute on Array", bg="#ff3333")
            
            if self.connected:
                self.status_label.config(text=f"Mode: Live - Connected to {self.ssh_host}")
            else:
                self.status_label.config(text="Mode: Live - Click 'Connect to Array'")
    
    def show_connection_dialog(self):
        """Show dialog to enter SSH connection details"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Connect to HPE MSA Array")
        dialog.geometry("550x500")
        dialog.configure(bg="#2b2b2b")
        dialog.transient(self.root)
        dialog.grab_set()
        
        dialog.geometry("+%d+%d" % (
            self.root.winfo_x() + self.root.winfo_width()//2 - 275,
            self.root.winfo_y() + self.root.winfo_height()//2 - 250
        ))
        
        # Header
        header_frame = tk.Frame(dialog, bg="#3366cc", height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="🔌 Connect to HPE MSA Array",
            font=("Arial", 14, "bold"),
            fg="white",
            bg="#3366cc"
        ).pack(pady=15)
        
        tk.Label(
            dialog,
            text="Enter your MSA array connection details below:",
            font=("Arial", 9),
            fg="#888888",
            bg="#2b2b2b"
        ).pack(pady=10)
        
        # Form
        form_frame = tk.Frame(dialog, bg="#2b2b2b")
        form_frame.pack(padx=40, pady=10, fill='both', expand=True)
        
        # Host/IP
        tk.Label(form_frame, text="Host/IP Address:", fg="white", bg="#2b2b2b", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky='w', pady=12)
        host_entry = tk.Entry(form_frame, width=35, bg="#1e1e1e", fg="white", font=("Arial", 10), insertbackground="white")
        host_entry.grid(row=0, column=1, pady=12, padx=10, sticky='ew')
        host_entry.insert(0, "192.168.1.100")
        
        tk.Label(form_frame, text="(e.g., 192.168.1.100)", fg="#666666", bg="#2b2b2b", font=("Arial", 7)).grid(row=1, column=1, sticky='w', padx=10)
        
        # Username
        tk.Label(form_frame, text="Username:", fg="white", bg="#2b2b2b", font=("Arial", 9, "bold")).grid(row=2, column=0, sticky='w', pady=12)
        user_entry = tk.Entry(form_frame, width=35, bg="#1e1e1e", fg="white", font=("Arial", 10), insertbackground="white")
        user_entry.grid(row=2, column=1, pady=12, padx=10, sticky='ew')
        user_entry.insert(0, "manage")
        
        tk.Label(form_frame, text="(default: manage)", fg="#666666", bg="#2b2b2b", font=("Arial", 7)).grid(row=3, column=1, sticky='w', padx=10)
        
        # Password
        tk.Label(form_frame, text="Password:", fg="white", bg="#2b2b2b", font=("Arial", 9, "bold")).grid(row=4, column=0, sticky='w', pady=12)
        pass_entry = tk.Entry(form_frame, width=35, show="●", bg="#1e1e1e", fg="white", font=("Arial", 10), insertbackground="white")
        pass_entry.grid(row=4, column=1, pady=12, padx=10, sticky='ew')
        
        show_pass_var = tk.BooleanVar()
        tk.Checkbutton(
            form_frame,
            text="Show password",
            variable=show_pass_var,
            command=lambda: pass_entry.config(show="" if show_pass_var.get() else "●"),
            fg="#888888",
            bg="#2b2b2b",
            selectcolor="#1e1e1e",
            font=("Arial", 8)
        ).grid(row=5, column=1, sticky='w', padx=10)
        
        # Port
        tk.Label(form_frame, text="SSH Port:", fg="white", bg="#2b2b2b", font=("Arial", 9, "bold")).grid(row=6, column=0, sticky='w', pady=12)
        port_entry = tk.Entry(form_frame, width=35, bg="#1e1e1e", fg="white", font=("Arial", 10), insertbackground="white")
        port_entry.grid(row=6, column=1, pady=12, padx=10, sticky='ew')
        port_entry.insert(0, "22")
        
        tk.Label(form_frame, text="(default: 22)", fg="#666666", bg="#2b2b2b", font=("Arial", 7)).grid(row=7, column=1, sticky='w', padx=10)
        
        form_frame.columnconfigure(1, weight=1)
        
        # Status message
        status_frame = tk.Frame(dialog, bg="#2b2b2b")
        status_frame.pack(pady=10, fill='x', padx=40)
        
        status_msg = tk.Label(status_frame, text="", fg="#ffaa00", bg="#2b2b2b", font=("Arial", 9), wraplength=450, justify='left')
        status_msg.pack()
        
        # Buttons
        btn_frame = tk.Frame(dialog, bg="#2b2b2b")
        btn_frame.pack(pady=15)
        
        def attempt_connect():
            host = host_entry.get().strip()
            username = user_entry.get().strip()
            password = pass_entry.get()
            port = port_entry.get().strip() or "22"
            
            if not host:
                status_msg.config(text="❌ Please enter Host/IP Address", fg="#ff6b6b")
                return
            if not username:
                status_msg.config(text="❌ Please enter Username", fg="#ff6b6b")
                return
            if not password:
                status_msg.config(text="❌ Please enter Password", fg="#ff6b6b")
                return
            
            connect_button.config(state='disabled')
            cancel_button.config(state='disabled')
            status_msg.config(text="🔄 Connecting to array...", fg="#ffaa00")
            dialog.update()
            
            # Create SSH connector
            self.ssh_connector = MSAConnector(host, username, password, int(port))
            result = self.ssh_connector.connect()
            
            if result is True:
                # Connection successful
                self.connected = True
                self.ssh_host = host
                self.ssh_username = username
                
                # Get array information
                self.fetch_array_info()
                
                # Update inventory from live array
                self.fetch_disk_inventory()
                
                dialog.destroy()
                
            else:
                status_msg.config(text=f"❌ {result}", fg="#ff6b6b")
                connect_button.config(state='normal')
                cancel_button.config(state='normal')
        
        connect_button = tk.Button(btn_frame, text="🔌 Connect", font=("Arial", 11, "bold"), bg="#00cc66", fg="white", width=14, command=attempt_connect, cursor="hand2")
        connect_button.pack(side='left', padx=5)
        
        cancel_button = tk.Button(btn_frame, text="Cancel", font=("Arial", 11), bg="#666666", fg="white", width=14, command=dialog.destroy, cursor="hand2")
        cancel_button.pack(side='left', padx=5)
        
        tk.Label(dialog, text="🔒 Connection encrypted via SSH", fg="#666666", bg="#2b2b2b", font=("Arial", 8)).pack(pady=5)
        
        dialog.bind('<Return>', lambda e: attempt_connect())
        host_entry.focus()
    
    def fetch_array_info(self):
        """Fetch and display array information after connection"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.output_box.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.output_box.insert(tk.END, f"🔄 Fetching array information...\n", "info")
        self.output_box.see(tk.END)
        self.root.update()
        
        # Execute 'show configuration' to get array info
        response = self.ssh_connector.execute_command("show configuration")
        array_data = MSAResponseParser.parse_whoami(response)
        
        self.array_info = array_data
        
        # Display connection success with array info
        self.output_box.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.output_box.insert(tk.END, "✅ Successfully connected to HPE MSA Array\n", "execution")
        self.output_box.insert(tk.END, f"   Host: {self.ssh_host}\n", "success")
        self.output_box.insert(tk.END, f"   User: {self.ssh_username}\n", "success")
        
        if array_data.get("system_name"):
            self.output_box.insert(tk.END, f"   System Name: {array_data['system_name']}\n", "success")
        if array_data.get("model"):
            self.output_box.insert(tk.END, f"   Model: {array_data['model']}\n", "success")
        if array_data.get("version"):
            self.output_box.insert(tk.END, f"   Firmware: {array_data['version']}\n", "success")
        
        self.output_box.insert(tk.END, "   Status: Ready to execute commands\n\n", "success")
        self.output_box.see(tk.END)
        
        # Update UI
        self.status_indicator.config(text=f"● Connected: {self.ssh_host}", fg="#00ff00")
        self.status_label.config(text=f"✅ Connected to {self.ssh_host} ({array_data.get('model', 'MSA Array')})")
        self.connect_btn.config(text="✓ Disconnect", bg="#cc3333", command=self.disconnect_from_array)
        
        messagebox.showinfo(
            "Connection Successful",
            f"✅ Connected to HPE MSA Array\n\n"
            f"Host: {self.ssh_host}\n"
            f"Model: {array_data.get('model', 'N/A')}\n"
            f"System: {array_data.get('system_name', 'N/A')}\n\n"
            f"Ready to execute commands."
        )
    
    def fetch_disk_inventory(self):
        """Fetch live disk inventory from array"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.output_box.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.output_box.insert(tk.END, "🔄 Fetching disk inventory from array...\n", "info")
        self.output_box.see(tk.END)
        self.root.update()
        
        # Execute 'show disks'
        response = self.ssh_connector.execute_command("show disks")
        disks_data = MSAResponseParser.parse_show_disks(response)
        
        if disks_data:
            self.disks = disks_data
            
            # Update inventory display
            self.create_inventory_display()
            
            # Show summary
            summary = MSAResponseParser.format_disk_summary(disks_data)
            self.output_box.insert(tk.END, f"[{timestamp}] ", "timestamp")
            self.output_box.insert(tk.END, f"✅ Disk inventory updated from live array\n", "execution")
            self.output_box.insert(tk.END, summary + "\n", "info")
            self.output_box.see(tk.END)
    
    def disconnect_from_array(self):
        """Disconnect from MSA array"""
        if not self.connected:
            return
        
        confirm = messagebox.askyesno(
            "Disconnect",
            f"Disconnect from {self.ssh_host}?\n\n"
            "Any pending commands will not be executed."
        )
        
        if not confirm:
            return
        
        if self.ssh_connector:
            self.ssh_connector.disconnect()
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.output_box.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.output_box.insert(tk.END, f"🔌 Disconnected from {self.ssh_host}\n\n", "warning")
        self.output_box.see(tk.END)
        
        self.connected = False
        self.ssh_connector = None
        self.status_indicator.config(text="● Live Mode (Not Connected)", fg="#ff6b00")
        self.status_label.config(text="Mode: Live - Click 'Connect to Array'")
        self.connect_btn.config(text="🔌 Connect to Array", bg="#3366cc", command=self.show_connection_dialog)
        
        self.ssh_host = None
        self.ssh_username = None
        self.array_info = {}
    
    def insert_suggestion(self, text):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, text)
        self.entry.focus()
    
    def run_command(self):
        """Generate command"""
        user_input = self.entry.get().strip()
        
        if not user_input:
            self.status_label.config(text="⚠️  Please enter a command")
            return
        
        try:
            result = generate_command(user_input, self.disks)
            self.last_command = result
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            self.output_box.insert(tk.END, f"[{timestamp}] ", "timestamp")
            self.output_box.insert(tk.END, f"Input: {user_input}\n", "input")
            
            if "❌" in result or "❗" in result:
                self.output_box.insert(tk.END, f"{result}\n\n", "error")
                self.status_label.config(text="❌ Error in command")
                self.execute_btn.config(state='disabled')
                self.last_command = None
            elif "⚠️" in result:
                self.output_box.insert(tk.END, f"{result}\n\n", "warning")
                self.status_label.config(text="⚠️  Warning issued")
                self.execute_btn.config(state='normal')
            else:
                self.output_box.insert(tk.END, f"✓ {result}\n\n", "success")
                self.status_label.config(text="✅ Command generated")
                self.execute_btn.config(state='normal')
                self.command_history.append({"timestamp": timestamp, "input": user_input, "output": result})
            
            self.output_box.see(tk.END)
            self.entry.delete(0, tk.END)
            
        except Exception as e:
            self.output_box.insert(tk.END, f"❌ Error: {str(e)}\n\n", "error")
            self.execute_btn.config(state='disabled')
    
    def execute_command(self):
        """Execute the last generated command"""
        if not self.last_command:
            messagebox.showwarning("No Command", "Generate a command first.")
            return
        
        command = self.last_command
        if "✓" in command:
            command = command.split("✓")[-1].strip()
        if "\n" in command:
            command = command.split("\n")[0].strip()
        
        # Check destructive commands
        destructive = any(kw in command.lower() for kw in ['delete', 'remove', 'clear', 'format'])
        
        if destructive and self.execution_mode == "live":
            if not messagebox.askyesno("Confirm", f"⚠️ Destructive command:\n\n{command}\n\nContinue?"):
                return
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if self.execution_mode == "simulation":
            self.output_box.insert(tk.END, f"[{timestamp}] ", "timestamp")
            self.output_box.insert(tk.END, "🔵 SIMULATION MODE\n", "simulation")
            self.output_box.insert(tk.END, f"Command: {command}\n", "success")
            self.output_box.insert(tk.END, "✓ Simulation successful (no changes)\n\n", "simulation")
            self.status_label.config(text="✓ Simulation completed")
        else:
            if not self.connected:
                messagebox.showerror("Not Connected", "Connect to array first.")
                return
            
            self.output_box.insert(tk.END, f"[{timestamp}] ", "timestamp")
            self.output_box.insert(tk.END, f"🔴 EXECUTING ON {self.ssh_host}\n", "execution")
            self.output_box.insert(tk.END, f"Command: {command}\n", "success")
            self.output_box.insert(tk.END, "⏳ Executing...\n", "warning")
            self.output_box.see(tk.END)
            self.root.update()
            
            # Execute on array
            response = self.ssh_connector.execute_command(command)
            
            # Parse response
            if self.output_format_var.get() == "raw":
                # Show raw XML
                self.output_box.insert(tk.END, "\n--- Raw Response ---\n", "info")
                self.output_box.insert(tk.END, response[:1000] + "...\n\n" if len(response) > 1000 else response + "\n\n", "info")
            else:
                # Show formatted response
                parsed = MSAResponseParser.parse_command_response(response)
                
                if parsed["success"]:
                    self.output_box.insert(tk.END, "✅ Command executed successfully\n", "execution")
                    self.output_box.insert(tk.END, f"Response: {parsed['message']}\n", "success")
                    if parsed["timestamp"]:
                        self.output_box.insert(tk.END, f"Timestamp: {parsed['timestamp']}\n", "info")
                else:
                    self.output_box.insert(tk.END, "❌ Command failed\n", "error")
                    self.output_box.insert(tk.END, f"Error: {parsed['message']}\n", "error")
                
                self.output_box.insert(tk.END, "\n", "info")
            
            self.status_label.config(text=f"✅ Executed on {self.ssh_host}")
        
        self.output_box.see(tk.END)
    
    def clear_output(self):
        self.output_box.delete(1.0, tk.END)
        self.execute_btn.config(state='disabled')
        self.last_command = None
    
    def show_help(self):
        help_text = """
╔══════════════════════════════════════════════════════════════════╗
║                    HPE MSA AI COMMAND GENERATOR                  ║
╚══════════════════════════════════════════════════════════════════╝

MODES:
  🔵 Simulation - Safe testing (generates but doesn't execute)
  🔴 Live - Connects and executes on real array

CONNECTION:
  1. Switch to Live Mode
  2. Click "Connect to Array"
  3. Enter: Host, Username, Password
  4. System fetches array info and disk inventory

COMMANDS:
  • create disk group with raid 5 using 4 HDDs
  • create 3 volumes of 100GB in pool a
  • expand volume myvol size 50GB
  • show disks, show volumes, show disk groups

OUTPUT FORMATS:
  • Formatted - Shows parsed, human-readable output
  • Raw XML - Shows complete XML response from array

WORKFLOW:
  1. Enter command → 2. Generate → 3. Execute → 4. See results
"""
        self.output_box.insert(tk.END, help_text, "success")
        self.output_box.see(tk.END)


def main():
    root = tk.Tk()
    app = MSACommandGeneratorUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()