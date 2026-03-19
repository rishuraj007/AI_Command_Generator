import re
from disk_group import create_disk_group
from volume import create_volume, expand_volume
from ai_layer import ai_interpret


def detect_intent(user_input):
    user_input = user_input.lower()

    if "show" in user_input and "volume" in user_input:
        return "show_volumes"

    if "expand" in user_input and "volume" in user_input:
        return "expand_volume"

    if "show" in user_input and "disk" in user_input:
        return "show_disks"

    if "disk group" in user_input:
        return "disk_group"

    if "volume" in user_input:
        return "volume"

    return "unknown"


def parse_volume_requests(user_input):
    user_input = user_input.lower()
    requests = []

    pattern1 = r'(\d+)\s*volumes?.*?(\d+\s*(?:gb|tb)).*?pool\s*([a-z])'
    matches1 = re.findall(pattern1, user_input)

    for count, size, pool in matches1:
        requests.append({
            "count": int(count),
            "size": size,
            "pool": pool
        })

    pattern2 = r'(\d+\s*(?:gb|tb)).*?pool\s*([a-z])'
    matches2 = re.findall(pattern2, user_input)

    if matches2 and not requests:
        for size, pool in matches2:
            requests.append({
                "count": 1,
                "size": size,
                "pool": pool
            })

    pattern3 = r'(\d+)\s*volumes?.*?pool\s*([a-z]).*?(\d+\s*(?:gb|tb))'
    matches3 = re.findall(pattern3, user_input)

    if matches3 and not requests:
        for count, pool, size in matches3:
            requests.append({
                "count": int(count),
                "size": size,
                "pool": pool
            })

    return requests


def parse_expand_volume(user_input):
    name_match = re.search(r'volume\s+(\w+)', user_input)
    size_match = re.search(r'(\d+\s*(gb|tb))', user_input)

    name = name_match.group(1) if name_match else None
    size = size_match.group(1) if size_match else None

    return name, size


# 🔥 FIXED STRICT PARSER
def parse_input(user_input):
    user_input = user_input.lower()

    # RAID
    raid = None
    raid_match = re.search(r'raid[\s\-]*(\d+)', user_input)
    if raid_match:
        raid = raid_match.group(1)

    # STRICT COUNT (no RAID confusion)
    count = None
    count_match = re.search(r'(\d+)\s*(drive|drives|disk|disks)', user_input)
    if count_match:
        count = int(count_match.group(1))

    # Disk type
    disk_type = None
    if "ssd" in user_input:
        disk_type = "ssd"
    elif "hdd" in user_input:
        disk_type = "hdd"

    return raid, count, disk_type


def generate_command(user_input, disks):
    intent = detect_intent(user_input)

    # -------- SHOW --------
    if intent == "show_volumes":
        return "show volumes"

    if intent == "show_disks":
        return "show disks"

    # -------- EXPAND --------
    if intent == "expand_volume":
        name, size = parse_expand_volume(user_input)

        if not name or not size:
            return "❌ Could not understand expand request"

        return expand_volume(name, size)

    # -------- CREATE VOLUME --------
    if intent == "volume":
        volume_requests = parse_volume_requests(user_input)

        if volume_requests:
            return create_volume(volume_requests)

        return "❌ Could not understand volume request"

    # -------- DISK GROUP --------
    if intent == "disk_group":
        raid, count, disk_type = parse_input(user_input)

        ai_result = ai_interpret(user_input)
        group_type = ai_result.get("group_type")

        # ONLY override if None
        if disk_type is None:
            disk_type = ai_result["disk_type"]

        if count is None:
            count = ai_result["count"]

        if disk_type is None:
            disk_type = "hdd"

        if not raid and not group_type:
            return "❗ Please specify RAID or type"

        if count is None:
            return "❗ Please specify number of disks"

        return create_disk_group(
            disks,
            raid,
            count,
            disk_type,
            "a",
            group_type
        )

    return "❌ Unknown command"