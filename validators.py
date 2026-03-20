"""
HPE MSA Command Validators
Validates all inputs according to HPE MSA documentation standards
"""
import re


class ValidationError(Exception):
    """Custom exception for validation errors with suggestions"""
    def __init__(self, message, suggestions=None):
        self.message = message
        self.suggestions = suggestions or []
        super().__init__(self.message)


class InputValidator:
    """Centralized validation for all HPE MSA command parameters"""
    
    # HPE MSA supported RAID levels
    VALID_RAIDS = ["0", "1", "5", "6", "10"]
    VALID_POOLS = ["a", "b"]  # Can be extended with custom pool names
    VALID_DISK_TYPES = ["ssd", "hdd"]
    VALID_GROUP_TYPES = ["virtual", "msa-dp+"]
    
    # Regex patterns
    SIZE_PATTERN = r'^(\d+)\s*(b|kb|mb|gb|tb|kib|mib|gib|tib)$'
    VOLUME_NAME_PATTERN = r'^[a-zA-Z0-9_-]{1,32}$'
    POOL_NAME_PATTERN = r'^[a-zA-Z0-9_-]{1,16}$'
    
    # RAID requirements based on HPE documentation
    RAID_RULES = {
        "0": {"min": 1, "max": 16, "optimal": [2, 4, 8, 16]},
        "1": {"min": 2, "max": 2, "optimal": [2]},
        "5": {"min": 3, "max": 16, "optimal": [3, 5, 9]},  # Power of 2 + 1
        "6": {"min": 4, "max": 16, "optimal": [4, 6, 10]},  # Power of 2 + 2
        "10": {"min": 4, "max": 16, "optimal": [4, 6, 8, 10, 12]},  # Even numbers
    }
    
    @staticmethod
    def validate_raid_level(raid):
        """Validate RAID level is supported"""
        if raid not in InputValidator.VALID_RAIDS:
            raise ValidationError(
                f"❌ Invalid RAID level: {raid}",
                suggestions=[f"Valid RAID levels: {', '.join(InputValidator.VALID_RAIDS)}"]
            )
        return raid
    
    @staticmethod
    def validate_disk_count(raid, count):
        """Validate disk count for given RAID level"""
        if raid not in InputValidator.RAID_RULES:
            raise ValidationError(f"❌ Unknown RAID level: {raid}")
        
        rules = InputValidator.RAID_RULES[raid]
        
        # Check minimum
        if count < rules["min"]:
            raise ValidationError(
                f"❌ RAID {raid} requires minimum {rules['min']} disks, you specified {count}"
            )
        
        # Check maximum
        if count > rules["max"]:
            raise ValidationError(
                f"❌ RAID {raid} supports maximum {rules['max']} disks, you specified {count}"
            )
        
        # RAID 10 special validation - must be even
        if raid == "10" and count % 2 != 0:
            raise ValidationError(
                f"❌ RAID 10 requires even number of disks, you specified {count}",
                suggestions=["Use 4, 6, 8, 10, 12, 14, or 16 disks"]
            )
        
        return count
    
    @staticmethod
    def suggest_optimal_disk_count(raid, count):
        """Provide performance suggestions based on HPE best practices"""
        if raid not in InputValidator.RAID_RULES:
            return None
        
        optimal = InputValidator.RAID_RULES[raid]["optimal"]
        
        if count not in optimal:
            closest = min(optimal, key=lambda x: abs(x - count) if x <= count else float('inf'))
            return f"💡 For optimal performance, HPE recommends using {', '.join(map(str, optimal))} disks for RAID {raid}. Closest optimal: {closest}"
        
        return None
    
    @staticmethod
    def validate_pool(pool):
        """Validate pool name format"""
        if pool is None:
            return "a"  # Default pool
        
        if not re.match(InputValidator.POOL_NAME_PATTERN, pool):
            raise ValidationError(
                f"❌ Invalid pool name: {pool}",
                suggestions=["Pool names: 1-16 alphanumeric characters, underscore, or hyphen"]
            )
        return pool
    
    @staticmethod
    def validate_size(size_str):
        """Validate and normalize size format"""
        size_str = size_str.strip().lower()
        match = re.match(InputValidator.SIZE_PATTERN, size_str)
        
        if not match:
            raise ValidationError(
                f"❌ Invalid size format: {size_str}",
                suggestions=["Use format: 100GB, 5TB, 500GiB, etc."]
            )
        
        amount, unit = match.groups()
        amount = int(amount)
        
        # Convert to GB for range checking
        unit_multipliers = {
            'b': 1/(1024**3), 'kb': 1/(1024**2), 'mb': 1/1024, 'gb': 1, 'tb': 1024,
            'kib': 1/(1024**2), 'mib': 1/1024, 'gib': 1, 'tib': 1024
        }
        
        amount_gb = amount * unit_multipliers.get(unit, 1)
        
        # Validate reasonable ranges
        if amount_gb < 0.001:  # Less than 1MB
            raise ValidationError("❌ Size too small (minimum ~1MB)")
        
        if amount_gb > 100000:  # More than 100TB
            raise ValidationError("❌ Size exceeds maximum (100TB)")
        
        # Normalize to HPE format (uppercase, no space)
        return f"{amount}{unit.upper()}"
    
    @staticmethod
    def validate_volume_name(name):
        """Validate volume name format"""
        if not re.match(InputValidator.VOLUME_NAME_PATTERN, name):
            raise ValidationError(
                f"❌ Invalid volume name: {name}",
                suggestions=["Use alphanumeric, underscore, hyphen (max 32 chars)"]
            )
        return name
    
    @staticmethod
    def validate_disk_type(disk_type):
        """Validate disk type"""
        if disk_type not in InputValidator.VALID_DISK_TYPES:
            raise ValidationError(
                f"❌ Invalid disk type: {disk_type}",
                suggestions=[f"Valid types: {', '.join(InputValidator.VALID_DISK_TYPES)}"]
            )
        return disk_type
    
    @staticmethod
    def validate_msa_dp_plus(count):
        """Validate MSA-DP+ specific requirements"""
        if count < 12:
            raise ValidationError(
                f"❌ MSA-DP+ requires minimum 12 disks, you specified {count}",
                suggestions=["MSA-DP+ requires 12-128 disks"]
            )
        
        if count > 128:
            raise ValidationError(
                f"❌ MSA-DP+ supports maximum 128 disks, you specified {count}",
                suggestions=["MSA-DP+ requires 12-128 disks"]
            )
        
        return count
    
    @staticmethod
    def validate_volume_count(count):
        """Validate number of volumes to create"""
        if count < 1:
            raise ValidationError("❌ Volume count must be at least 1")
        
        if count > 100:
            raise ValidationError(
                "❌ Creating more than 100 volumes at once",
                suggestions=["Consider creating volumes in smaller batches"]
            )
        
        return count
