# Async Backend Application

A multi-threaded application with PySide6 frontend and asynchronous Python backend communicating via stdin/stdout/stderr pipes.

## Architecture

### Frontend (PySide6)
- **Main Thread**: GUI rendering and user interactions
- **Controller Thread**: Manages backend process communication
- **Communication**: PySide6 signals between threads

### Backend (Python)
- **Stdin**: Receives JSON commands from frontend
- **Stdout**: Sends JSON results to frontend
- **Stderr**: Sends logs and uncaught exceptions
- **Interruptible Tasks**: Long-running functions can be stopped immediately

## File Structure

```
project/
├── main.py          # Main GUI application
├── controller.py    # Controller thread for backend communication
├── backend.py       # Backend process
└── README.md        # This file
```

## Installation

```bash
pip install PySide6
```

## Usage

Run the application:

```bash
python main.py
```

## Features

### Frontend Features
1. **File Selection**: Choose input file for conversion
2. **Conversion Settings**: Configure quality and other parameters
3. **Start/Stop Controls**: Start conversion or stop running tasks
4. **Real-time Output**: View backend results and progress
5. **Log Monitoring**: See backend logs in real-time
6. **Auto-Recovery**: Automatically detects and restarts dead backend

### Backend Features
1. **Heartbeat Monitoring**: Responds to heartbeat every 5 seconds
2. **Command Processing**: Handles multiple commands asynchronously
3. **Interruptible Tasks**: Tasks can be stopped immediately via `kill_task` command
4. **Progress Updates**: Sends progress information during long operations
5. **Error Handling**: All uncaught exceptions logged to stderr
6. **Graceful Shutdown**: Responds to quit command

## Communication Protocol

### Commands (Frontend → Backend via stdin)

#### Heartbeat
```json
{"command": "heartbeat"}
```

#### Convert File
```json
{
  "command": "convert",
  "filepath": "/path/to/file",
  "settings": {
    "quality": 75
  }
}
```

#### Kill Current Task
```json
{"command": "kill_task"}
```

#### Quit Backend
```json
{"command": "quit"}
```

### Responses (Backend → Frontend via stdout)

#### Pong (Heartbeat Response)
```json
{
  "type": "pong",
  "timestamp": 1234567890.123
}
```

#### Progress Update
```json
{
  "type": "progress",
  "progress": 50.0,
  "step": 50,
  "total": 100
}
```

#### Result
```json
{
  "type": "result",
  "status": "success",
  "filepath": "/path/to/file",
  "output_file": "/path/to/file.converted",
  "settings": {"quality": 75},
  "message": "File converted successfully"
}
```

#### Info Message
```json
{
  "type": "info",
  "message": "Task stop signal sent"
}
```

### Logs (Backend → Frontend via stderr)

Plain text log messages with timestamps:
```
2025-11-04 10:30:45,123 - INFO - Backend started
2025-11-04 10:30:50,456 - INFO - Starting conversion: /path/to/file
```

## Implementation Details

### Heartbeat Mechanism
- Frontend sends heartbeat every 5 seconds
- Backend responds with "pong" immediately
- Frontend expects response within 10 seconds
- If timeout occurs, backend is considered dead and restarted

### Task Interruption
- Backend uses `threading.Event` for stop signals
- Long-running function checks `should_stop()` periodically
- When `kill_task` received, stop flag is set
- Task exits gracefully at next checkpoint

### Thread Safety
- Backend processes commands from a thread-safe queue
- Stdin reader runs in separate thread
- Task execution in dedicated thread
- Main loop coordinates all activities

### Error Handling
- All exceptions logged to stderr with stack traces
- Frontend displays errors to user
- Backend continues running after non-fatal errors
- Process death triggers auto-recovery

## Customization

### Modify the Long-Running Task

Edit `backend.py` in the `long_running_conversion` method:

```python
def long_running_conversion(self, filepath, settings):
    try:
        # Your custom logic here
        for step in range(total_steps):
            # Check for stop signal
            if self.current_task.should_stop():
                self.send_output({
                    "type": "result",
                    "status": "cancelled"
                })
                return
            
            # Do work...
            # Send progress updates
            self.send_output({"type": "progress", "progress": percent})
        
        # Send final result
        self.send_output({"type": "result", "status": "success"})
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
```

### Add New Commands

1. Define command in frontend (controller.py):
```python
def send_custom_command(self, param):
    self.send_command({"command": "custom", "param": param})
```

2. Handle command in backend (backend.py):
```python
def handle_custom(self, param):
    # Your logic here
    self.send_output({"type": "result", "data": result})
```

3. Add to command processor:
```python
elif cmd == "custom":
    self.handle_custom(command_dict.get("param"))
```

## Troubleshooting

### Backend Not Starting
- Check Python interpreter path in `controller.py`
- Verify `backend.py` is in same directory
- Check stderr logs for startup errors

### Heartbeat Timeout
- Increase `heartbeat_timeout` in controller.py if tasks are very long
- Check if backend is blocked (not checking `should_stop()`)

### Commands Not Processed
- Verify JSON format is correct
- Check backend stderr for parsing errors
- Ensure stdin pipe is not broken

## License

MIT License - Feel free to modify and use in your projects.