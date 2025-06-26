"""
Hook Metadata:
enabled: true
priority: 100
hook_types: ["BEFORE_EXECUTE_COMMAND"]
conditions: {"tool_name": "execute_command", "auto_approve": true}
description: "Automatically approve proceedWhileRunning confirmations for long-running commands"
"""

import json
import sys
from typing import Dict, Any

def main(hook_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Auto-approve proceedWhileRunning confirmations for execute_command tool.
    
    Args:
        hook_data: Contains tool_name, parameters, context, and user_state
        
    Returns:
        Dict with action and any modifications to the execution
    """
    
    # Check if this is an execute_command that might need proceedWhileRunning approval
    if hook_data.get("tool_name") == "execute_command":
        command = hook_data.get("parameters", {}).get("command", "")
        
        # Commands that typically run for a long time and might need auto-approval
        long_running_commands = [
            "npm install", "yarn install", "pip install",
            "npm run build", "yarn build", "npm run dev", "yarn dev",
            "docker build", "docker run", "docker-compose up",
            "pytest", "npm test", "yarn test",
            "git clone", "git pull", "git push"
        ]
        
        # Check if command matches patterns that benefit from auto-approval
        for pattern in long_running_commands:
            if pattern in command.lower():
                return {
                    "action": "modify_execution",
                    "modifications": {
                        "auto_approve_proceed_while_running": True,
                        "log_message": f"Auto-approved proceedWhileRunning for command: {command}"
                    }
                }
    
    # Default: don't modify execution
    return {"action": "continue"}

if __name__ == "__main__":
    # Read hook data from stdin
    hook_data = json.loads(sys.stdin.read())
    
    # Execute hook logic
    result = main(hook_data)
    
    # Return result as JSON
    print(json.dumps(result))