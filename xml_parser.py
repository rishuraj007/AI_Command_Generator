import xml.etree.ElementTree as ET

def parse_xml(xml_string):
    root = ET.fromstring(xml_string)
    disks = []

    for obj in root.findall(".//OBJECT[@basetype='drives']"):
        disk = {"id": None, "type": None, "status": None}

        for prop in obj.findall("PROPERTY"):
            name = prop.get("name")
            value = prop.text

            if name == "location":
                disk["id"] = value

            elif name == "description":
                disk["type"] = "ssd" if "SSD" in value.upper() else "hdd"

            elif name == "usage":
                disk["status"] = "free" if value == "AVAIL" else "used"

        disks.append(disk)

    return disks
