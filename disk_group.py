"""
Disk Group Operations
Handles creation and management of disk groups with HPE-compliant syntax
"""
from validators import ValidationError, InputValidator


def select_disks(disks, disk_type, count, allow_mixed=False):
    """
    Select appropriate disks for disk group creation
    
    Args:
        disks: List of available disks
        disk_type: 'ssd' or 'hdd'
        count: Number of disks needed
        allow_mixed: Allow mixing disk capacities (not recommended)
    
    Returns:
        List of disk IDs or raises ValidationError
    """
    if not disk_type:
        raise ValidationError(
            "❌ Disk type not specified",
            suggestions=["Specify disk type: SSD or HDD"]
        )

    # Filter matching disks
    matching = [
        d for d in disks
        if d["status"] == "free" and d["type"] == disk_type
    ]

    # Check availability
    if len(matching) == 0:
        raise ValidationError(
            f"❌ No available {disk_type.upper()} disks found",
            suggestions=["Check disk availability with: show disks"]
        )

    if len(matching) < count:
        available_ids = [d['id'] for d in matching]
        raise ValidationError(
            f"❌ Insufficient {disk_type.upper()} disks: need {count}, available {len(matching)}",
            suggestions=[
                f"Available {disk_type.upper()} disks: {', '.join(available_ids)}",
                f"Try requesting {len(matching)} disks instead"
            ]
        )

    # Select disks
    selected = matching[:count]
    
    # TODO: Add capacity consistency checking
    # HPE recommends not mixing disks with capacity ratio > 2:1
    # Check for sector size consistency (512n vs 512e)
    
    return [d["id"] for d in selected]


def create_disk_group(disks, raid, count, disk_type, pool, group_type=None):
    """
    Create disk group with HPE-compliant syntax
    
    Official HPE syntax:
    - Standard RAID: add disk-group type virtual disks <list> pool <name> level r<N>
    - MSA-DP+: add disk-group type msa-dp+ pool <name> disks <list> [spare-capacity default|dedicated]
    """
    warnings = []
    
    # -------- Validation --------
    
    # Validate pool
    InputValidator.validate_pool(pool)
    
    # MSA-DP+ validation
    if group_type == "msa-dp+":
        InputValidator.validate_msa_dp_plus(count)
        # MSA-DP+ typically uses HDD
        if disk_type == "ssd":
            warnings.append("⚠️  MSA-DP+ is typically used with HDDs, not SSDs")
    
    # Standard RAID validation
    elif raid:
        InputValidator.validate_raid_level(raid)
        InputValidator.validate_disk_count(raid, count)
        
        # Check for optimal disk count
        optimal_suggestion = InputValidator.suggest_optimal_disk_count(raid, count)
        if optimal_suggestion:
            warnings.append(optimal_suggestion)
    
    else:
        raise ValidationError(
            "❌ Neither RAID level nor group type specified",
            suggestions=[
                "Specify RAID level: 0, 1, 5, 6, or 10",
                "Or specify group type: msa-dp+"
            ]
        )
    
    # -------- Disk Selection --------
    try:
        selected = select_disks(disks, disk_type, count)
    except ValidationError as e:
        raise e
    
    disk_str = ",".join(selected)
    
    # -------- Command Generation --------
    
    if group_type == "msa-dp+":
        # MSA-DP+ command format
        cmd = f"add disk-group type msa-dp+ pool {pool} disks {disk_str} spare-capacity default"
    else:
        # Standard RAID command format (HPE-compliant)
        cmd = f"add disk-group type virtual disks {disk_str} pool {pool} level r{raid}"
    
    # -------- Response with warnings --------
    if warnings:
        return "\n".join(warnings) + "\n✓ " + cmd
    
    return cmd


def delete_disk_group(disk_group_id, pool):
    """
    Delete a disk group
    
    Official HPE syntax: delete disk-group <disk-group-id> pool <pool-name>
    """
    InputValidator.validate_pool(pool)
    return f"delete disk-group {disk_group_id} pool {pool}"


def add_spare_disks(disk_ids):
    """
    Designate disks as global spares
    
    Official HPE syntax: add spares disks <disk-list>
    """
    if isinstance(disk_ids, list):
        disk_ids = ",".join(disk_ids)
    
    return f"add spares disks {disk_ids}"


def remove_spare_disks(disk_ids):
    """
    Remove disks from spare designation
    
    Official HPE syntax: remove spares disks <disk-list>
    """
    if isinstance(disk_ids, list):
        disk_ids = ",".join(disk_ids)
    
    return f"remove spares disks {disk_ids}"


def show_disk_groups(pool=None):
    """
    Show disk group information
    
    Official HPE syntax: show disk-groups [pool <pool-name>]
    """
    if pool:
        InputValidator.validate_pool(pool)
        return f"show disk-groups pool {pool}"
    
    return "show disk-groups"
