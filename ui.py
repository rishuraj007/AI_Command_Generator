"""
HPE MSA AI Command Generator - GUI Interface
Professional UI with enhanced features for client demonstrations
"""
import tkinter as tk
from tkinter import scrolledtext, ttk
from datetime import datetime

from command_engine import generate_command
from xml_parser import parse_xml
from data import xml_data


# Load disks
disks = parse_xml(xml_data)


class MSACommandGeneratorUI:
    def __init__(self, root):
        self.root = root
        self.root.title("HPE MSA AI Command Generator")
        self.root.geometry("1000x700")
        self.root.configure(bg="#1e1e1e")
        
        self.command_history = []
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        
        # -------- HEADER --------
        header_frame = tk.Frame(self.root, bg="#2e5fa3", height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        title = tk.Label(
            header_frame,
            text="🤖 HPE MSA AI Command Generator",
            font=("Arial", 20, "bold"),
            fg="white",
            bg="#2e5fa3"
        )
        title.pack(pady=20)
        
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
                command=lambda s=suggestion: self.insert_suggestion(s)
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
            text="Generated Commands:",
            font=("Arial", 11, "bold"),
            fg="white",
            bg="#1e1e1e"
        )
        output_label.pack(anchor='w', padx=20)
        
        self.output_box = scrolledtext.ScrolledText(
            self.root,
            width=100,
            height=20,
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
        
        # -------- STATUS BAR --------
        status_frame = tk.Frame(self.root, bg="#2e5fa3", height=30)
        status_frame.pack(fill='x', side='bottom')
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            status_frame,
            text="Ready",
            font=("Arial", 9),
            fg="white",
            bg="#2e5fa3",
            anchor='w'
        )
        self.status_label.pack(fill='x', padx=10)
    
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
            
            # Get timestamp
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Display input
            self.output_box.insert(tk.END, f"[{timestamp}] ", "timestamp")
            self.output_box.insert(tk.END, f"Input: {user_input}\n", "input")
            
            # Display output with appropriate formatting
            if "❌" in result or "❗" in result:
                self.output_box.insert(tk.END, f"{result}\n\n", "error")
                self.status_label.config(text="❌ Error in command")
            elif "⚠️" in result:
                self.output_box.insert(tk.END, f"{result}\n\n", "warning")
                self.status_label.config(text="⚠️  Warning issued")
            else:
                self.output_box.insert(tk.END, f"✓ {result}\n\n", "success")
                self.status_label.config(text="✅ Command generated successfully")
                
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
    
    def clear_output(self):
        """Clear the output box"""
        self.output_box.delete(1.0, tk.END)
        self.status_label.config(text="Output cleared")
    
    def show_help(self):
        """Display help information"""
        help_text = """
╔══════════════════════════════════════════════════════════════════╗
║                         QUICK HELP GUIDE                         ║
╚══════════════════════════════════════════════════════════════════╝

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

TIPS:
  💡 Use natural language - AI will understand your intent
  💡 Specify disk types: SSD, HDD, fast, capacity
  💡 Include pool names and disk counts
  💡 Check examples in suggestion chips above

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
