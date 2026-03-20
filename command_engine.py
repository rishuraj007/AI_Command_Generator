"""
Command Engine
Central orchestrator for parsing user input and generating HPE MSA commands
"""
import re
from ssh_connector import MSAConnector
class CommandExecutor:
    def __init__(self):
        self.connector = None
        self.connected = False
        self.simulation_mode = True  # Safe default
    
    def set_mode(self, simulation=True):
        """Toggle between simulation and live mode"""
        self.simulation_mode = simulation
    
    def connect_to_array(self, host, username, password):
        """Connect to MSA array"""
        self.connector = MSAConnector(host, username, password)
        result = self.connector.connect()
        
        if result is True:
            self.connected = True
            self.simulation_mode = False
            return "✅ Connected to MSA array"
        else:
            return f"❌ {result}"
    
    def execute(self, command):
        """Execute command (simulation or live)"""
        if self.simulation_mode:
            return f"[SIMULATION] Would execute: {command}"
        
        if not self.connected:
            return "❌ Not connected to array. Use simulation mode or connect first."
        
        # Execute on real array
        result = self.connector.execute_command(command)
        return result
    
from disk_group import (
    create_disk_group, delete_disk_group, add_spare_disks, 
    remove_spare_disks, show_disk_groups
)
from volume import (
    create_volume, expand_volume, delete_volume, map_volume, 
    unmap_volume, show_volumes, set_volume_tier, create_snapshot,
    delete_snapshot, show_snapshots
)
from ai_layer import ai_interpret, recommend_raid_by_workload, detect_ambiguity
from validators import ValidationError, InputValidator


def detect_intent(user_input):
    """
    Detect user intent from natural language input
    Enhanced with more command patterns
    """
    user_input_lower = user_input.lower()

    # -------- SHOW commands --------
    if "show" in user_input_lower:
        if "volume" in user_input_lower:
            return "show_volumes"
        if "disk" in user_input_lower and "group" in user_input_lower:
            return "show_disk_groups"
        if "disk" in user_input_lower:
            return "show_disks"
        if "pool" in user_input_lower:
            return "show_pools"
        if "snapshot" in user_input_lower:
            return "show_snapshots"
        if "system" in user_input_lower:
            return "show_system"
    
    # -------- DELETE commands --------
    if any(kw in user_input_lower for kw in ["delete", "remove"]):
        if "volume" in user_input_lower:
            return "delete_volume"
        if "disk" in user_input_lower and "group" in user_input_lower:
            return "delete_disk_group"
        if "snapshot" in user_input_lower:
            return "delete_snapshot"
        if "spare" in user_input_lower:
            return "remove_spare"
    
    # -------- VOLUME operations --------
    if "expand" in user_input_lower and "volume" in user_input_lower:
        return "expand_volume"
    
    if "map" in user_input_lower and "volume" in user_input_lower:
        return "map_volume"
    
    if "unmap" in user_input_lower and "volume" in user_input_lower:
        return "unmap_volume"
    
    if "snapshot" in user_input_lower:
        if "create" in user_input_lower:
            return "create_snapshot"
        return "show_snapshots"
    
    if "tier" in user_input_lower and "volume" in user_input_lower:
        return "set_volume_tier"
    
    # -------- DISK GROUP operations --------
    # Check disk group BEFORE volume to avoid false positives
    if "spare" in user_input_lower:
        return "add_spare"
    
    if any(kw in user_input_lower for kw in ["disk group", "disk-group", "diskgroup", "raid", "dp+"]):
        return "create_disk_group"
    
    # -------- VOLUME operations (after disk group check) --------
    if "volume" in user_input_lower or "create" in user_input_lower:
        return "create_volume"

    return "unknown"


def parse_volume_requests(user_input):
    """
    Parse volume creation requests from natural language
    Supports multiple patterns
    """
    user_input_lower = user_input.lower()
    requests = []

    # Pattern 1: "N volumes of SIZE in pool X"
    pattern1 = r'(\d+)\s*volumes?.*?(\d+\s*(?:gb|tb|gib|tib)).*?pool\s+([a-z0-9_-]+)'
    matches1 = re.findall(pattern1, user_input_lower)

    for count, size, pool in matches1:
        requests.append({
            "count": int(count),
            "size": size,
            "pool": pool
        })

    # Pattern 2: "volume SIZE in pool X" (single volume)
    if not requests:
        pattern2 = r'(\d+\s*(?:gb|tb|gib|tib)).*?pool\s+([a-z0-9_-]+)'
        matches2 = re.findall(pattern2, user_input_lower)

        for size, pool in matches2:
            requests.append({
                "count": 1,
                "size": size,
                "pool": pool
            })

    # Pattern 3: "N volumes in pool X of SIZE"
    if not requests:
        pattern3 = r'(\d+)\s*volumes?.*?pool\s+([a-z0-9_-]+).*?(\d+\s*(?:gb|tb|gib|tib))'
        matches3 = re.findall(pattern3, user_input_lower)

        for count, pool, size in matches3:
            requests.append({
                "count": int(count),
                "size": size,
                "pool": pool
            })

    return requests


