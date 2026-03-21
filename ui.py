"""
HPE MSA AI Command Generator - FIXED VERSION
Works with real SSH and properly parses all responses
"""
import tkinter as tk
from tkinter import scrolledtext, messagebox
from datetime import datetime

from command_engine import generate_command
from xml_parser import parse_xml
from data import xml_data

# Use the FIXED versions
from ssh_connector import MSAConnector
from msa_parser import MSAResponseParser

# Load initial sample disks
disks = parse_xml(xml_data)


class MSACommandGeneratorUI:
    def __init__(self, root):
        self.root = root
        self.root.title("HPE MSA AI Command Generator v2.0 - FIXED")
        self.root.geometry("1200x850")
        self.root.configure(bg="#1e1e1e")
        
        self.command_history = []
        self.execution_mode = "simulation"
        self.connected = False
        self.ssh_connector = None
        self.ssh_host = None
        self.ssh_username = None
        self.array_info = {}
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
        
        # DISK INVENTORY PANEL
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
            "show volumes",
            "create raid 5 with 4 HDDs",
            "create 3 volumes of 100GB in pool a"
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
            font=("Consolas", 9),
            bg="#0d1117",
            fg="#00ffcc",
            insertbackground="#00ffcc",
            selectbackground="#264f78",
            wrap='none'
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
            text="🔵 Simulation",
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
            text="🔴 Live",
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
            self.status_label.config(text="Mode: Simulation")
        else:
            self.status_indicator.config(text="● Live Mode", fg="#ff6b00")
            self.connect_btn.config(state='normal')
            self.execute_btn.config(text="▶️ Execute on Array", bg="#ff3333")
            
            if self.connected:
                self.status_label.config(text=f"Mode: Live - Connected to {self.ssh_host}")
            else:
                self.status_label.config(text="Mode: Live - Click 'Connect to Array'")
    
    def show_connection_dialog(self):
        """Show connection dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Connect to HPE MSA Array")
        dialog.geometry("550x480")
        dialog.configure(bg="#2b2b2b")
        dialog.transient(self.root)
        dialog.grab_set()
        
        dialog.geometry("+%d+%d" % (
            self.root.winfo_x() + self.root.winfo_width()//2 - 275,
            self.root.winfo_y() + self.root.winfo_height()//2 - 240
        ))
        
        header = tk.Frame(dialog, bg="#3366cc", height=60)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="🔌 Connect to HPE MSA Array",
            font=("Arial", 14, "bold"),
            fg="white",
            bg="#3366cc"
        ).pack(pady=15)
        
        tk.Label(
            dialog,
            text="Enter your MSA array connection details:",
            font=("Arial", 9),
            fg="#888888",
            bg="#2b2b2b"
        ).pack(pady=10)
        
        form = tk.Frame(dialog, bg="#2b2b2b")
        form.pack(padx=40, pady=10, fill='both', expand=True)
        
        # Fields
        tk.Label(form, text="Host/IP:", fg="white", bg="#2b2b2b", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky='w', pady=10)
        host_entry = tk.Entry(form, width=35, bg="#1e1e1e", fg="white", font=("Arial", 10))
        host_entry.grid(row=0, column=1, pady=10, sticky='ew')
        host_entry.insert(0, "10.225.135.102")
        
        tk.Label(form, text="Username:", fg="white", bg="#2b2b2b", font=("Arial", 9, "bold")).grid(row=1, column=0, sticky='w', pady=10)
        user_entry = tk.Entry(form, width=35, bg="#1e1e1e", fg="white", font=("Arial", 10))
        user_entry.grid(row=1, column=1, pady=10, sticky='ew')
        user_entry.insert(0, "manage")
        
        tk.Label(form, text="Password:", fg="white", bg="#2b2b2b", font=("Arial", 9, "bold")).grid(row=2, column=0, sticky='w', pady=10)
        pass_entry = tk.Entry(form, width=35, show="●", bg="#1e1e1e", fg="white", font=("Arial", 10))
        pass_entry.grid(row=2, column=1, pady=10, sticky='ew')
        
        show_pass = tk.BooleanVar()
        tk.Checkbutton(
            form,
            text="Show password",
            variable=show_pass,
            command=lambda: pass_entry.config(show="" if show_pass.get() else "●"),
            fg="#888888",
            bg="#2b2b2b",
            selectcolor="#1e1e1e",
            font=("Arial", 8)
        ).grid(row=3, column=1, sticky='w')
        
        tk.Label(form, text="SSH Port:", fg="white", bg="#2b2b2b", font=("Arial", 9, "bold")).grid(row=4, column=0, sticky='w', pady=10)
        port_entry = tk.Entry(form, width=35, bg="#1e1e1e", fg="white", font=("Arial", 10))
        port_entry.grid(row=4, column=1, pady=10, sticky='ew')
        port_entry.insert(0, "22")
        
        form.columnconfigure(1, weight=1)
        
        status_msg = tk.Label(dialog, text="", fg="#ffaa00", bg="#2b2b2b", font=("Arial", 9), wraplength=450)
        status_msg.pack(pady=10)
        
        btn_frame = tk.Frame(dialog, bg="#2b2b2b")
        btn_frame.pack(pady=15)
        
        def attempt_connect():
            host = host_entry.get().strip()
            user = user_entry.get().strip()
            password = pass_entry.get()
            port = port_entry.get().strip() or "22"
            
            if not all([host, user, password]):
                status_msg.config(text="❌ Please fill all fields", fg="#ff6b6b")
                return
            
            connect_btn.config(state='disabled')
            cancel_btn.config(state='disabled')
            status_msg.config(text="🔄 Connecting to array...", fg="#ffaa00")
            dialog.update()
            
            self.ssh_connector = MSAConnector(host, user, password, int(port))
            result = self.ssh_connector.connect()
            
            if result is True:
                self.connected = True
                self.ssh_host = host
                self.ssh_username = user
                self.fetch_array_info()
                self.fetch_disk_inventory()
                dialog.destroy()
            else:
                status_msg.config(text=f"❌ {result}", fg="#ff6b6b")
                connect_btn.config(state='normal')
                cancel_btn.config(state='normal')
        
        connect_btn = tk.Button(btn_frame, text="🔌 Connect", font=("Arial", 11, "bold"), bg="#00cc66", fg="white", width=14, command=attempt_connect, cursor="hand2")
        connect_btn.pack(side='left', padx=5)
        
        cancel_btn = tk.Button(btn_frame, text="Cancel", font=("Arial", 11), bg="#666666", fg="white", width=14, command=dialog.destroy, cursor="hand2")
        cancel_btn.pack(side='left', padx=5)
        
        dialog.bind('<Return>', lambda e: attempt_connect())
        host_entry.focus()
    
    def fetch_array_info(self):
        """Fetch array information"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.output_box.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.output_box.insert(tk.END, "🔄 Fetching array information...\n", "info")
        self.output_box.see(tk.END)
        self.root.update()
        
        response = self.ssh_connector.execute_command("show configuration")
        array_data = MSAResponseParser.parse_show_configuration(response)
        
        self.array_info = array_data
        
        self.output_box.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.output_box.insert(tk.END, "✅ Connected to HPE MSA Array\n", "execution")
        self.output_box.insert(tk.END, f"   Host: {self.ssh_host}\n", "success")
        self.output_box.insert(tk.END, f"   User: {self.ssh_username}\n", "success")
        
        if array_data.get("system_name"):
            self.output_box.insert(tk.END, f"   System: {array_data['system_name']}\n", "success")
        if array_data.get("model"):
            self.output_box.insert(tk.END, f"   Model: {array_data['model']}\n", "success")
        if array_data.get("version"):
            self.output_box.insert(tk.END, f"   Firmware: {array_data['version']}\n", "success")
        if array_data.get("location"):
            self.output_box.insert(tk.END, f"   Location: {array_data['location']}\n", "success")
        
        self.output_box.insert(tk.END, "   Status: Ready\n\n", "success")
        self.output_box.see(tk.END)
        
        self.status_indicator.config(text=f"● Connected: {self.ssh_host}", fg="#00ff00")
        self.status_label.config(text=f"✅ Connected to {self.ssh_host}")
        self.connect_btn.config(text="✓ Disconnect", bg="#cc3333", command=self.disconnect_from_array)
        
        messagebox.showinfo(
            "Connected",
            f"✅ Connected to {array_data.get('model', 'MSA Array')}\n\n"
            f"System: {array_data.get('system_name', 'N/A')}\n"
            f"Host: {self.ssh_host}\n\n"
            f"Ready to execute commands!"
        )
    
    def fetch_disk_inventory(self):
        """Fetch disk inventory"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.output_box.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.output_box.insert(tk.END, "🔄 Fetching disk inventory...\n", "info")
        self.root.update()
        
        response = self.ssh_connector.execute_command("show disks")
        disks_data = MSAResponseParser.parse_show_disks(response)
        
        if disks_data:
            self.disks = disks_data
            self.create_inventory_display()
            
            summary = MSAResponseParser.format_disk_summary(disks_data)
            self.output_box.insert(tk.END, f"✅ Disk inventory updated\n{summary}\n", "info")
        
        self.output_box.see(tk.END)
    
    def disconnect_from_array(self):
        """Disconnect"""
        if not messagebox.askyesno("Disconnect", f"Disconnect from {self.ssh_host}?"):
            return
        
        if self.ssh_connector:
            self.ssh_connector.disconnect()
        
        self.connected = False
        self.status_indicator.config(text="● Live (Not Connected)", fg="#ff6b00")
        self.status_label.config(text="Disconnected")
        self.connect_btn.config(text="🔌 Connect", bg="#3366cc", command=self.show_connection_dialog)
    
    def insert_suggestion(self, text):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, text)
    
    def run_command(self):
        """Generate command"""
        user_input = self.entry.get().strip()
        if not user_input:
            return
        
        try:
            result = generate_command(user_input, self.disks)
            self.last_command = result
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            self.output_box.insert(tk.END, f"[{timestamp}] Input: {user_input}\n", "input")
            
            if "❌" in result or "❗" in result:
                self.output_box.insert(tk.END, f"{result}\n\n", "error")
                self.execute_btn.config(state='disabled')
                self.last_command = None
            else:
                self.output_box.insert(tk.END, f"✓ {result}\n\n", "success")
                self.execute_btn.config(state='normal')
            
            self.output_box.see(tk.END)
            self.entry.delete(0, tk.END)
        except Exception as e:
            self.output_box.insert(tk.END, f"❌ Error: {e}\n\n", "error")
    
    def execute_command(self):
        """Execute command"""
        if not self.last_command:
            return
        
        command = self.last_command
        if "✓" in command:
            command = command.split("✓")[-1].strip()
        if "\n" in command:
            command = command.split("\n")[0].strip()
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if self.execution_mode == "simulation":
            self.output_box.insert(tk.END, f"[{timestamp}] 🔵 SIMULATION\n", "simulation")
            self.output_box.insert(tk.END, f"Command: {command}\n✓ Simulated\n\n", "success")
        else:
            if not self.connected:
                messagebox.showerror("Not Connected", "Connect to array first")
                return
            
            self.output_box.insert(tk.END, f"[{timestamp}] 🔴 EXECUTING ON {self.ssh_host}\n", "execution")
            self.output_box.insert(tk.END, f"Command: {command}\n⏳ Executing...\n", "success")
            self.output_box.see(tk.END)
            self.root.update()
            
            response = self.ssh_connector.execute_command(command)
            
            # Check if this is a show volumes command
            if "show volumes" in command.lower():
                volumes = MSAResponseParser.parse_show_volumes(response)
                if volumes:
                    table = MSAResponseParser.format_volumes_table(volumes)
                    self.output_box.insert(tk.END, f"\n{table}\n\n", "info")
                else:
                    parsed = MSAResponseParser.parse_command_response(response)
                    self.output_box.insert(tk.END, f"{parsed['message']}\n\n", "info")
            elif self.output_format_var.get() == "raw":
                self.output_box.insert(tk.END, f"\n--- Raw Response ---\n{response[:2000]}\n\n", "info")
            else:
                parsed = MSAResponseParser.parse_command_response(response)
                status = "✅" if parsed["success"] else "❌"
                self.output_box.insert(tk.END, f"{status} {parsed['message']}\n\n", "execution")
        
        self.output_box.see(tk.END)
    
    def clear_output(self):
        self.output_box.delete(1.0, tk.END)


def main():
    root = tk.Tk()
    app = MSACommandGeneratorUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()