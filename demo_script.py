"""
DEMO SCRIPT for Client Presentations
HPE MSA AI Command Generator

This script provides a guided demonstration flow for showcasing
the AI command generator to clients.
"""

DEMO_SCENARIOS = {
    "1_basic_raid": {
        "title": "Basic RAID Configuration",
        "scenario": "IT admin needs to create a RAID 5 array for general file storage",
        "commands": [
            "show disks",
            "create disk group with raid 5 using 4 HDDs",
            "show disk groups"
        ],
        "talking_points": [
            "Natural language input - no need to remember exact syntax",
            "System validates disk availability automatically",
            "HPE-compliant command generated instantly"
        ]
    },
    
    "2_performance": {
        "title": "Performance-Oriented Storage",
        "scenario": "Database team needs fast storage with redundancy",
        "commands": [
            "I need fast storage for my database with 4 drives",
            "create raid 10 with 4 SSDs",
            "create 2 volumes of 500GB in pool a"
        ],
        "talking_points": [
            "AI understands workload requirements (database = performance)",
            "Automatically recommends RAID 10 for best IOPS",
            "Selects SSD drives without explicit specification"
        ]
    },
    
    "3_capacity": {
        "title": "Capacity-Optimized Storage",
        "scenario": "Backup team needs maximum storage capacity",
        "commands": [
            "create cheap storage for backups with 12 drives",
            "show volumes",
            "create volume 5TB in pool a"
        ],
        "talking_points": [
            "Keywords like 'cheap' and 'backup' guide disk selection",
            "Recommends HDD for cost-effective capacity",
            "Supports large volume sizes (TB scale)"
        ]
    },
    
    "4_error_prevention": {
        "title": "Intelligent Error Prevention",
        "scenario": "Show how AI prevents common configuration mistakes",
        "commands": [
            "create raid 5 with 2 disks",  # Error: too few disks
            "create raid 10 with 5 disks",  # Error: odd number
            "create raid 5 with 20 SSDs",  # Error: insufficient disks
        ],
        "talking_points": [
            "Validates RAID requirements before execution",
            "Provides helpful suggestions instead of cryptic errors",
            "Prevents costly misconfigurations"
        ]
    },
    
    "5_advanced": {
        "title": "Advanced Operations",
        "scenario": "Complete workflow from creation to mapping",
        "commands": [
            "create disk group raid 6 with 6 HDDs in pool a",
            "create 3 volumes of 1TB in pool a",
            "expand volume a_vol1 size 500GB",
            "map volume a_vol1 initiator 21:00:00:24:ff:47:00:00"
        ],
        "talking_points": [
            "End-to-end storage provisioning workflow",
            "Multiple operations in sequence",
            "Production-ready commands for immediate use"
        ]
    },
    
    "6_natural_language": {
        "title": "Natural Language Flexibility",
        "scenario": "Show how different phrasings produce same result",
        "commands": [
            "make me a raid 5 with 4 cheap drives",
            "create raid 5 disk group using 4 HDDs",
            "I want raid 5 storage with 4 capacity drives"
        ],
        "talking_points": [
            "Understands various ways of expressing same intent",
            "No need to memorize specific command syntax",
            "Reduces training time for new administrators"
        ]
    }
}


def print_demo_menu():
    """Print demonstration menu"""
    print("\n" + "="*70)
    print("HPE MSA AI COMMAND GENERATOR - DEMO SCENARIOS")
    print("="*70)
    
    for key, demo in DEMO_SCENARIOS.items():
        print(f"\n{key}. {demo['title']}")
        print(f"   Scenario: {demo['scenario']}")
    
    print("\n" + "="*70)


def show_demo(demo_key):
    """Display a specific demo scenario"""
    if demo_key not in DEMO_SCENARIOS:
        print("Invalid demo selection")
        return
    
    demo = DEMO_SCENARIOS[demo_key]
    
    print("\n" + "="*70)
    print(f"DEMO: {demo['title']}")
    print("="*70)
    print(f"\nScenario: {demo['scenario']}\n")
    
    print("COMMANDS TO DEMONSTRATE:")
    for i, cmd in enumerate(demo['commands'], 1):
        print(f"  {i}. {cmd}")
    
    print("\nTALKING POINTS:")
    for point in demo['talking_points']:
        print(f"  • {point}")
    
    print("\n" + "="*70)


def full_demo_script():
    """Print complete demo script for presentations"""
    print("\n" + "="*70)
    print("COMPLETE DEMO SCRIPT FOR CLIENT PRESENTATIONS")
    print("="*70)
    
    print("""
INTRODUCTION (2 minutes)
------------------------
"Today I'll show you how AI can simplify HPE MSA storage management.
Instead of memorizing complex CLI syntax, administrators can use
natural language to configure storage systems."

[Show GUI interface]

"Here's our AI-powered command generator. Notice the disk inventory
panel showing what's available in the system."
""")
    
    for key in sorted(DEMO_SCENARIOS.keys()):
        demo = DEMO_SCENARIOS[key]
        print(f"\n\nDEMO {key}: {demo['title']} (2-3 minutes)")
        print("-" * 70)
        print(f"Scenario: {demo['scenario']}\n")
        
        for i, cmd in enumerate(demo['commands'], 1):
            print(f"Command {i}: \"{cmd}\"")
        
        print("\nKey Points:")
        for point in demo['talking_points']:
            print(f"  • {point}")
    
    print("""

CONCLUSION (1 minute)
---------------------
"As you've seen, this AI layer:
  • Reduces training time for new administrators
  • Prevents configuration errors before they happen
  • Translates intent into production-ready commands
  • Works with existing HPE MSA infrastructure

The system can be extended with additional commands and integrated
with your existing workflows."

QUESTIONS & DISCUSSION
----------------------
[Be prepared to discuss:]
  • Integration with existing monitoring tools
  • API connectivity to live MSA systems
  • Custom command templates
  • Multi-system management
  • Audit logging and compliance
""")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "full":
            full_demo_script()
        elif sys.argv[1] == "menu":
            print_demo_menu()
        else:
            show_demo(sys.argv[1])
    else:
        print("\nUsage:")
        print("  python demo_script.py menu    - Show all demos")
        print("  python demo_script.py full    - Show complete presentation script")
        print("  python demo_script.py 1_basic_raid - Show specific demo")
        print("\nAvailable demos:")
        for key in sorted(DEMO_SCENARIOS.keys()):
            print(f"  {key}")
