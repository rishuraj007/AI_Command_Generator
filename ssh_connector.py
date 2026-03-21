"""
SSH Connector for HPE MSA Arrays
Automatically uses real SSH if paramiko is installed, otherwise simulation
"""
import time
import re


class MSAConnector:
    """
    SSH connector for HPE MSA storage arrays
    Auto-detects paramiko and uses real SSH if available
    """
    
    def __init__(self, host, username, password, port=22):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.client = None
        self.shell = None
        self.connected = False
        
        # Try to import paramiko - if available, use real SSH
        try:
            import paramiko
            self.simulation_mode = False
            self.paramiko = paramiko
            print(f"[SSH] Paramiko detected - will use REAL SSH connection")
        except ImportError:
            self.simulation_mode = True
            self.paramiko = None
            print(f"[SSH] Paramiko not found - using SIMULATION mode")
            print(f"[SSH] Install with: pip install paramiko")
            # For simulation - load sample data
            self.simulation_responses = {}
            self._load_simulation_data()
    
    def _load_simulation_data(self):
        """Load sample responses for simulation mode"""
        # This is only used if paramiko is NOT installed
        self.simulation_responses["show disks"] = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<RESPONSE VERSION="L100" REQUEST="show disks">
<OBJECT basetype="drives" name="drive">
    <PROPERTY name="location">1.1</PROPERTY>
    <PROPERTY name="description">SSD SAS</PROPERTY>
    <PROPERTY name="architecture">SSD</PROPERTY>
    <PROPERTY name="usage">AVAIL</PROPERTY>
</OBJECT>
<OBJECT basetype="status" name="status">
    <PROPERTY name="response-type">Success</PROPERTY>
    <PROPERTY name="response">Command completed successfully.</PROPERTY>
</OBJECT>
</RESPONSE>'''
        
        self.simulation_responses["default"] = '''<?xml version="1.0" encoding="UTF-8"?>
<RESPONSE>
<OBJECT basetype="status" name="status">
    <PROPERTY name="response-type">Success</PROPERTY>
    <PROPERTY name="response">Command completed successfully.</PROPERTY>
</OBJECT>
</RESPONSE>'''
    
    def connect(self):
        """
        Establish SSH connection to MSA array
        Returns True on success, error message on failure
        """
        if self.simulation_mode:
            # Simulation mode - always succeeds
            print("[SSH SIMULATION] Simulating connection...")
            time.sleep(1)
            self.connected = True
            return True
        
        # REAL SSH CONNECTION
        try:
            print(f"[SSH] Connecting to {self.host}:{self.port}...")
            
            self.client = self.paramiko.SSHClient()
            self.client.set_missing_host_key_policy(self.paramiko.AutoAddPolicy())
            
            # Connect with SSH
            self.client.connect(
                hostname=self.host,
                username=self.username,
                password=self.password,
                port=self.port,
                timeout=15,
                look_for_keys=False,
                allow_agent=False
            )
            
            print(f"[SSH] Connected! Opening shell channel...")
            
            # Open interactive shell
            self.shell = self.client.invoke_shell()
            
            # Wait for shell to be ready and clear initial banner
            time.sleep(2)
            if self.shell.recv_ready():
                initial_output = self.shell.recv(8192).decode('utf-8', errors='ignore')
                print(f"[SSH] Initial banner received ({len(initial_output)} bytes)")
            
            self.connected = True
            print(f"[SSH] Connection established successfully!")
            return True
            
        except self.paramiko.AuthenticationException:
            return "Authentication failed - Invalid username or password"
        except self.paramiko.SSHException as e:
            return f"SSH error: {str(e)}"
        except Exception as e:
            return f"Connection failed: {str(e)}"
    
    def execute_command(self, command):
        """
        Execute command on MSA and return XML output
        Returns XML string response
        """
        if not self.connected:
            return "Not connected to array"
        
        if self.simulation_mode:
            # Simulation mode - return canned responses
            print(f"[SSH SIMULATION] Executing: {command}")
            time.sleep(1)
            
            cmd_lower = command.lower().strip()
            if "show disks" in cmd_lower:
                return self.simulation_responses.get("show disks", self.simulation_responses["default"])
            else:
                return self.simulation_responses.get("default")
        
        # REAL SSH EXECUTION
        try:
            if not self.shell:
                return "Shell not available"
            
            print(f"[SSH] Executing command: {command}")
            
            # Clear any pending output first
            while self.shell.recv_ready():
                self.shell.recv(8192)
                time.sleep(0.1)
            
            # Send command
            self.shell.send(command + '\n')
            time.sleep(0.5)  # Give command time to start
            
            # Read output
            output = ""
            max_wait = 15  # Maximum 15 seconds
            start_time = time.time()
            no_data_count = 0
            
            while time.time() - start_time < max_wait:
                if self.shell.recv_ready():
                    chunk = self.shell.recv(8192).decode('utf-8', errors='ignore')
                    output += chunk
                    no_data_count = 0
                    time.sleep(0.2)
                else:
                    no_data_count += 1
                    if no_data_count > 5 and output:  # No data for 1 second and we have output
                        break
                    time.sleep(0.2)
            
            print(f"[SSH] Received {len(output)} bytes")
            
            # Extract XML from output (MSA returns XML wrapped in other text)
            xml_output = self._extract_xml(output)
            
            if xml_output:
                print(f"[SSH] Extracted XML ({len(xml_output)} bytes)")
                return xml_output
            else:
                print(f"[SSH] Warning: No XML found in output")
                # Return the raw output if no XML found
                return output
            
        except Exception as e:
            error_msg = f"Execution error: {str(e)}"
            print(f"[SSH] {error_msg}")
            return error_msg
    
    def _extract_xml(self, text):
        """
        Extract XML response from MSA output
        MSA responses may include command echo and other text
        """
        # Look for XML starting with <?xml or <RESPONSE
        xml_start = text.find('<?xml')
        if xml_start == -1:
            xml_start = text.find('<RESPONSE')
        
        if xml_start == -1:
            return None
        
        # Find the end of XML
        xml_end = text.rfind('</RESPONSE>')
        if xml_end == -1:
            return None
        
        xml_end += len('</RESPONSE>')
        
        return text[xml_start:xml_end]
    
    def disconnect(self):
        """Close SSH connection"""
        if self.simulation_mode:
            print("[SSH SIMULATION] Disconnecting...")
            self.connected = False
            return True
        
        # REAL SSH DISCONNECT
        try:
            print("[SSH] Disconnecting...")
            if self.shell:
                self.shell.close()
            if self.client:
                self.client.close()
            self.connected = False
            print("[SSH] Disconnected successfully")
            return True
        except Exception as e:
            print(f"[SSH] Disconnect error: {str(e)}")
            return f"Disconnect error: {str(e)}"
    
    def is_connected(self):
        """Check if connection is active"""
        return self.connected