"""
SSH Connector for HPE MSA Arrays
Handles SSH connection and command execution
"""
import time


class MSAConnector:
    """
    SSH connector for HPE MSA storage arrays
    
    Note: This is a simulation mode connector. For production use:
    1. Install paramiko: pip install paramiko
    2. Uncomment the paramiko import and implementation
    3. Remove the simulation code
    """
    
    def __init__(self, host, username, password, port=22):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.client = None
        self.shell = None
        self.connected = False
        self.simulation_mode = True  # Set to False when using real SSH
        
        # For simulation - load sample data
        self.simulation_responses = {}
        self._load_simulation_data()
    
    def _load_simulation_data(self):
        """Load sample responses for simulation mode"""
        # Sample show disks response (truncated for demo)
        self.simulation_responses["show disks"] = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<RESPONSE VERSION="L100" REQUEST="show disks">
<OBJECT basetype="drives" name="drive">
    <PROPERTY name="location">1.1</PROPERTY>
    <PROPERTY name="description">SSD SAS</PROPERTY>
    <PROPERTY name="architecture">SSD</PROPERTY>
    <PROPERTY name="usage">AVAIL</PROPERTY>
    <PROPERTY name="vendor">SEAGATE</PROPERTY>
    <PROPERTY name="model">ST1200MM0108</PROPERTY>
    <PROPERTY name="health">OK</PROPERTY>
</OBJECT>
<OBJECT basetype="drives" name="drive">
    <PROPERTY name="location">1.2</PROPERTY>
    <PROPERTY name="description">HDD SAS</PROPERTY>
    <PROPERTY name="architecture">HDD</PROPERTY>
    <PROPERTY name="usage">USED</PROPERTY>
    <PROPERTY name="vendor">SEAGATE</PROPERTY>
    <PROPERTY name="model">ST1200MM0108</PROPERTY>
    <PROPERTY name="health">OK</PROPERTY>
</OBJECT>
<OBJECT basetype="status" name="status">
    <PROPERTY name="response-type">Success</PROPERTY>
    <PROPERTY name="response">Command completed successfully.</PROPERTY>
    <PROPERTY name="return-code">0</PROPERTY>
</OBJECT>
</RESPONSE>'''
        
        # Sample show configuration response
        self.simulation_responses["show configuration"] = '''<?xml version="1.0" encoding="UTF-8"?>
<RESPONSE VERSION="L100" REQUEST="show configuration">
<OBJECT basetype="system" name="system">
    <PROPERTY name="system-name">MSA-DEMO-ARRAY</PROPERTY>
    <PROPERTY name="product-id">MSA 2050</PROPERTY>
    <PROPERTY name="sc-fw">GL250R014</PROPERTY>
    <PROPERTY name="vendor-name">HPE</PROPERTY>
</OBJECT>
<OBJECT basetype="status" name="status">
    <PROPERTY name="response-type">Success</PROPERTY>
    <PROPERTY name="response">Command completed successfully.</PROPERTY>
</OBJECT>
</RESPONSE>'''
        
        # Sample generic success response
        self.simulation_responses["default"] = '''<?xml version="1.0" encoding="UTF-8"?>
<RESPONSE>
<OBJECT basetype="status" name="status">
    <PROPERTY name="response-type">Success</PROPERTY>
    <PROPERTY name="response">Command completed successfully.</PROPERTY>
    <PROPERTY name="return-code">0</PROPERTY>
</OBJECT>
</RESPONSE>'''
    
    def connect(self):
        """
        Establish SSH connection to MSA array
        Returns True on success, error message on failure
        """
        if self.simulation_mode:
            # Simulation mode - always succeeds
            time.sleep(1)  # Simulate connection time
            self.connected = True
            return True
        
        # TODO: Uncomment for real SSH connection
        """
        try:
            import paramiko
            
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            self.client.connect(
                hostname=self.host,
                username=self.username,
                password=self.password,
                port=self.port,
                timeout=10,
                look_for_keys=False,
                allow_agent=False
            )
            
            # Open shell channel
            self.shell = self.client.invoke_shell()
            time.sleep(2)  # Wait for shell to be ready
            
            # Clear initial output
            if self.shell.recv_ready():
                self.shell.recv(4096)
            
            self.connected = True
            return True
            
        except paramiko.AuthenticationException:
            return "Authentication failed - Invalid username or password"
        except paramiko.SSHException as e:
            return f"SSH error: {str(e)}"
        except Exception as e:
            return f"Connection failed: {str(e)}"
        """
        
        return "Real SSH not implemented - install paramiko"
    
    def execute_command(self, command):
        """
        Execute command on MSA and return XML output
        Returns XML string response
        """
        if not self.connected:
            return "Not connected to array"
        
        if self.simulation_mode:
            # Simulation mode - return canned responses
            time.sleep(1)  # Simulate execution time
            
            # Check for specific commands
            cmd_lower = command.lower().strip()
            
            if "show disks" in cmd_lower:
                return self.simulation_responses["show disks"]
            elif "show configuration" in cmd_lower:
                return self.simulation_responses["show configuration"]
            else:
                return self.simulation_responses["default"]
        
        # TODO: Uncomment for real SSH execution
        """
        try:
            if not self.shell:
                return "Shell not available"
            
            # Send command
            self.shell.send(command + '\n')
            time.sleep(2)  # Wait for command to execute
            
            # Read output
            output = ""
            max_wait = 10  # Maximum 10 seconds
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                if self.shell.recv_ready():
                    chunk = self.shell.recv(8192).decode('utf-8', errors='ignore')
                    output += chunk
                    time.sleep(0.5)
                else:
                    if output:  # Have some output, likely complete
                        break
                    time.sleep(0.5)
            
            return output
            
        except Exception as e:
            return f"Execution error: {str(e)}"
        """
        
        return "Real SSH not implemented"
    
    def disconnect(self):
        """Close SSH connection"""
        if self.simulation_mode:
            self.connected = False
            return True
        
        # TODO: Uncomment for real SSH
        """
        try:
            if self.shell:
                self.shell.close()
            if self.client:
                self.client.close()
            self.connected = False
            return True
        except Exception as e:
            return f"Disconnect error: {str(e)}"
        """
        
        return True
    
    def is_connected(self):
        """Check if connection is active"""
        return self.connected