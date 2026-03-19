def validate_raid(raid, count):
    rules = {
        "0": 1,
        "1": 2,
        "5": 3
    }

    if raid in rules:
        if count < rules[raid]:
            return f"❌ RAID {raid} requires minimum {rules[raid]} disks"

    return None


def select_disks(disks, disk_type, count):
    if not disk_type:
        return "❌ Disk type not specified (SSD/HDD required)"

    matching = [
        d for d in disks
        if d["status"] == "free" and d["type"] == disk_type
    ]

    if len(matching) < count:
        return f"❌ Only {len(matching)} {disk_type.upper()} disks available"

    return [d["id"] for d in matching[:count]]


def create_disk_group(disks, raid, count, disk_type, pool, group_type=None):
    # -------- RAID validation --------
    if group_type != "msa-dp+":
        error = validate_raid(raid, count)
        if error:
            return error

    selected = select_disks(disks, disk_type, count)

    if isinstance(selected, str):
        return selected

    disk_str = ",".join(selected)

    # -------- DP+ --------
    if group_type == "msa-dp+":
        return f"add disk-group type msa-dp+ pool {pool} disks {disk_str}"

    # -------- RAID --------
    return f"add disk-group disks {disk_str} pool {pool} level r{raid}"