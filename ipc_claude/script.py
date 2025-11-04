import sys
import json
import logging
import threading
import time
from queue import Queue, Empty


# Configure logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)


class StoppableTask:
    """Context manager for interruptible tasks"""
    def __init__(self):
        self.stop_flag = threading.Event()
    
    def stop(self):
        """Signal the task to stop"""
        self.stop_flag.set()
    
    def should_stop(self):
        """Check if task should stop"""
        return self.stop_flag.is_set()
    
    def reset(self):
        """Reset the stop flag for new task"""
        self.stop_flag.clear()


class Backend:
    def __init__(self):
        self.running = True
        self.command_queue = Queue()
        self.current_task = StoppableTask()
        self.task_thread = None
        
    def send_output(self, data):
        """Send JSON output to stdout"""
        try:
            json_str = json.dumps(data)
            print(json_str, flush=True)
        except Exception as e:
            logger.error(f"Error sending output: {e}")
    
    def handle_heartbeat(self):
        """Respond to heartbeat"""
        self.send_output({"type": "pong", "timestamp": time.time()})
    
    def handle_convert(self, filepath, settings):
        """Handle conversion command"""
        logger.info(f"Starting conversion: {filepath} with settings {settings}")
        
        # Stop any existing task
        if self.task_thread and self.task_thread.is_alive():
            logger.warning("Task already running, stopping it first")
            self.current_task.stop()
            self.task_thread.join(timeout=5)
        
        # Reset and start new task
        self.current_task.reset()
        self.task_thread = threading.Thread(
            target=self.long_running_conversion,
            args=(filepath, settings),
            daemon=True
        )
        self.task_thread.start()
    
    def handle_kill_task(self):
        """Kill the current running task"""
        logger.info("Received kill task command")
        if self.task_thread and self.task_thread.is_alive():
            self.current_task.stop()
            self.send_output({
                "type": "info",
                "message": "Task stop signal sent"
            })
        else:
            self.send_output({
                "type": "info",
                "message": "No task running"
            })
    
    def long_running_conversion(self, filepath, settings):
        """Simulate a long-running conversion task that can be interrupted"""
        try:
            total_steps = 100
            quality = settings.get("quality", 75)
            
            for step in range(total_steps):
                # Check if we should stop
                if self.current_task.should_stop():
                    logger.info("Task stopped by user")
                    self.send_output({
                        "type": "result",
                        "status": "cancelled",
                        "message": "Task was cancelled"
                    })
                    return
                
                # Simulate work
                time.sleep(0.1)  # Simulate processing
                
                # Send progress updates
                if step % 10 == 0:
                    progress = (step / total_steps) * 100
                    self.send_output({
                        "type": "progress",
                        "progress": progress,
                        "step": step,
                        "total": total_steps
                    })
                    logger.info(f"Progress: {progress:.1f}%")
            
            # Task completed successfully
            logger.info("Conversion completed successfully")
            self.send_output({
                "type": "result",
                "status": "success",
                "filepath": filepath,
                "output_file": filepath + ".converted",
                "settings": settings,
                "message": f"File converted successfully with quality {quality}"
            })
            
        except Exception as e:
            logger.error(f"Error in conversion task: {e}", exc_info=True)
            self.send_output({
                "type": "result",
                "status": "error",
                "message": str(e)
            })
    
    def process_command(self, command_dict):
        """Process a command from stdin"""
        try:
            cmd = command_dict.get("command")
            
            if cmd == "heartbeat":
                self.handle_heartbeat()
            
            elif cmd == "convert":
                filepath = command_dict.get("filepath")
                settings = command_dict.get("settings", {})
                if filepath:
                    self.handle_convert(filepath, settings)
                else:
                    logger.error("Convert command missing filepath")
            
            elif cmd == "kill_task":
                self.handle_kill_task()
            
            elif cmd == "quit":
                logger.info("Received quit command")
                self.running = False
            
            else:
                logger.warning(f"Unknown command: {cmd}")
                
        except Exception as e:
            logger.error(f"Error processing command: {e}", exc_info=True)
    
    def read_commands(self):
        """Read commands from stdin in a separate thread"""
        while self.running:
            try:
                line = sys.stdin.readline()
                if not line:
                    # EOF reached
                    logger.info("stdin closed, shutting down")
                    self.running = False
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                try:
                    command = json.loads(line)
                    self.command_queue.put(command)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON received: {line[:100]}... Error: {e}")
                    
            except Exception as e:
                logger.error(f"Error reading stdin: {e}", exc_info=True)
                break
    
    def run(self):
        """Main backend loop"""
        logger.info("Backend started")
        
        # Start stdin reader thread
        stdin_thread = threading.Thread(target=self.read_commands, daemon=True)
        stdin_thread.start()
        
        # Main command processing loop
        while self.running:
            try:
                # Get command from queue with timeout
                command = self.command_queue.get(timeout=1)
                self.process_command(command)
            except Empty:
                # No command, continue
                continue
            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
        
        # Cleanup
        logger.info("Backend shutting down")
        if self.task_thread and self.task_thread.is_alive():
            self.current_task.stop()
            self.task_thread.join(timeout=3)


def main():
    """Entry point with exception handling"""
    try:
        backend = Backend()
        backend.run()
    except Exception as e:
        logger.critical(f"Fatal error in backend: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()