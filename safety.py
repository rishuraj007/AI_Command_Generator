# safety.py
class SafetyValidator:
    DESTRUCTIVE_COMMANDS = ['delete', 'remove', 'clear', 'format']
    
    @staticmethod
    def is_destructive(command):
        """Check if command is destructive"""
        return any(kw in command.lower() for kw in SafetyValidator.DESTRUCTIVE_COMMANDS)
    
    @staticmethod
    def require_confirmation(command):
        """Require user confirmation for destructive commands"""
        if SafetyValidator.is_destructive(command):
            print(f"\n⚠️  WARNING: This command is destructive!")
            print(f"Command: {command}")
            confirm = input("Type 'CONFIRM' to proceed: ")
            return confirm == "CONFIRM"
        return True
```

---

## 📋 **Implementation Roadmap**

### **Week 1: Basic SSH Connection**
```
✅ Install paramiko: pip install paramiko
✅ Create ssh_connector.py
✅ Test connection to array
✅ Read XML output from "show disks"
```

### **Week 2: Safe Execution**
```
✅ Add simulation/live mode toggle
✅ Implement safety validator
✅ Add command confirmation for destructive ops
✅ Test with read-only commands first
```

### **Week 3: Full Integration**
```
✅ Update UI with connection panel
✅ Add connection status indicator
✅ Implement command history with execution results
✅ Add rollback suggestions
```

### **Week 4: Production Features**
```
✅ Encrypted credential storage
✅ Multi-array support
✅ Audit logging
✅ Error recovery