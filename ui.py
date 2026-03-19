import tkinter as tk
from tkinter import scrolledtext

from command_engine import generate_command
from xml_parser import parse_xml
from data import xml_data


# Load disks
disks = parse_xml(xml_data)


def extract_command(result):
    """
    Extract only the final command line from output
    """
    lines = result.strip().split("\n")

    # Return last non-empty line
    for line in reversed(lines):
        if line.strip():
            return line

    return result


def run_command():
    user_input = entry.get()

    if not user_input.strip():
        output_box.insert(tk.END, "❗ Please enter a command\n\n")
        return

    result = generate_command(user_input, disks)

    # 🔥 Only show command
    command_only = extract_command(result)

    output_box.insert(tk.END, f"> {user_input}\n")
    output_box.insert(tk.END, f"{command_only}\n\n")

    entry.delete(0, tk.END)


# -------- UI --------
root = tk.Tk()
root.title("AI Command Generator")
root.geometry("700x500")
root.configure(bg="#1e1e1e")

title = tk.Label(
    root,
    text="AI-Based MSA Command Generator",
    font=("Arial", 16, "bold"),
    fg="white",
    bg="#1e1e1e"
)
title.pack(pady=10)

entry = tk.Entry(
    root,
    width=80,
    font=("Arial", 12)
)
entry.pack(pady=10)

submit_btn = tk.Button(
    root,
    text="Generate Command",
    font=("Arial", 12, "bold"),
    bg="#2e5fa3",
    fg="white",
    command=run_command
)
submit_btn.pack(pady=5)

output_box = scrolledtext.ScrolledText(
    root,
    width=80,
    height=20,
    font=("Consolas", 11),
    bg="#121212",
    fg="#00ffcc"
)
output_box.pack(pady=10)

root.mainloop()