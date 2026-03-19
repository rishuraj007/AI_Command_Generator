import re

def ai_interpret(user_input):
    user_input = user_input.lower()

    result = {
        "raid": None,
        "disk_type": None,
        "count": None,
        "group_type": None,
        "explanation": []
    }

    # -------- Disk type --------
    if "fast" in user_input or "performance" in user_input:
        result["disk_type"] = "ssd"
        result["explanation"].append("Detected 'fast/performance' → SSD")

    elif "cheap" in user_input or "capacity" in user_input:
        result["disk_type"] = "hdd"
        result["explanation"].append("Detected 'cheap/capacity' → HDD")

    # -------- DP+ --------
    if "dp+" in user_input:
        result["group_type"] = "msa-dp+"
        result["disk_type"] = "hdd"
        result["explanation"].append("Detected 'dp+' → MSA-DP+ disk group")

    # -------- RAID --------
    raid_match = re.search(r'raid[\s\-]*(\d+)', user_input)
    if raid_match:
        result["raid"] = raid_match.group(1)

    # -------- STRICT COUNT --------
    count_match = re.search(r'(\d+)\s*(drive|drives|disk|disks)', user_input)
    if count_match:
        result["count"] = int(count_match.group(1))
        result["explanation"].append(f"Detected count → {result['count']}")

    return result