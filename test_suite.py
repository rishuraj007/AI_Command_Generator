"""
Test Suite for HPE MSA Command Generator
Tests all major functionality and edge cases
"""
from command_engine import generate_command
from xml_parser import parse_xml
from data import xml_data

# Load test data
disks = parse_xml(xml_data)


def test_command(description, user_input, expected_in_output=None):
    """Helper function to test commands"""
    print(f"\n{'='*70}")
    print(f"TEST: {description}")
    print(f"{'='*70}")
    print(f"Input: {user_input}")
    
    result = generate_command(user_input, disks)
    print(f"Output:\n{result}")
    
    if expected_in_output:
        if expected_in_output in result:
            print("✅ PASS")
        else:
            print(f"❌ FAIL - Expected '{expected_in_output}' in output")
    
    return result


def run_all_tests():
    """Run comprehensive test suite"""
    
    print("\n" + "="*70)
    print("HPE MSA COMMAND GENERATOR - TEST SUITE")
    print("="*70)
    
    # ========== DISK GROUP TESTS ==========
    print("\n\n" + "="*70)
    print("DISK GROUP CREATION TESTS")
    print("="*70)
    
    test_command(
        "Basic RAID 5 with 4 HDDs",
        "create disk group with raid 5 using 4 HDDs",
        "add disk-group type virtual"
    )
    
    test_command(
        "RAID 10 with SSDs",
        "create raid 10 with 4 fast drives",
        "r10"
    )
    
    test_command(
        "RAID 6 with 6 disks",
        "create disk group raid 6 with 6 HDDs",
        "r6"
    )
    
    test_command(
        "MSA-DP+ with 12 disks",
        "create dp+ disk group with 12 HDDs in pool a",
        "type msa-dp+"
    )
    
    # Edge cases
    test_command(
        "RAID 5 with insufficient disks (should error)",
        "create raid 5 with 2 disks",
        "❌"
    )
    
    test_command(
        "RAID 10 with odd number (should error)",
        "create raid 10 with 5 disks",
        "❌"
    )
    
    test_command(
        "MSA-DP+ with too few disks (should error)",
        "create dp+ with 8 disks",
        "❌"
    )
    
    # ========== VOLUME TESTS ==========
    print("\n\n" + "="*70)
    print("VOLUME CREATION TESTS")
    print("="*70)
    
    test_command(
        "Create single volume",
        "create volume 100GB in pool a",
        "create volume size 100GB"
    )
    
    test_command(
        "Create multiple volumes",
        "create 3 volumes of 50GB in pool b",
        "create volume size 50GB"
    )
    
    test_command(
        "Create volume with TB size",
        "create volume 5TB in pool a",
        "5TB"
    )
    
    # ========== VOLUME EXPANSION TESTS ==========
    print("\n\n" + "="*70)
    print("VOLUME EXPANSION TESTS")
    print("="*70)
    
    test_command(
        "Expand existing volume",
        "expand volume myvol size 100GB",
        "expand volume myvol"
    )
    
    test_command(
        "Expand without volume name (should error)",
        "expand volume size 50GB",
        "❌"
    )
    
    # ========== SHOW COMMANDS TESTS ==========
    print("\n\n" + "="*70)
    print("SHOW COMMANDS TESTS")
    print("="*70)
    
    test_command(
        "Show disks",
        "show disks",
        "show disks"
    )
    
    test_command(
        "Show volumes",
        "show volumes",
        "show volumes"
    )
    
    test_command(
        "Show disk groups",
        "show disk groups",
        "show disk-groups"
    )
    
    test_command(
        "Show pools",
        "show pools",
        "show pools"
    )
    
    # ========== DELETE COMMANDS TESTS ==========
    print("\n\n" + "="*70)
    print("DELETE COMMANDS TESTS")
    print("="*70)
    
    test_command(
        "Delete volume",
        "delete volume test_vol",
        "delete volumes test_vol"
    )
    
    # ========== MAP COMMANDS TESTS ==========
    print("\n\n" + "="*70)
    print("MAP/UNMAP VOLUME TESTS")
    print("="*70)
    
    test_command(
        "Map volume to host",
        "map volume myvol initiator 21:00:00:24:ff:47:00:00",
        "map volume myvol"
    )
    
    # ========== NATURAL LANGUAGE TESTS ==========
    print("\n\n" + "="*70)
    print("NATURAL LANGUAGE UNDERSTANDING TESTS")
    print("="*70)
    
    test_command(
        "Performance-oriented request",
        "I need fast storage for my database",
        "ssd"
    )
    
    test_command(
        "Capacity-oriented request",
        "Create cheap storage for backups with 12 drives",
        "hdd"
    )
    
    test_command(
        "Mixed language",
        "make me a raid 5 with 4 cheap drives in pool a",
        "r5"
    )
    
    # ========== ERROR HANDLING TESTS ==========
    print("\n\n" + "="*70)
    print("ERROR HANDLING TESTS")
    print("="*70)
    
    test_command(
        "No RAID specified (should error)",
        "create disk group with 4 disks",
        "❌"
    )
    
    test_command(
        "No disk count specified (should error)",
        "create raid 5 disk group",
        "❌"
    )
    
    test_command(
        "Invalid command (should error)",
        "do something random",
        "❌"
    )
    
    test_command(
        "Insufficient available disks (should error)",
        "create raid 5 with 20 SSDs",
        "❌"
    )
    
    print("\n\n" + "="*70)
    print("TEST SUITE COMPLETED")
    print("="*70 + "\n")


if __name__ == "__main__":
    run_all_tests()