def parse_expand_volume(user_input):
    """Parse volume expansion request"""
    # Volume name
    name_match = re.search(r'volume\s+([a-zA-Z0-9_-]+)', user_input.lower())
    # Size
    size_match = re.search(r'(\d+\s*(?:gb|tb|gib|tib))', user_input.lower())

    name = name_match.group(1) if name_match else None
    size = size_match.group(1) if size_match else None

    return name, size


def parse_delete_volume(user_input):
    """Parse volume deletion request"""
    name_match = re.search(r'volume\s+([a-zA-Z0-9_-]+)', user_input.lower())
    return name_match.group(1) if name_match else None


def parse_map_volume(user_input):
    """Parse volume mapping request"""
    volume_match = re.search(r'volume\s+([a-zA-Z0-9_-]+)', user_input.lower())
    
    # Try to find initiator (WWN or IQN)
    initiator_match = re.search(r'(?:initiator|host|wwn|iqn)\s+([a-zA-Z0-9:.-]+)', user_input.lower())
    
    volume = volume_match.group(1) if volume_match else None
    initiator = initiator_match.group(1) if initiator_match else None
    
    # Access mode
    access = "rw"  # default
    if "read-only" in user_input.lower() or "ro" in user_input.lower():
        access = "ro"
    
    return volume, initiator, access


