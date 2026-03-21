"""
MSA XML Response Parser
Parses HPE MSA XML outputs and extracts relevant information
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
    def parse_whoami(xml_string):
        """
        Parse 'show configuration' or whoami-like response
        Returns dict with user and system information
        """
        try:
            root = ET.fromstring(xml_string)
            
            info = {
                "username": None,
                "system_name": None,
                "model": None,
                "version": None
            }
            
            # Try to extract from various possible locations
            for obj in root.findall(".//OBJECT"):
                for prop in obj.findall("PROPERTY"):
                    name = prop.get("name")
                    value = prop.text or ""
                    
                    if name == "system-name":
                        info["system_name"] = value
                    elif name == "product-id":
                        info["model"] = value
                    elif name == "sc-fw":
                        info["version"] = value
            
            return info
            
        except Exception as e:
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
        
        summary = f"""
Disk Summary:
  Total Disks: {total}
  Used: {used}
  Available: {free}
  
  SSDs: {ssd_count} ({ssd_free} available)
  HDDs: {hdd_count} ({hdd_free} available)
"""
        return summary
    
    @staticmethod
    def format_disk_table(disks, max_display=10):
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