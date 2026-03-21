"""
Enhanced MSA XML Response Parser
Properly parses show disks, show volumes, and other MSA commands
"""
import xml.etree.ElementTree as ET
import re


class MSAResponseParser:
    """Parser for MSA array XML responses"""
    
    @staticmethod
    def parse_show_disks(xml_string):
        """
        Parse 'show disks' XML response
        Returns list of disk objects with relevant properties
        """
        try:
            root = ET.fromstring(xml_string)
            disks = []
            
            for obj in root.findall(".//OBJECT[@basetype='drives']"):
                disk = {}
                
                # Extract key properties
                for prop in obj.findall("PROPERTY"):
                    name = prop.get("name")
                    value = prop.text or ""
                    
                    # Map important properties
                    if name == "location":
                        disk["id"] = value
                        disk["location"] = value
                    elif name == "serial-number":
                        disk["serial"] = value
                    elif name == "vendor":
                        disk["vendor"] = value
                    elif name == "model":
                        disk["model"] = value
                    elif name == "architecture":
                        # HDD or SSD
                        disk["type"] = value.lower()
                    elif name == "usage":
                        # AVAIL, LEFTOVR, etc.
                        disk["status"] = "free" if value == "AVAIL" else "used"
                        disk["usage"] = value
                    elif name == "size":
                        disk["size"] = value
                    elif name == "health":
                        disk["health"] = value
                    elif name == "temperature":
                        disk["temperature"] = value
                    elif name == "storage-tier":
                        disk["tier"] = value
                    elif name == "disk-group":
                        disk["disk_group"] = value
                    elif name == "storage-pool-name":
                        disk["pool"] = value
                    elif name == "description":
                        disk["description"] = value
                
                # Ensure required fields exist
                if "id" in disk:
                    if "type" not in disk:
                        # Fallback: check description for SSD
                        desc = disk.get("description", "")
                        disk["type"] = "ssd" if "SSD" in desc.upper() else "hdd"
                    
                    if "status" not in disk:
                        disk["status"] = "unknown"
                    
                    disks.append(disk)
            
            return disks
            
        except Exception as e:
            print(f"Error parsing show disks XML: {e}")
            return []
    
    @staticmethod
    def parse_show_volumes(xml_string):
        """
        Parse 'show volumes' XML response
        Returns list of volume objects
        """
        try:
            root = ET.fromstring(xml_string)
            volumes = []
            
            for obj in root.findall(".//OBJECT[@basetype='volumes']"):
                volume = {}
                
                for prop in obj.findall("PROPERTY"):
                    name = prop.get("name")
                    value = prop.text or ""
                    
                    if name == "volume-name":
                        volume["name"] = value
                    elif name == "storage-pool-name":
                        volume["pool"] = value
                    elif name == "total-size":
                        volume["total_size"] = value
                    elif name == "allocated-size":
                        volume["allocated_size"] = value
                    elif name == "volume-type":
                        volume["type"] = value
                    elif name == "health":
                        volume["health"] = value
                    elif name == "health-reason":
                        volume["health_reason"] = value
                    elif name == "serial-number":
                        volume["serial"] = value
                
                if "name" in volume:
                    volumes.append(volume)
            
            return volumes
            
        except Exception as e:
            print(f"Error parsing show volumes XML: {e}")
            return []
    
    @staticmethod
    def format_volumes_table(volumes):
        """Format volumes as ASCII table"""
        if not volumes:
            return "No volumes found"
        
        lines = []
        lines.append("┌─────────────────┬──────┬──────────────┬──────────────┬────────┐")
        lines.append("│ Volume Name     │ Pool │ Total Size   │ Alloc Size   │ Health │")
        lines.append("├─────────────────┼──────┼──────────────┼──────────────┼────────┤")
        
        for vol in volumes:
            name = vol.get("name", "N/A")[:15].ljust(15)
            pool = vol.get("pool", "N/A")[:4].ljust(4)
            total = vol.get("total_size", "N/A")[:12].ljust(12)
            alloc = vol.get("allocated_size", "N/A")[:12].ljust(12)
            health = vol.get("health", "N/A")[:6].ljust(6)
            
            lines.append(f"│ {name} │ {pool} │ {total} │ {alloc} │ {health} │")
        
        lines.append("└─────────────────┴──────┴──────────────┴──────────────┴────────┘")
        
        return "\n".join(lines)
    
    @staticmethod
    def parse_command_response(xml_string):
        """
        Parse general command response and extract status
        Returns dict with status, message, and timestamp
        """
        try:
            root = ET.fromstring(xml_string)
            
            # Find status object
            status_obj = root.find(".//OBJECT[@basetype='status']")
            
            if status_obj is None:
                return {
                    "success": False,
                    "message": "No status in response",
                    "timestamp": None
                }
            
            response_type = None
            message = None
            timestamp = None
            return_code = None
            
            for prop in status_obj.findall("PROPERTY"):
                name = prop.get("name")
                value = prop.text or ""
                
                if name == "response-type":
                    response_type = value
                elif name == "response":
                    message = value
                elif name == "time-stamp":
                    timestamp = value
                elif name == "return-code":
                    return_code = value
            
            success = response_type == "Success" if response_type else False
            
            return {
                "success": success,
                "message": message or "No response message",
                "timestamp": timestamp,
                "return_code": return_code,
                "response_type": response_type
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error parsing response: {str(e)}",
                "timestamp": None
            }
    
    @staticmethod
    def parse_show_configuration(xml_string):
        """
        Parse 'show configuration' response for system info
        Returns dict with system information
        """
        try:
            root = ET.fromstring(xml_string)
            
            info = {
                "system_name": None,
                "model": None,
                "vendor": None,
                "version": None,
                "location": None
            }
            
            # Look for system objects
            for obj in root.findall(".//OBJECT"):
                basetype = obj.get("basetype", "")
                
                if basetype in ["system", "versions", "configuration"]:
                    for prop in obj.findall("PROPERTY"):
                        name = prop.get("name")
                        value = prop.text or ""
                        
                        if name == "system-name":
                            info["system_name"] = value
                        elif name == "product-id":
                            info["model"] = value
                        elif name == "vendor-name":
                            info["vendor"] = value
                        elif name == "sc-fw" or name == "bundle-version":
                            info["version"] = value
                        elif name == "system-location":
                            info["location"] = value
            
            return info
            
        except Exception as e:
            print(f"Error parsing configuration: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def format_disk_summary(disks):
        """
        Format disk list into human-readable summary
        """
        if not disks:
            return "No disks found"
        
        total = len(disks)
        free = len([d for d in disks if d.get("status") == "free"])
        used = total - free
        
        ssd_count = len([d for d in disks if d.get("type") == "ssd"])
        hdd_count = len([d for d in disks if d.get("type") == "hdd"])
        
        ssd_free = len([d for d in disks if d.get("type") == "ssd" and d.get("status") == "free"])
        hdd_free = len([d for d in disks if d.get("type") == "hdd" and d.get("status") == "free"])
        
        summary = f"""Disk Summary:
  Total Disks: {total}
  Used: {used}
  Available: {free}
  
  SSDs: {ssd_count} ({ssd_free} available)
  HDDs: {hdd_count} ({hdd_free} available)
"""
        return summary
    
    @staticmethod
    def format_disk_table(disks, max_display=20):
        """
        Format disk list as a table
        """
        if not disks:
            return "No disks found"
        
        lines = []
        lines.append("┌──────────┬──────────┬────────┬──────────┬─────────────┬────────┐")
        lines.append("│ Location │ Type     │ Status │ Vendor   │ Model       │ Health │")
        lines.append("├──────────┼──────────┼────────┼──────────┼─────────────┼────────┤")
        
        display_count = min(len(disks), max_display)
        
        for i, disk in enumerate(disks[:display_count]):
            location = disk.get("location", "N/A")[:8].ljust(8)
            dtype = disk.get("type", "N/A")[:8].upper().ljust(8)
            status = disk.get("usage", disk.get("status", "N/A"))[:8].ljust(8)
            vendor = disk.get("vendor", "N/A")[:8].ljust(8)
            model = disk.get("model", "N/A")[:11].ljust(11)
            health = disk.get("health", "N/A")[:6].ljust(6)
            
            lines.append(f"│ {location} │ {dtype} │ {status} │ {vendor} │ {model} │ {health} │")
        
        lines.append("└──────────┴──────────┴────────┴──────────┴─────────────┴────────┘")
        
        if len(disks) > max_display:
            lines.append(f"... and {len(disks) - max_display} more disks")
        
        return "\n".join(lines)