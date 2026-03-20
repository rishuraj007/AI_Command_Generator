# HPE MSA AI Command Generator

AI-powered natural language interface for HPE Modular Smart Array (MSA) storage systems. Converts natural language requests into HPE-compliant CLI commands.

## 🚀 Features

### Core Capabilities
- **Natural Language Processing**: Understands conversational commands
- **Intelligent RAID Recommendations**: Suggests optimal configurations based on workload
- **HPE-Compliant Syntax**: Generates commands matching official HPE MSA documentation
- **Comprehensive Validation**: Prevents invalid configurations before execution
- **Multiple Interfaces**: CLI and GUI options

### Supported Operations

#### Disk Group Management
- Create RAID 0, 1, 5, 6, 10 disk groups
- Create MSA-DP+ disk groups (12-128 disks)
- Show disk group information
- Delete disk groups
- Add/remove global spares

#### Volume Management
- Create single or multiple volumes
- Expand existing volumes
- Delete volumes
- Map/unmap volumes to hosts
- Set volume tiering (optimize/standard/archive)
- Create and manage snapshots

#### Show Commands
- Show disks, volumes, disk groups, pools
- Show system information
- Show snapshots

## 📋 Requirements

```
Python 3.7+
tkinter (for GUI - usually pre-installed)
```

## 🎯 Quick Start

### CLI Mode
```bash
python main.py
```

### GUI Mode
```bash
python ui.py
```

### Run Tests
```bash
python test_suite.py
```

## 💡 Usage Examples

### Disk Group Creation

```
Natural Language Input:
"create disk group with raid 5 using 4 HDDs"

Generated Command:
add disk-group type virtual disks 1.4,1.5,1.6,1.7 pool a level r5
```

```
Natural Language Input:
"create raid 10 with 6 fast drives"

Generated Command:
add disk-group type virtual disks 1.1,1.3,2.1,1.4,1.5,1.6 pool a level r10
```

```
Natural Language Input:
"create dp+ disk group with 12 HDDs"

Generated Command:
add disk-group type msa-dp+ pool a disks 1.4,1.5,1.6,1.7,1.8,1.9,1.10,1.11,1.12,1.13,1.14,1.15 spare-capacity default
```

### Volume Creation

```
Natural Language Input:
"create 3 volumes of 100GB in pool a"

Generated Commands:
create volume size 100GB pool a name a_vol1
create volume size 100GB pool a name a_vol2
create volume size 100GB pool a name a_vol3
```

### Volume Operations

```
Natural Language Input:
"expand volume myvol size 50GB"

Generated Command:
expand volume myvol size 50GB
```

```
Natural Language Input:
"map volume myvol initiator 21:00:00:24:ff:47:00:00"

Generated Command:
map volume myvol access rw lun auto initiator 21:00:00:24:ff:47:00:00
```

### Show Commands

```
Natural Language Input:
"show disks"

Generated Command:
show disks
```

## 🏗️ Architecture

### Project Structure
```
.
├── ai_layer.py          # Natural language interpretation
├── command_engine.py    # Intent detection and command orchestration
├── disk_group.py        # Disk group operations
├── volume.py            # Volume operations
├── validators.py        # Input validation and error handling
├── xml_parser.py        # XML disk inventory parser
├── data.py              # Sample disk data
├── main.py              # CLI interface
├── ui.py                # GUI interface
└── test_suite.py        # Comprehensive tests
```

### Module Responsibilities

#### `validators.py`
- Centralized input validation
- HPE MSA parameter constraints
- Custom `ValidationError` exception with suggestions
- RAID level validation (0, 1, 5, 6, 10)
- MSA-DP+ validation (12-128 disks)
- Size format validation (GB, TB, GiB, TiB)

#### `ai_layer.py`
- Natural language processing
- Keyword extraction (RAID, disk type, count, pool, size)
- Workload detection (database, backup, video)
- Intelligent disk type recommendation
- Ambiguity detection (multiple RAIDs, disk counts)

#### `command_engine.py`
- Intent detection (create, delete, show, expand, map)
- Command routing to appropriate modules
- Error handling and user feedback
- Suggestion generation for invalid inputs

#### `disk_group.py`
- Disk group creation with HPE-compliant syntax
- Disk selection algorithm
- RAID validation and optimal configuration suggestions
- Spare disk management
- MSA-DP+ support

#### `volume.py`
- Volume creation, expansion, deletion
- Volume-to-host mapping
- Snapshot management
- Tiering configuration

## ✅ Validation & Error Handling

