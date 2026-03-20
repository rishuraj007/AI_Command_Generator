"""
HPE MSA AI Command Generator - CLI Interface
Enhanced with help system and command history
"""
from data import xml_data
from xml_parser import parse_xml
from command_engine import generate_command

# Parse XML once
disks = parse_xml(xml_data)

def show_help():
    """Display help information"""
    help_text = """
╔══════════════════════════════════════════════════════════════════╗
║          HPE MSA AI Command Generator - Help                     ║
╚══════════════════════════════════════════════════════════════════╝

DISK GROUP COMMANDS:
  • Create RAID disk group:
    "create disk group with raid 5 using 4 HDDs"
    "create raid 10 with 6 fast drives"
  
  • Create MSA-DP+ group:
    "create dp+ disk group with 12 HDDs"
  
  • Show disk groups:
    "show disk groups"

VOLUME COMMANDS:
  • Create volumes:
    "create 3 volumes of 100GB in pool a"
    "create volume 50GB in pool b"
  
  • Expand volume:
    "expand volume myvol size 50GB"
  
  • Delete volume:
    "delete volume myvol"
  
  • Map volume to host:
    "map volume myvol initiator 21:00:00:24:ff:47:00:00"
  
  • Show volumes:
    "show volumes"

SNAPSHOT COMMANDS:
  • Create snapshot:
    "create snapshot of volume myvol"
  
  • Show snapshots:
    "show snapshots"

GENERAL COMMANDS:
  • show disks
  • show pools
  • show system
  • help - Show this help
  • exit - Exit the program

TIPS:
  💡 Use natural language - the AI will interpret your intent
  💡 Be specific about disk types: SSD, HDD, fast, capacity
  💡 Specify pool names: pool a, pool b
  💡 Include disk counts: 4 disks, 6 drives
    """
    print(help_text)


def show_disk_summary(disks):
    """Show summary of available disks"""
    total = len(disks)
    free = len([d for d in disks if d['status'] == 'free'])
    used = total - free
    
    ssd_free = len([d for d in disks if d['type'] == 'ssd' and d['status'] == 'free'])
    hdd_free = len([d for d in disks if d['type'] == 'hdd' and d['status'] == 'free'])
    
    print("\n" + "="*70)
    print("DISK INVENTORY SUMMARY")
    print("="*70)
    print(f"Total Disks: {total} | Used: {used} | Free: {free}")
    print(f"Available SSDs: {ssd_free} | Available HDDs: {hdd_free}")
    print("="*70 + "\n")


def main():
    print("\n" + "="*70)
    print("    HPE MSA AI Command Generator")
    print("    Type 'help' for commands, 'exit' to quit")
    print("="*70)
    
    show_disk_summary(disks)
    
    command_history = []
    
    while True:
        try:
            user_input = input("\n🤖 Enter command: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == "exit":
                print("\n👋 Goodbye!\n")
                break
            
            if user_input.lower() == "help":
                show_help()
                continue
            
            if user_input.lower() == "disks":
                show_disk_summary(disks)
                continue
            
            # Generate command
            result = generate_command(user_input, disks)
            
            # Display result
            print("\n" + "-"*70)
            if "❌" in result or "❗" in result:
                print("❌ ERROR:")
                print(result)
            elif "⚠️" in result:
                print("⚠️  WARNING:")
                print(result)
            else:
                print("✅ GENERATED COMMAND:")
                print(result)
                command_history.append({
                    "input": user_input,
                    "output": result
                })
            print("-"*70)
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}\n")


if __name__ == "__main__":
    main()
