# ssh_connector.py
import paramiko
import time

class MSAConnector:
    def __init__(self, host, username, password, port=22):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.client = None
        self.shell = None
    
    def connect(self):
        """Establish SSH connection to MSA array"""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(
                hostname=self.host,
                username=self.username,
                password=self.password,
                port=self.port,
                timeout=10
            )
            self.shell = self.client.invoke_shell()
            time.sleep(1)  # Wait for shell to be ready
            return True
        except Exception as e:
            return f"Connection failed: {str(e)}"
    
    def execute_command(self, command):
        """Execute command on MSA and return output"""
        if not self.shell:
            return "Not connected"
        
        try:
            # Send command
            self.shell.send(command + '\n')
            time.sleep(2)  # Wait for command to execute
            
            # Read output
            output = ""
            while self.shell.recv_ready():
                output += self.shell.recv(4096).decode('utf-8')
            
            return output
        except Exception as e:
            return f"Execution failed: {str(e)}"
    
    def disconnect(self):
        """Close SSH connection"""
        if self.shell:
            self.shell.close()
        if self.client:
            self.client.close()