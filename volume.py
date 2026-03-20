"""
Volume Operations
Handles creation, expansion, and management of volumes with HPE-compliant syntax
"""
from validators import ValidationError, InputValidator


def create_volume(volume_requests):
    """
    Create one or more volumes
    
    Official HPE syntax:
    create volume size <size> pool <pool> name <name> [tier optimize|standard|archive]
    """
    commands = []
    
    # Validate all requests first
    for req in volume_requests:
        InputValidator.validate_pool(req["pool"])
        InputValidator.validate_size(req["size"])
        InputValidator.validate_volume_count(req["count"])
    
    # Generate commands
    for req in volume_requests:
        count = req["count"]
        size = InputValidator.validate_size(req["size"])  # Normalize size format
        pool = req["pool"]
        tier = req.get("tier", None)  # Optional tier specification

        for i in range(1, count + 1):
            # Generate unique volume name
            name = f"{pool}_vol{i}"
            
            # Basic command
            cmd = f"create volume size {size} pool {pool} name {name}"
            
            # Add tier if specified
            if tier:
                cmd += f" tier {tier}"
            
            commands.append(cmd)

    return "\n".join(commands)


def expand_volume(volume_name, size):
    """
    Expand an existing volume
    
    Official HPE syntax:
    expand volume <volume-name> size <size>
    """
    InputValidator.validate_volume_name(volume_name)
    size = InputValidator.validate_size(size)
    
    return f"expand volume {volume_name} size {size}"


def delete_volume(volume_name):
    """
    Delete a volume
    
    Official HPE syntax:
    delete volumes <volume-name>
    """
    InputValidator.validate_volume_name(volume_name)
    return f"delete volumes {volume_name}"


def map_volume(volume_name, host_initiator, access="rw", lun="auto"):
    """
    Map volume to host for access
    
    Official HPE syntax:
    map volume <volume> access <rw|ro> lun <auto|N> initiator <wwn|iqn>
    
    Args:
        volume_name: Name of the volume to map
        host_initiator: Host WWN or iSCSI IQN
        access: 'rw' (read-write) or 'ro' (read-only)
        lun: LUN number or 'auto' for automatic assignment
    """
    InputValidator.validate_volume_name(volume_name)
    
    if access not in ["rw", "ro"]:
        raise ValidationError(
            f"❌ Invalid access mode: {access}",
            suggestions=["Use 'rw' for read-write or 'ro' for read-only"]
        )
    
    return f"map volume {volume_name} access {access} lun {lun} initiator {host_initiator}"


def unmap_volume(volume_name, host_initiator):
    """
    Unmap volume from host
    
    Official HPE syntax:
    unmap volume <volume> initiator <wwn|iqn>
    """
    InputValidator.validate_volume_name(volume_name)
    return f"unmap volume {volume_name} initiator {host_initiator}"


def show_volumes(pool=None):
    """
    Show volume information
    
    Official HPE syntax:
    show volumes [pool <pool-name>]
    """
    if pool:
        InputValidator.validate_pool(pool)
        return f"show volumes pool {pool}"
    
    return "show volumes"


def set_volume_tier(volume_name, tier):
    """
    Set volume tiering optimization
    
    Official HPE syntax:
    set volume <volume-name> tier <optimize|standard|archive>
    
    Args:
        tier: optimize (SSD tier), standard (mixed), archive (HDD tier)
    """
    InputValidator.validate_volume_name(volume_name)
    
    valid_tiers = ["optimize", "standard", "archive"]
    if tier not in valid_tiers:
        raise ValidationError(
            f"❌ Invalid tier: {tier}",
            suggestions=[f"Valid tiers: {', '.join(valid_tiers)}"]
        )
    
    return f"set volume {volume_name} tier {tier}"


def create_snapshot(volume_name, snapshot_name=None):
    """
    Create volume snapshot
    
    Official HPE syntax:
    create snapshot <volume-name> <snapshot-name>
    """
    InputValidator.validate_volume_name(volume_name)
    
    if snapshot_name:
        InputValidator.validate_volume_name(snapshot_name)
    else:
        # Generate snapshot name
        from datetime import datetime
        snapshot_name = f"{volume_name}_snap_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    return f"create snapshot {volume_name} {snapshot_name}"


def delete_snapshot(snapshot_name):
    """
    Delete a snapshot
    
    Official HPE syntax:
    delete snapshot <snapshot-name>
    """
    InputValidator.validate_volume_name(snapshot_name)
    return f"delete snapshot {snapshot_name}"


def show_snapshots(volume_name=None):
    """
    Show snapshot information
    
    Official HPE syntax:
    show snapshots [<volume-name>]
    """
    if volume_name:
        InputValidator.validate_volume_name(volume_name)
        return f"show snapshots {volume_name}"
    
    return "show snapshots"
