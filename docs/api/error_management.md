# Error Management System API Documentation

## Overview
The Error Management System provides a comprehensive API for detecting, managing, and fixing errors in software projects. It includes memory management, security validation, and automated error resolution capabilities.

## Core Components

### ErrorManager

The main class responsible for managing errors and coordinating system components.

#### Initialization
```python
manager = ErrorManager(project_root: Optional[Path] = None)
```
- `project_root`: Optional path to the project root directory

#### Methods

##### Error Management
```python
async def add_error_async(error: Error) -> bool
```
Adds an error to the management system asynchronously.
- Parameters:
  - `error`: Error object containing error details
- Returns: Boolean indicating success

```python
async def process_error(error_id: str) -> Dict[str, Error]
```
Processes an error asynchronously.
- Parameters:
  - `error_id`: Unique identifier of the error
- Returns: Dictionary containing processed error if successful

```python
async def apply_fix(error_id: str, fix_content: str) -> bool
```
Applies a fix to an error asynchronously.
- Parameters:
  - `error_id`: Unique identifier of the error
  - `fix_content`: The fix content to apply
- Returns: Boolean indicating success

##### Memory Management
```python
def get_memory_metrics() -> Dict[str, List[Any]]
```
Retrieves current memory usage metrics.
- Returns: Dictionary containing memory usage history

```python
def adjust_thresholds()
```
Adjusts memory thresholds based on usage patterns.

### MemoryManager

Manages system resource usage and thresholds.

#### Initialization
```python
manager = MemoryManager()
```

#### Methods

```python
def set_threshold(component_type: str, component_name: str, threshold: ResourceThreshold)
```
Sets resource thresholds for a component.
- Parameters:
  - `component_type`: Type of component ("file", "function", "class", "method")
  - `component_name`: Name of the component
  - `threshold`: ResourceThreshold object

```python
def get_threshold(component_type: str, component_name: str) -> ResourceThreshold
```
Gets resource thresholds for a component.
- Parameters:
  - `component_type`: Type of component
  - `component_name`: Name of the component
- Returns: ResourceThreshold object

```python
def get_usage_metrics() -> Dict[str, List[ResourceUsage]]
```
Gets historical usage metrics.
- Returns: Dictionary containing usage history

## Data Models

### Error
```python
@dataclass
class Error:
    id: str
    file_path: Path
    line_number: int
    error_type: str
    message: str
    status: str
    created_at: datetime
    fix_attempts: int
```

### ResourceThreshold
```python
@dataclass
class ResourceThreshold:
    memory_limit: int  # in MB
    token_limit: int
    response_time_limit: float  # in seconds
```

### ResourceUsage
```python
@dataclass
class ResourceUsage:
    memory_used: int  # in MB
    tokens_used: int
    response_time: float  # in seconds
```

## Usage Examples

### Basic Error Management
```python
# Initialize manager
manager = ErrorManager(Path("/path/to/project"))

# Add an error
error = Error(
    id="error_1",
    file_path=Path("src/file.py"),
    line_number=10,
    error_type="SyntaxError",
    message="Invalid syntax",
    status="new",
    created_at=datetime.now(),
    fix_attempts=0
)
await manager.add_error_async(error)

# Process error
result = await manager.process_error("error_1")

# Apply fix
success = await manager.apply_fix("error_1", "fixed_content")
```

### Memory Management
```python
# Get memory metrics
metrics = manager.get_memory_metrics()

# Adjust thresholds
manager.adjust_thresholds()

# Stop monitoring
await manager.stop()
```

## Error Handling

The system includes comprehensive error handling:

1. Security Validation
```python
try:
    await manager.add_error_async(error)
except SecurityError as e:
    logger.error(f"Security error: {e}")
```

2. Memory Threshold Violations
```python
# System automatically handles memory threshold violations
# and logs warnings when thresholds are exceeded
```

3. General Error Handling
```python
try:
    await manager.process_error(error_id)
except Exception as e:
    logger.error(f"Error processing error: {e}")
```

## Best Practices

1. Memory Management
- Monitor memory usage regularly
- Adjust thresholds based on application needs
- Handle threshold violations appropriately

2. Error Processing
- Implement retry logic for failed fixes
- Monitor fix success rates
- Maintain error history for analysis

3. Security
- Always validate file paths
- Verify fixes before applying
- Maintain secure environment boundaries

## Configuration

The system can be configured through various threshold settings:

```python
# Configure process threshold
process_threshold = ResourceThreshold(
    memory_limit=200,  # 200MB
    token_limit=2000,
    response_time_limit=5.0
)
manager._memory_manager.set_threshold("method", "process_error", process_threshold)

# Configure file threshold
file_threshold = ResourceThreshold(
    memory_limit=150,  # 150MB
    token_limit=1500,
    response_time_limit=3.0
)
manager._memory_manager.set_threshold("file", "path/to/file", file_threshold)