def generate_command(user_input, disks):
    """
    Main command generation function with comprehensive error handling
    
    Args:
        user_input: Natural language command from user
        disks: List of available disks
    
    Returns:
        HPE MSA command string or error message with suggestions
    """
    try:
        # Detect ambiguities
        ambiguities = detect_ambiguity(user_input)
        ambiguity_warnings = []
        
        if ambiguities:
            for amb in ambiguities:
                ambiguity_warnings.append(amb["message"])
        
        # Detect intent
        intent = detect_intent(user_input)

        # -------- SHOW commands --------
        if intent == "show_volumes":
            ai_result = ai_interpret(user_input)
            pool = ai_result.get("pool")
            return show_volumes(pool)

        if intent == "show_disk_groups":
            ai_result = ai_interpret(user_input)
            pool = ai_result.get("pool")
            return show_disk_groups(pool)

        if intent == "show_disks":
            return "show disks"
        
        if intent == "show_pools":
            return "show pools"
        
        if intent == "show_snapshots":
            ai_result = ai_interpret(user_input)
            volume_name = ai_result.get("volume_name")
            return show_snapshots(volume_name)
        
        if intent == "show_system":
            return "show system"

        # -------- DELETE commands --------
        if intent == "delete_volume":
            volume_name = parse_delete_volume(user_input)
            
            if not volume_name:
                raise ValidationError(
                    "❌ Volume name not specified",
                    suggestions=["Example: delete volume myvolume"]
                )
            
            return delete_volume(volume_name)
        
        if intent == "delete_disk_group":
            # Parse disk group ID and pool
            dg_match = re.search(r'(?:disk.group|group)\s+([a-zA-Z0-9_-]+)', user_input.lower())
            ai_result = ai_interpret(user_input)
            pool = ai_result.get("pool", "a")
            
            if not dg_match:
                raise ValidationError(
                    "❌ Disk group ID not specified",
                    suggestions=["Example: delete disk-group dg_001 pool a"]
                )
            
            return delete_disk_group(dg_match.group(1), pool)
        
        if intent == "delete_snapshot":
            name_match = re.search(r'snapshot\s+([a-zA-Z0-9_-]+)', user_input.lower())
            
            if not name_match:
                raise ValidationError(
                    "❌ Snapshot name not specified",
                    suggestions=["Example: delete snapshot snap_001"]
                )
            
            return delete_snapshot(name_match.group(1))

        # -------- EXPAND volume --------
        if intent == "expand_volume":
            name, size = parse_expand_volume(user_input)

            if not name:
                raise ValidationError(
                    "❌ Volume name not specified",
                    suggestions=["Example: expand volume myvolume size 50GB"]
                )
            
            if not size:
                raise ValidationError(
                    "❌ Size not specified",
                    suggestions=["Example: expand volume myvolume size 50GB"]
                )

            return expand_volume(name, size)

        # -------- MAP volume --------
        if intent == "map_volume":
            volume, initiator, access = parse_map_volume(user_input)
            
            if not volume:
                raise ValidationError(
                    "❌ Volume name not specified",
                    suggestions=["Example: map volume myvol initiator 21:00:00:24:ff:47:00:00"]
                )
            
            if not initiator:
                raise ValidationError(
                    "❌ Host initiator (WWN/IQN) not specified",
                    suggestions=["Example: map volume myvol initiator 21:00:00:24:ff:47:00:00"]
                )
            
            return map_volume(volume, initiator, access)
        
        # -------- UNMAP volume --------
        if intent == "unmap_volume":
            volume, initiator, _ = parse_map_volume(user_input)
            
            if not volume or not initiator:
                raise ValidationError(
                    "❌ Volume name or initiator not specified",
                    suggestions=["Example: unmap volume myvol initiator 21:00:00:24:ff:47:00:00"]
                )
            
            return unmap_volume(volume, initiator)
        
        # -------- SET TIER --------
        if intent == "set_volume_tier":
            ai_result = ai_interpret(user_input)
            volume_name = ai_result.get("volume_name")
            
            # Detect tier
            tier = None
            if "optimize" in user_input.lower():
                tier = "optimize"
            elif "archive" in user_input.lower():
                tier = "archive"
            elif "standard" in user_input.lower():
                tier = "standard"
            
            if not volume_name or not tier:
                raise ValidationError(
                    "❌ Volume name or tier not specified",
                    suggestions=["Example: set volume myvol tier optimize"]
                )
            
            return set_volume_tier(volume_name, tier)
        
        # -------- CREATE SNAPSHOT --------
        if intent == "create_snapshot":
            ai_result = ai_interpret(user_input)
            volume_name = ai_result.get("volume_name")
            
            if not volume_name:
                raise ValidationError(
                    "❌ Volume name not specified",
                    suggestions=["Example: create snapshot of volume myvol"]
                )
            
            return create_snapshot(volume_name)

        # -------- CREATE VOLUME --------
        if intent == "create_volume":
            volume_requests = parse_volume_requests(user_input)

            if not volume_requests:
                raise ValidationError(
                    "❌ Could not parse volume request",
                    suggestions=[
                        "Example: create 3 volumes of 100GB in pool a",
                        "Example: create volume 50GB in pool b"
                    ]
                )

            return create_volume(volume_requests)

        # -------- ADD SPARE --------
        if intent == "add_spare":
            # Extract disk IDs
            disk_match = re.findall(r'(\d+\.\d+)', user_input)
            
            if not disk_match:
                raise ValidationError(
                    "❌ Disk IDs not specified",
                    suggestions=["Example: add spare disks 1.1,1.2,1.3"]
                )
            
            return add_spare_disks(disk_match)
        
        # -------- REMOVE SPARE --------
        if intent == "remove_spare":
            disk_match = re.findall(r'(\d+\.\d+)', user_input)
            
            if not disk_match:
                raise ValidationError(
                    "❌ Disk IDs not specified",
                    suggestions=["Example: remove spare disks 1.1,1.2"]
                )
            
            return remove_spare_disks(disk_match)

        # -------- CREATE DISK GROUP --------
        if intent == "create_disk_group":
            # Use AI interpretation
            ai_result = ai_interpret(user_input)
            
            raid = ai_result.get("raid")
            count = ai_result.get("count")
            disk_type = ai_result.get("disk_type")
            pool = ai_result.get("pool") or "a"  # Default to pool 'a' if None
            group_type = ai_result.get("group_type")

            # Validate we have required parameters
            if not raid and not group_type:
                raise ValidationError(
                    "❗ RAID level or group type not specified",
                    suggestions=[
                        "Example: create disk group with raid 5 using 4 HDDs",
                        "Example: create dp+ disk group with 12 HDDs"
                    ]
                )

            if count is None:
                raise ValidationError(
                    "❗ Number of disks not specified",
                    suggestions=["Example: using 4 disks", "with 6 drives"]
                )

            # Set default disk type if not detected
            if disk_type is None:
                disk_type = "hdd"  # Default to HDD

            # Generate command
            cmd = create_disk_group(disks, raid, count, disk_type, pool, group_type)
            
            # Add ambiguity warnings if any
            if ambiguity_warnings:
                return "\n".join(ambiguity_warnings) + "\n" + cmd
            
            return cmd

        # -------- UNKNOWN command --------
        raise ValidationError(
            "❌ Command not recognized",
            suggestions=[
                "Try: show volumes",
                "Try: create volume 100GB in pool a",
                "Try: create disk group with raid 5 using 4 HDDs",
                "Try: expand volume myvol size 50GB"
            ]
        )
    
    except ValidationError as e:
        # Format error message with suggestions
        error_msg = e.message
        if e.suggestions:
            error_msg += "\n💡 " + "\n💡 ".join(e.suggestions)
        return error_msg
    
    except Exception as e:
        # Catch unexpected errors
        return f"❌ Unexpected error: {str(e)}\n💡 Please check your command syntax"
