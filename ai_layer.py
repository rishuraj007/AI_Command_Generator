"""
AI Layer for Natural Language Processing
Interprets user input and extracts command parameters
"""
import re


def ai_interpret(user_input):
    """
    Enhanced AI interpretation with better keyword detection
    Returns structured dictionary of detected parameters
    """
    user_input_lower = user_input.lower()

    result = {
        "raid": None,
        "disk_type": None,
        "count": None,
        "group_type": None,
        "pool": None,
        "size": None,
        "volume_name": None,
        "workload_hints": [],
        "explanation": []
    }

    # -------- Workload Detection --------
    workload_keywords = {
        "database": ["database", "db", "sql", "oracle", "mysql", "postgres"],
        "backup": ["backup", "archive", "restore"],
        "video": ["video", "media", "streaming"],
        "general": ["file", "share", "nas"]
    }
    
    for workload, keywords in workload_keywords.items():
        if any(kw in user_input_lower for kw in keywords):
            result["workload_hints"].append(workload)

    # -------- Disk Type Detection --------
    # Explicit mentions
    if "ssd" in user_input_lower:
        result["disk_type"] = "ssd"
        result["explanation"].append("Detected explicit 'SSD'")
    elif "hdd" in user_input_lower:
        result["disk_type"] = "hdd"
        result["explanation"].append("Detected explicit 'HDD'")
    
    # Performance keywords → SSD
    elif any(kw in user_input_lower for kw in ["fast", "performance", "high speed", "quick", "speedy"]):
        result["disk_type"] = "ssd"
        result["explanation"].append("Detected performance keywords → SSD recommended")
    
    # Capacity keywords → HDD
    elif any(kw in user_input_lower for kw in ["cheap", "capacity", "storage", "large", "bulk", "archive"]):
        result["disk_type"] = "hdd"
        result["explanation"].append("Detected capacity keywords → HDD recommended")

    # -------- Group Type Detection --------
    if "dp+" in user_input_lower or "msa-dp+" in user_input_lower or "msadp" in user_input_lower:
        result["group_type"] = "msa-dp+"
        result["disk_type"] = "hdd"  # MSA-DP+ typically uses HDD
        result["explanation"].append("Detected 'DP+' → MSA-DP+ disk group")

    # -------- RAID Level Detection --------
    raid_match = re.search(r'raid[\s\-]*(\d+)', user_input_lower)
    if raid_match:
        result["raid"] = raid_match.group(1)
        result["explanation"].append(f"Detected RAID level → {result['raid']}")

    # -------- Disk Count Detection --------
    # Look for explicit count before drive/disk keywords
    count_match = re.search(r'(\d+)\s*(?:drive|drives|disk|disks)', user_input_lower)
    if count_match:
        result["count"] = int(count_match.group(1))
        result["explanation"].append(f"Detected disk count → {result['count']}")
    
    # Alternative patterns: "using 4" or "with 6"
    if result["count"] is None:
        alt_match = re.search(r'(?:using|with)\s+(\d+)', user_input_lower)
        if alt_match:
            result["count"] = int(alt_match.group(1))
            result["explanation"].append(f"Detected disk count → {result['count']}")

    # -------- Pool Detection --------
    # Single letter pool
    pool_match = re.search(r'pool\s+([a-z])\b', user_input_lower)
    if pool_match:
        result["pool"] = pool_match.group(1)
        result["explanation"].append(f"Detected pool → {result['pool']}")
    else:
        # Custom pool name
        pool_match = re.search(r'pool\s+([a-zA-Z0-9_-]+)', user_input)
        if pool_match:
            result["pool"] = pool_match.group(1)
            result["explanation"].append(f"Detected pool → {result['pool']}")

    # -------- Size Detection --------
    size_match = re.search(r'(\d+\s*(?:gb|tb|gib|tib|mb|mib))', user_input_lower)
    if size_match:
        result["size"] = size_match.group(1)
        result["explanation"].append(f"Detected size → {result['size']}")

    # -------- Volume Name Detection --------
    # Pattern: "volume <name>"
    volume_match = re.search(r'volume\s+([a-zA-Z0-9_-]+)', user_input)
    if volume_match:
        result["volume_name"] = volume_match.group(1)
        result["explanation"].append(f"Detected volume name → {result['volume_name']}")

    return result


def recommend_raid_by_workload(workload_hints, disk_count):
    """
    Provide intelligent RAID recommendations based on workload
    """
    recommendations = []
    
    if "database" in workload_hints:
        if disk_count >= 4:
            recommendations.append({
                "raid": "10",
                "reason": "RAID 10 provides best performance for databases (high IOPS)",
                "priority": "high"
            })
        recommendations.append({
            "raid": "5",
            "reason": "RAID 5 with SSDs offers balanced performance for databases",
            "priority": "medium"
        })
    
    if "backup" in workload_hints:
        if disk_count >= 12:
            recommendations.append({
                "raid": None,
                "type": "msa-dp+",
                "reason": "MSA-DP+ maximizes capacity for backup/archive workloads",
                "priority": "high"
            })
        if disk_count >= 4:
            recommendations.append({
                "raid": "6",
                "reason": "RAID 6 provides dual-parity protection for critical backups",
                "priority": "medium"
            })
    
    if "video" in workload_hints:
        recommendations.append({
            "raid": "5",
            "reason": "RAID 5 balances performance and capacity for video streaming",
            "priority": "high"
        })
    
    return recommendations


def detect_ambiguity(user_input):
    """
    Detect potentially ambiguous or conflicting parameters in user input
    """
    user_input_lower = user_input.lower()
    ambiguities = []
    
    # Multiple RAID levels mentioned
    raid_matches = re.findall(r'raid[\s\-]*(\d+)', user_input_lower)
    if len(raid_matches) > 1:
        ambiguities.append({
            "type": "multiple_raids",
            "message": f"⚠️  Multiple RAID levels detected: {', '.join(raid_matches)}",
            "suggestion": "Please specify which RAID level to use"
        })
    
    # Multiple disk counts mentioned
    count_matches = re.findall(r'(\d+)\s*(?:drive|drives|disk|disks)', user_input_lower)
    if len(count_matches) > 1:
        ambiguities.append({
            "type": "multiple_counts",
            "message": f"⚠️  Multiple disk counts detected: {', '.join(count_matches)}",
            "suggestion": "Clarify the number of disks to use"
        })
    
    # Both SSD and HDD mentioned
    if "ssd" in user_input_lower and "hdd" in user_input_lower:
        ambiguities.append({
            "type": "mixed_disk_types",
            "message": "⚠️  Both SSD and HDD mentioned",
            "suggestion": "Using HDD by default. Specify preferred disk type explicitly."
        })
    
    # Multiple pool names
    pool_matches = re.findall(r'pool\s+([a-z])', user_input_lower)
    if len(pool_matches) > 1:
        ambiguities.append({
            "type": "multiple_pools",
            "message": f"⚠️  Multiple pools detected: {', '.join(pool_matches)}",
            "suggestion": "Specify which pool to use"
        })
    
    return ambiguities
