"""
Hook Metadata:
enabled: true
priority: 90
hook_types: ["BEFORE_EXECUTE_COMMAND", "AFTER_EXECUTE_COMMAND", "COMMAND_OUTPUT_RECEIVED"]
conditions: {"tool_name": "execute_command", "contains": "todo"}
description: "Batch process large TODO lists automatically with interruption recovery"
"""

import json
import sys
import os
import time
from typing import Dict, Any, List

# Global state file for tracking TODO progress
STATE_FILE = ".roo/hooks/todo_batch_state.json"

def load_state() -> Dict[str, Any]:
    """Load TODO batch processing state"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {
        "current_batch": 0,
        "total_batches": 0,
        "completed_todos": [],
        "failed_todos": [],
        "batch_size": 10,
        "auto_retry": True,
        "max_retries": 3
    }

def save_state(state: Dict[str, Any]) -> None:
    """Save TODO batch processing state"""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def detect_todo_list(command: str) -> List[str]:
    """Detect and extract TODO items from command or context"""
    # This is a simplified example - in practice, this would parse
    # TODO comments from files or extract items from the command
    todos = []
    
    # Example patterns to detect TODO lists
    if "process todos" in command.lower() or "todo list" in command.lower():
        # In a real implementation, this would scan files for TODO comments
        # For now, return example todos
        todos = [
            "Fix authentication bug in login.py",
            "Add validation to user input forms",
            "Optimize database queries in analytics",
            "Update documentation for API endpoints",
            "Refactor legacy code in utils module"
        ]
    
    return todos

def main(hook_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle TODO batch processing with interruption recovery.
    
    Args:
        hook_data: Contains hook_type, tool_name, parameters, context
        
    Returns:
        Dict with action and modifications
    """
    
    hook_type = hook_data.get("hook_type")
    tool_name = hook_data.get("tool_name")
    command = hook_data.get("parameters", {}).get("command", "")
    
    if tool_name == "execute_command":
        
        if hook_type == "BEFORE_EXECUTE_COMMAND":
            # Check if this is a TODO-related command
            todos = detect_todo_list(command)
            
            if todos and len(todos) > 5:  # Only batch process if >5 TODOs
                state = load_state()
                
                # Initialize new batch processing session
                state.update({
                    "current_batch": 0,
                    "total_batches": (len(todos) + state["batch_size"] - 1) // state["batch_size"],
                    "todos": todos,
                    "start_time": time.time(),
                    "session_id": f"todo_batch_{int(time.time())}"
                })
                
                save_state(state)
                
                return {
                    "action": "modify_execution",
                    "modifications": {
                        "batch_processing": True,
                        "auto_approve_proceed_while_running": True,
                        "log_message": f"Starting TODO batch processing: {len(todos)} items in {state['total_batches']} batches"
                    }
                }
        
        elif hook_type == "AFTER_EXECUTE_COMMAND":
            # Check if batch processing was active
            state = load_state()
            
            if state.get("current_batch", 0) > 0:
                # Update progress
                state["current_batch"] += 1
                
                if state["current_batch"] < state["total_batches"]:
                    # Continue with next batch
                    next_todos = state["todos"][
                        state["current_batch"] * state["batch_size"]:
                        (state["current_batch"] + 1) * state["batch_size"]
                    ]
                    
                    save_state(state)
                    
                    return {
                        "action": "queue_next_command",
                        "next_command": f"# Processing TODO batch {state['current_batch'] + 1}/{state['total_batches']}\n# Items: {', '.join(next_todos[:3])}{'...' if len(next_todos) > 3 else ''}",
                        "auto_approve": True
                    }
                else:
                    # Batch processing complete
                    completion_time = time.time() - state.get("start_time", 0)
                    
                    return {
                        "action": "log_completion",
                        "log_message": f"TODO batch processing completed: {len(state.get('todos', []))} items processed in {completion_time:.1f}s"
                    }
        
        elif hook_type == "COMMAND_OUTPUT_RECEIVED":
            # Monitor for errors and handle retries
            output = hook_data.get("output", "")
            
            if "error" in output.lower() or "failed" in output.lower():
                state = load_state()
                
                if state.get("auto_retry", True):
                    retry_count = state.get("retry_count", 0)
                    
                    if retry_count < state.get("max_retries", 3):
                        state["retry_count"] = retry_count + 1
                        save_state(state)
                        
                        return {
                            "action": "retry_command",
                            "log_message": f"TODO batch processing error detected, retrying ({retry_count + 1}/{state['max_retries']})",
                            "auto_approve": True
                        }
                    else:
                        return {
                            "action": "pause_batch",
                            "log_message": "TODO batch processing paused due to repeated errors. Manual intervention required."
                        }
    
    return {"action": "continue"}

if __name__ == "__main__":
    # Read hook data from stdin
    hook_data = json.loads(sys.stdin.read())
    
    # Execute hook logic
    result = main(hook_data)
    
    # Return result as JSON
    print(json.dumps(result))