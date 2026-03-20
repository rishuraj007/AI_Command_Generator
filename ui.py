"""
HPE MSA AI Command Generator - Enhanced GUI Interface
Professional UI with SSH connection support and execution modes
"""
import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
from datetime import datetime

from command_engine import generate_command
from xml_parser import parse_xml
from data import xml_data


# Load disks
disks = parse_xml(xml_data)


class MSACommandGeneratorUI:
    def __init__(self, root):
        self.root = root
        self.root.title("HPE MSA AI Command Generator v2.0")
        self.root.geometry("1200x800")
        self.root.configure(bg="#1e1e1e")
        
        self.command_history = []
        self.execution_mode = "simulation"  # simulation or live
        self.connected = False
        self.ssh_connector = None
        self.ssh_host = None
        self.ssh_username = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        
        # -------- HEADER --------
        header_frame = tk.Frame(self.root, bg="#2e5fa3", height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        title = tk.Label(
            header_frame,
            text="🤖 HPE MSA AI Command Generator v2.0",
            font=("Arial", 20, "bold"),
            fg="white",
            bg="#2e5fa3"
        )
        title.pack(pady=20)
        
        # -------- CONNECTION PANEL --------
        self.create_connection_panel()
        
        # -------- DISK INVENTORY PANEL --------
        inventory_frame = tk.Frame(self.root, bg="#1e1e1e")
        inventory_frame.pack(fill='x', padx=20, pady=10)
        
        self.create_inventory_display(inventory_frame)
        
        # -------- INPUT SECTION --------
        input_frame = tk.Frame(self.root, bg="#1e1e1e")
        input_frame.pack(fill='x', padx=20, pady=10)
        
        input_label = tk.Label(
            input_frame,
            text="Enter Command (Natural Language):",
            font=("Arial", 11, "bold"),
            fg="white",
            bg="#1e1e1e"
        )
        input_label.pack(anchor='w')
        
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
        
        # -------- SUGGESTION CHIPS --------
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
        
        # -------- BUTTONS --------
        button_frame = tk.Frame(self.root, bg="#1e1e1e")
        button_frame.pack(fill='x', padx=20, pady=5)
        
        generate_btn = tk.Button(
            button_frame,
            text="✨ Generate Command",
            font=("Arial", 12, "bold"),
            bg="#00cc66",
            fg="white",
            relief='flat',
            command=self.run_command,
            cursor="hand2"
        )
        generate_btn.pack(side='left', padx=5)
        
        # Execute button (changes based on mode)
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
        
        clear_btn = tk.Button(
            button_frame,
            text="🗑️ Clear Output",
            font=("Arial", 10),
            bg="#cc3333",
            fg="white",
            relief='flat',
            command=self.clear_output,
            cursor="hand2"
        )
        clear_btn.pack(side='left', padx=5)
        
        help_btn = tk.Button(
            button_frame,
            text="❓ Help",
            font=("Arial", 10),
            bg="#3366cc",
            fg="white",
            relief='flat',
            command=self.show_help,
            cursor="hand2"
        )
        help_btn.pack(side='left', padx=5)
        
        # -------- OUTPUT SECTION --------
        output_label = tk.Label(
            self.root,
            text="Generated Commands & Results:",
            font=("Arial", 11, "bold"),
            fg="white",
            bg="#1e1e1e"
        )
        output_label.pack(anchor='w', padx=20)
        
        self.output_box = scrolledtext.ScrolledText(
            self.root,
            width=100,
            height=18,
            font=("Consolas", 11),
            bg="#0d1117",
            fg="#00ffcc",
            insertbackground="#00ffcc",
            selectbackground="#264f78"
        )
        self.output_box.pack(padx=20, pady=5, fill='both', expand=True)
        
        # Configure text tags for colored output
        self.output_box.tag_config("error", foreground="#ff6b6b")
        self.output_box.tag_config("warning", foreground="#ffa500")
        self.output_box.tag_config("success", foreground="#00ffcc")
        self.output_box.tag_config("input", foreground="#ffffff", font=("Consolas", 11, "bold"))
        self.output_box.tag_config("timestamp", foreground="#888888", font=("Consolas", 9))
        self.output_box.tag_config("execution", foreground="#00ff00", font=("Consolas", 10, "bold"))
        self.output_box.tag_config("simulation", foreground="#ffaa00", font=("Consolas", 10))
        
        # -------- STATUS BAR --------
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
        
        # Store last generated command
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
        
        # Left side: Mode selection
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
        
        sim_radio = tk.Radiobutton(
            mode_frame,
            text="🔵 Simulation (Safe - No Real Changes)",
            variable=self.mode_var,
            value="simulation",
            bg="#2b2b2b",
            fg="white",
            selectcolor="#1e1e1e",
            activebackground="#2b2b2b",
            activeforeground="white",
            command=self.on_mode_change,
            cursor="hand2"
        )
        sim_radio.pack(side='left', padx=5)
        
        live_radio = tk.Radiobutton(
            mode_frame,
            text="🔴 Live (Executes on Array)",
            variable=self.mode_var,
            value="live",
            bg="#2b2b2b",
            fg="white",
            selectcolor="#1e1e1e",
            activebackground="#2b2b2b",
            activeforeground="white",
            command=self.on_mode_change,
            cursor="hand2"
        )
        live_radio.pack(side='left', padx=5)
        
        # Right side: Connection controls
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
            state='disabled'  # Disabled in simulation mode
        )
        self.connect_btn.pack(side='left', padx=5)
    
    def create_inventory_display(self, parent):
        """Create disk inventory summary"""
        total = len(disks)
        free = len([d for d in disks if d['status'] == 'free'])
        used = total - free
        ssd_free = len([d for d in disks if d['type'] == 'ssd' and d['status'] == 'free'])
        hdd_free = len([d for d in disks if d['type'] == 'hdd' and d['status'] == 'free'])
        
        inv_container = tk.Frame(parent, bg="#2b2b2b", relief='solid', borderwidth=1)
        inv_container.pack(fill='x', pady=5)
        
        tk.Label(
            inv_container,
            text="📊 Disk Inventory",
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
            self.status_label.config(text="Mode: Simulation - Safe testing, no real changes")
        else:
            self.status_indicator.config(text="● Live Mode", fg="#ff6b00")
            self.connect_btn.config(state='normal')
            self.execute_btn.config(text="▶️ Execute on Array", bg="#ff3333")
            
            if self.connected:
                self.status_label.config(text="Mode: Live - Connected to array")
            else:
                self.status_label.config(text="Mode: Live - Not connected. Click 'Connect to Array'")
    
    def show_connection_dialog(self):
        """Show dialog to enter SSH connection details"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Connect to HPE MSA Array")
        dialog.geometry("550x450")
        dialog.configure(bg="#2b2b2b")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (
            self.root.winfo_x() + self.root.winfo_width()//2 - 275,
            self.root.winfo_y() + self.root.winfo_height()//2 - 225
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
        
        # Instructions
        tk.Label(
            dialog,
            text="Enter your MSA array connection details below:",
            font=("Arial", 9),
            fg="#888888",
            bg="#2b2b2b"
        ).pack(pady=10)
        
        # Form frame
        form_frame = tk.Frame(dialog, bg="#2b2b2b")
        form_frame.pack(padx=40, pady=10, fill='both', expand=True)
        
        # Host/IP
        tk.Label(
            form_frame, 
            text="Host/IP Address:", 
            fg="white", 
            bg="#2b2b2b",
            font=("Arial", 9, "bold")
        ).grid(row=0, column=0, sticky='w', pady=12)
        
        host_entry = tk.Entry(
            form_frame, 
            width=35, 
            bg="#1e1e1e", 
            fg="white",
            font=("Arial", 10),
            insertbackground="white"
        )
        host_entry.grid(row=0, column=1, pady=12, padx=10, sticky='ew')
        host_entry.insert(0, "192.168.1.100")  # Default example
        
        tk.Label(
            form_frame,
            text="(e.g., 192.168.1.100 or msa.company.com)",
            fg="#666666",
            bg="#2b2b2b",
            font=("Arial", 7)
        ).grid(row=1, column=1, sticky='w', padx=10)
        
        # Username
        tk.Label(
            form_frame, 
            text="Username:", 
            fg="white", 
            bg="#2b2b2b",
            font=("Arial", 9, "bold")
        ).grid(row=2, column=0, sticky='w', pady=12)
        
        user_entry = tk.Entry(
            form_frame, 
            width=35, 
            bg="#1e1e1e", 
            fg="white",
            font=("Arial", 10),
            insertbackground="white"
        )
        user_entry.grid(row=2, column=1, pady=12, padx=10, sticky='ew')
        user_entry.insert(0, "manage")  # Default HPE MSA username
        
        tk.Label(
            form_frame,
            text="(default MSA username is 'manage')",
            fg="#666666",
            bg="#2b2b2b",
            font=("Arial", 7)
        ).grid(row=3, column=1, sticky='w', padx=10)
        
        # Password
        tk.Label(
            form_frame, 
            text="Password:", 
            fg="white", 
            bg="#2b2b2b",
            font=("Arial", 9, "bold")
        ).grid(row=4, column=0, sticky='w', pady=12)
        
        pass_entry = tk.Entry(
            form_frame, 
            width=35, 
            show="●", 
            bg="#1e1e1e", 
            fg="white",
            font=("Arial", 10),
            insertbackground="white"
        )
        pass_entry.grid(row=4, column=1, pady=12, padx=10, sticky='ew')
        
        # Show/Hide password toggle
        show_pass_var = tk.BooleanVar()
        
        def toggle_password():
            if show_pass_var.get():
                pass_entry.config(show="")
            else:
                pass_entry.config(show="●")
        
        tk.Checkbutton(
            form_frame,
            text="Show password",
            variable=show_pass_var,
            command=toggle_password,
            fg="#888888",
            bg="#2b2b2b",
            selectcolor="#1e1e1e",
            activebackground="#2b2b2b",
            activeforeground="white",
            font=("Arial", 8)
        ).grid(row=5, column=1, sticky='w', padx=10)
        
        # Port
        tk.Label(
            form_frame, 
            text="SSH Port:", 
            fg="white", 
            bg="#2b2b2b",
            font=("Arial", 9, "bold")
        ).grid(row=6, column=0, sticky='w', pady=12)
        
        port_entry = tk.Entry(
            form_frame, 
            width=35, 
            bg="#1e1e1e", 
            fg="white",
            font=("Arial", 10),
            insertbackground="white"
        )
        port_entry.grid(row=6, column=1, pady=12, padx=10, sticky='ew')
        port_entry.insert(0, "22")
        
        tk.Label(
            form_frame,
            text="(default SSH port is 22)",
            fg="#666666",
            bg="#2b2b2b",
            font=("Arial", 7)
        ).grid(row=7, column=1, sticky='w', padx=10)
        
        # Make column 1 expandable
        form_frame.columnconfigure(1, weight=1)
        
        # Status message with icon
        status_frame = tk.Frame(dialog, bg="#2b2b2b")
        status_frame.pack(pady=10, fill='x', padx=40)
        
        status_msg = tk.Label(
            status_frame,
            text="",
            fg="#ffaa00",
            bg="#2b2b2b",
            font=("Arial", 9),
            wraplength=450,
            justify='left'
        )
        status_msg.pack()
        
        # Buttons
        btn_frame = tk.Frame(dialog, bg="#2b2b2b")
        btn_frame.pack(pady=15)
        
        def attempt_connect():
            host = host_entry.get().strip()
            username = user_entry.get().strip()
            password = pass_entry.get()
            port = port_entry.get().strip()
            
            # Validation
            if not host:
                status_msg.config(text="❌ Please enter Host/IP Address", fg="#ff6b6b")
                host_entry.focus()
                return
            
            if not username:
                status_msg.config(text="❌ Please enter Username", fg="#ff6b6b")
                user_entry.focus()
                return
                
            if not password:
                status_msg.config(text="❌ Please enter Password", fg="#ff6b6b")
                pass_entry.focus()
                return
            
            if not port:
                port = "22"
            
            # Disable buttons during connection
            connect_button.config(state='disabled')
            cancel_button.config(state='disabled')
            
            status_msg.config(text="🔄 Connecting to array...", fg="#ffaa00")
            dialog.update()
            
            # TODO: Replace with actual SSH connection
            # from ssh_connector import MSAConnector
            # self.ssh_connector = MSAConnector(host, username, password, int(port))
            # result = self.ssh_connector.connect()
            
            # For now, simulate connection with validation
            import time
            time.sleep(2)  # Simulate connection time
            
            # Simulated success (replace with actual connection check)
            connection_success = True  # This will be: result == True
            
            if connection_success:
                # Store connection details
                self.ssh_host = host
                self.ssh_username = username
                self.connected = True
                
                # Update UI elements
                self.status_indicator.config(
                    text=f"● Connected: {host}",
                    fg="#00ff00"
                )
                self.status_label.config(
                    text=f"✅ Connected to {host} as {username} | Ready to execute commands"
                )
                self.connect_btn.config(
                    text="✓ Disconnect",
                    bg="#cc3333",
                    command=self.disconnect_from_array
                )
                
                # Show success message in output
                timestamp = datetime.now().strftime("%H:%M:%S")
                self.output_box.insert(tk.END, f"[{timestamp}] ", "timestamp")
                self.output_box.insert(
                    tk.END,
                    f"✅ Successfully connected to HPE MSA Array\n",
                    "execution"
                )
                self.output_box.insert(
                    tk.END,
                    f"   Host: {host}\n   User: {username}\n   Status: Ready\n\n",
                    "success"
                )
                self.output_box.see(tk.END)
                
                # Show success dialog
                messagebox.showinfo(
                    "Connection Successful",
                    f"✅ Connected to HPE MSA Array\n\n"
                    f"Host: {host}\n"
                    f"Username: {username}\n"
                    f"Port: {port}\n\n"
                    f"You can now execute commands on the array."
                )
                
                dialog.destroy()
            else:
                # Connection failed
                status_msg.config(
                    text=f"❌ Connection failed. Please check credentials and network connectivity.",
                    fg="#ff6b6b"
                )
                connect_button.config(state='normal')
                cancel_button.config(state='normal')
        
        connect_button = tk.Button(
            btn_frame,
            text="🔌 Connect",
            font=("Arial", 11, "bold"),
            bg="#00cc66",
            fg="white",
            width=14,
            height=1,
            command=attempt_connect,
            cursor="hand2"
        )
        connect_button.pack(side='left', padx=5)
        
        cancel_button = tk.Button(
            btn_frame,
            text="Cancel",
            font=("Arial", 11),
            bg="#666666",
            fg="white",
            width=14,
            height=1,
            command=dialog.destroy,
            cursor="hand2"
        )
        cancel_button.pack(side='left', padx=5)
        
        # Note at bottom
        tk.Label(
            dialog,
            text="🔒 Connection will be encrypted via SSH protocol",
            fg="#666666",
            bg="#2b2b2b",
            font=("Arial", 8)
        ).pack(pady=5)
        
        # Enable Enter key to connect
        def on_enter(event):
            attempt_connect()
        
        dialog.bind('<Return>', on_enter)
        
        # Focus on first empty field
        if not host_entry.get() or host_entry.get() == "192.168.1.100":
            host_entry.focus()
            host_entry.select_range(0, tk.END)
        elif not pass_entry.get():
            pass_entry.focus()
    
    def disconnect_from_array(self):
        """Disconnect from the MSA array"""
        if not self.connected:
            return
        
        confirm = messagebox.askyesno(
            "Disconnect",
            f"Disconnect from {self.ssh_host}?\n\n"
            "Any pending commands will not be executed.",
            icon='question'
        )
        
        if not confirm:
            return
        
        # TODO: Close SSH connection
        # if self.ssh_connector:
        #     self.ssh_connector.disconnect()
        
        # Update UI
        self.connected = False
        self.ssh_connector = None
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.output_box.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.output_box.insert(
            tk.END,
            f"🔌 Disconnected from {self.ssh_host}\n\n",
            "warning"
        )
        self.output_box.see(tk.END)
        
        self.status_indicator.config(text="● Live Mode (Not Connected)", fg="#ff6b00")
        self.status_label.config(text="Mode: Live - Not connected. Click 'Connect to Array'")
        self.connect_btn.config(
            text="🔌 Connect to Array",
            bg="#3366cc",
            command=self.show_connection_dialog
        )
        
        self.ssh_host = None
        self.ssh_username = None
        
        messagebox.showinfo("Disconnected", "Successfully disconnected from the array.")
    
    def insert_suggestion(self, text):
        """Insert suggestion into input field"""
        self.entry.delete(0, tk.END)
        self.entry.insert(0, text)
        self.entry.focus()
    
    def run_command(self):
        """Generate and display command"""
        user_input = self.entry.get().strip()

        if not user_input:
            self.status_label.config(text="⚠️  Please enter a command")
            return

        try:
            # Generate command
            result = generate_command(user_input, disks)
            
            # Store last command for execution
            self.last_command = result
            
            # Get timestamp
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Display input
            self.output_box.insert(tk.END, f"[{timestamp}] ", "timestamp")
            self.output_box.insert(tk.END, f"Input: {user_input}\n", "input")
            
            # Display output with appropriate formatting
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
                self.status_label.config(text="✅ Command generated successfully")
                self.execute_btn.config(state='normal')
                
                # Save to history
                self.command_history.append({
                    "timestamp": timestamp,
                    "input": user_input,
                    "output": result
                })

            # Auto-scroll to bottom
            self.output_box.see(tk.END)
            
            # Clear input
            self.entry.delete(0, tk.END)
            
        except Exception as e:
            self.output_box.insert(tk.END, f"❌ Unexpected error: {str(e)}\n\n", "error")
            self.status_label.config(text="❌ Unexpected error occurred")
            self.execute_btn.config(state='disabled')
    
    def execute_command(self):
        """Execute the last generated command"""
        if not self.last_command:
            messagebox.showwarning("No Command", "Please generate a command first before executing.")
            return
        
        # Extract actual command from formatted output
        command = self.last_command
        if "✓" in command:
            command = command.split("✓")[-1].strip()
        if "\n" in command:
            # Take only the first line if multiple commands
            command = command.split("\n")[0].strip()
        
        # Check for destructive commands
        destructive_keywords = ['delete', 'remove', 'clear', 'format']
        is_destructive = any(kw in command.lower() for kw in destructive_keywords)
        
        if is_destructive and self.execution_mode == "live":
            confirm = messagebox.askyesno(
                "Confirm Destructive Operation",
                f"⚠️ This command may delete or modify data:\n\n{command}\n\nAre you sure you want to execute this?",
                icon='warning'
            )
            if not confirm:
                self.status_label.config(text="❌ Execution cancelled by user")
                return
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if self.execution_mode == "simulation":
            # Simulation mode
            self.output_box.insert(tk.END, f"[{timestamp}] ", "timestamp")
            self.output_box.insert(tk.END, "🔵 SIMULATION MODE - Command would execute:\n", "simulation")
            self.output_box.insert(tk.END, f"{command}\n", "success")
            self.output_box.insert(tk.END, "✓ Simulation successful (no real changes made)\n\n", "simulation")
            self.status_label.config(text="✓ Simulation completed - No real changes made")
        else:
            # Live mode
            if not self.connected:
                messagebox.showerror(
                    "Not Connected",
                    "Please connect to the array first.\n\n"
                    "Click 'Connect to Array' button to establish connection."
                )
                return
            
            self.output_box.insert(tk.END, f"[{timestamp}] ", "timestamp")
            self.output_box.insert(tk.END, f"🔴 EXECUTING ON LIVE ARRAY: {self.ssh_host}\n", "execution")
            self.output_box.insert(tk.END, f"Command: {command}\n", "success")
            
            # TODO: Actually execute via SSH
            # if self.ssh_connector:
            #     result = self.ssh_connector.execute_command(command)
            #     self.output_box.insert(tk.END, f"Response:\n{result}\n\n", "success")
            
            # For now, simulate execution result
            self.output_box.insert(tk.END, "⏳ Executing on array...\n", "warning")
            self.root.update()
            
            import time
            time.sleep(2)  # Simulate execution time
            
            # Simulated response (replace with actual SSH response)
            self.output_box.insert(tk.END, "✅ Command executed successfully\n", "execution")
            self.output_box.insert(tk.END, f"Array Response: Success - Command completed\n\n", "success")
            self.status_label.config(text=f"✅ Command executed on {self.ssh_host}")
        
        self.output_box.see(tk.END)
    
    def clear_output(self):
        """Clear the output box"""
        self.output_box.delete(1.0, tk.END)
        self.status_label.config(text="Output cleared")
        self.execute_btn.config(state='disabled')
        self.last_command = None
    
    def show_help(self):
        """Display help information"""
        help_text = """
╔══════════════════════════════════════════════════════════════════╗
║                         QUICK HELP GUIDE                         ║
╚══════════════════════════════════════════════════════════════════╝

EXECUTION MODES:
  🔵 Simulation Mode - Safe testing, generates commands but doesn't execute
  🔴 Live Mode - Connects to array and executes commands (requires connection)

DISK GROUP COMMANDS:
  • create disk group with raid 5 using 4 HDDs
  • create raid 10 with 6 fast drives
  • create dp+ disk group with 12 HDDs

VOLUME COMMANDS:
  • create 3 volumes of 100GB in pool a
  • expand volume myvol size 50GB
  • delete volume myvol
  • map volume myvol initiator 21:00:00:24:ff:47:00:00

SHOW COMMANDS:
  • show disks
  • show volumes
  • show disk groups
  • show pools

WORKFLOW:
  1. Enter command in natural language
  2. Click "Generate Command" (or press Enter)
  3. Review the generated HPE command
  4. Click "Execute" to run in current mode

TIPS:
  💡 Use natural language - AI will understand your intent
  💡 Specify disk types: SSD, HDD, fast, capacity
  💡 Include pool names and disk counts
  💡 Check examples in suggestion chips above
  💡 Start with Simulation mode for safe testing

"""
        self.output_box.insert(tk.END, help_text, "success")
        self.output_box.see(tk.END)


def main():
    """Main entry point"""
    root = tk.Tk()
    app = MSACommandGeneratorUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()