### Input Validation
- **RAID Levels**: Validates minimum/maximum disk requirements
- **Disk Counts**: Ensures sufficient available disks
- **Size Formats**: Validates and normalizes size specifications
- **Pool Names**: Validates naming conventions
- **Volume Names**: Ensures alphanumeric constraints

### Error Messages with Suggestions
```
❌ RAID 5 requires minimum 3 disks, you specified 2
💡 RAID 5 requires 3-16 disks

❌ Insufficient HDD disks: need 8, available 5
💡 Available HDD disks: 1.4, 1.5, 1.6, 1.7, 2.2
💡 Try requesting 5 disks instead
```

### Warnings
```
⚠️  Multiple RAID levels detected: 5, 10
💡 Please specify which RAID level to use

💡 For optimal performance, HPE recommends using 3, 5, 9 disks for RAID 5. Closest optimal: 5
```

## 🎨 GUI Features

### Visual Elements
- **Real-time Disk Inventory**: Shows available SSDs/HDDs
- **Suggestion Chips**: Quick-access example commands
- **Colored Output**: Success (green), errors (red), warnings (orange)
- **Command History**: Tracks all generated commands with timestamps
- **Status Bar**: Real-time feedback on operations

### User Experience
- **Enter Key Support**: Press Enter to generate commands
- **Auto-scroll**: Automatically scrolls to latest output
- **Clear Output**: One-click output clearing
- **Built-in Help**: Accessible help documentation

## 🧪 Testing

Comprehensive test suite covering:
- All disk group creation scenarios
- Volume operations
- Edge cases and error conditions
- Natural language understanding
- Input validation

Run tests:
```bash
python test_suite.py
```

## 📚 HPE MSA Command Reference

### Official Syntax Patterns

**Disk Group (RAID)**
```
add disk-group type virtual disks <disk-list> pool <pool> level r<0|1|5|6|10>
```

**Disk Group (MSA-DP+)**
```
add disk-group type msa-dp+ pool <pool> disks <disk-list> spare-capacity default
```

**Volume Creation**
```
create volume size <size> pool <pool> name <name> [tier optimize|standard|archive]
```

**Volume Expansion**
```
expand volume <name> size <size>
```

**Volume Mapping**
```
map volume <name> access <rw|ro> lun <auto|N> initiator <wwn|iqn>
```

## 🎯 Best Practices

### RAID Level Selection
- **RAID 0**: Maximum performance, no redundancy (2-16 disks)
- **RAID 1**: Mirroring, 50% capacity (2 disks)
- **RAID 5**: Balanced performance/capacity (3-16 disks, optimal: 3, 5, 9)
- **RAID 6**: Dual parity protection (4-16 disks, optimal: 4, 6, 10)
- **RAID 10**: Mirrored stripes (4-16 disks, even numbers only)
- **MSA-DP+**: Maximum capacity, HDDs only (12-128 disks)

### Workload Recommendations
- **Database**: RAID 10 with SSDs (best IOPS)
- **Backup/Archive**: MSA-DP+ or RAID 6 with HDDs (maximize capacity)
- **Video Streaming**: RAID 5 with mixed drives (balance performance/capacity)
- **General File Storage**: RAID 5 or RAID 6 (balanced protection)

## 🔧 Customization

### Adding Custom Pool Names
Edit `validators.py`:
```python
VALID_POOLS = ["a", "b", "custom_pool_name"]
```

### Extending Disk Data
Edit `data.py` to add more disks or modify `xml_parser.py` to connect to live MSA API.

### Adding New Commands
1. Add intent detection in `command_engine.py`
2. Create command function in appropriate module
3. Add validation rules in `validators.py`
4. Update tests in `test_suite.py`

## 🚀 Future Enhancements

### Planned Features
- [ ] LLM integration (Claude/OpenAI) for advanced NLP
- [ ] Real-time MSA API integration
- [ ] Performance monitoring and recommendations
- [ ] Capacity planning tools
- [ ] Multi-system management
- [ ] Command preview with impact analysis
- [ ] Undo/rollback suggestions
- [ ] Export command scripts

### Client Demo Features
- [ ] Interactive dashboard with charts
- [ ] Command history analytics
- [ ] Workload-based wizard
- [ ] Template library for common configurations
- [ ] Simulation mode (no hardware required)

## 📄 License

Internal project for HPE MSA automation demonstrations.

## 👥 Contributing

For suggestions or improvements, please contact the development team.

## 📞 Support

For issues or questions about HPE MSA commands, refer to:
- HPE MSA CLI Command Reference Guide
- HPE Support Portal: https://support.hpe.com

---

**Version**: 2.0  
**Last Updated**: 2024  
**Status**: Production Ready for Client Demonstrations
