from data import xml_data
from xml_parser import parse_xml
from command_engine import generate_command

# Parse XML once
disks = parse_xml(xml_data)

while True:
    user_input = input("\nEnter request (or exit): ")

    if user_input.lower() == "exit":
        break

    result = generate_command(user_input, disks)
    print(result)