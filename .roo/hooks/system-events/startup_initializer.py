"""
Hook Metadata:
enabled: true
priority: 200
hook_types: ["EXTENSION_STARTUP", "WORKSPACE_OPENED"]
conditions: {}
description: "Initialize hook system and perform startup checks"
"""

import json
import sys
import os
import time
from datetime import datetime
from typing import Dict, Any, List

# System state file
SYSTEM_STATE_FILE = ".roo/hooks/system_state.json"

def load_system_state() -> Dict[str, Any]:
    """Load system state data"""
    if os.path.exists(SYSTEM_STATE_FILE):
        with open(SYSTEM_STATE_FILE, 'r') as f:
            return json.load(f)
    return {
        "first_startup": True,
        "startup_count": 0,
        "last_startup": None,
        "hook_system_version": "1.0.0",
        "performance_stats": {
            "average_startup_time": 0,
            "hook_execution_times": {}
        },
        "workspace_info": {}
    }

def save_system_state(state: Dict[str, Any]) -> None:
    """Save system state data"""
    os.makedirs(os.path.dirname(SYSTEM_STATE_FILE), exist_ok=True)
    with open(SYSTEM_STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def check_hook_system_health() -> Dict[str, Any]:
    """Check health of hook system"""
    health_report = {
        "status": "healthy",
        "issues": [],
        "recommendations": [],
        "hook_files": {
            "total": 0,
            "enabled": 0,
            "disabled": 0,
            "errors": []
        }
    }
    
    # Check for hook files in all categories
    hook_dirs = [
        ".roo/hooks/tool-execution",
        ".roo/hooks/user-interaction", 
        ".roo/hooks/workflow",
        ".roo/hooks/system-events"
    ]
    
    for hook_dir in hook_dirs:
        if os.path.exists(hook_dir):
            for file in os.listdir(hook_dir):
                if file.endswith('.py'):
                    health_report["hook_files"]["total"] += 1
                    
                    # Try to parse metadata
                    try:
                        with open(os.path.join(hook_dir, file), 'r') as f:
                            content = f.read()
                            
                        # Simple metadata extraction
                        if 'enabled: true' in content:
                            health_report["hook_files"]["enabled"] += 1
                        elif 'enabled: false' in content:
                            health_report["hook_files"]["disabled"] += 1
                        else:
                            health_report["hook_files"]["errors"].append(f"Missing enabled flag in {file}")
                            
                    except Exception as e:
                        health_report["hook_files"]["errors"].append(f"Error reading {file}: {str(e)}")
    
    # Generate recommendations
    if health_report["hook_files"]["total"] == 0:
        health_report["issues"].append("No hook files found")
        health_report["recommendations"].append("Create example hook files to get started")
    
    if health_report["hook_files"]["errors"]:
        health_report["status"] = "degraded"
        health_report["recommendations"].append("Fix hook file errors to ensure proper execution")
    
    return health_report

def initialize_workspace(workspace_path: str) -> Dict[str, Any]:
    """Initialize workspace-specific hook settings"""
    workspace_info = {
        "path": workspace_path,
        "initialized_at": datetime.now().isoformat(),
        "project_type": "unknown",
        "recommended_hooks": []
    }
    
    # Detect project type and recommend hooks
    if os.path.exists(os.path.join(workspace_path, "package.json")):
        workspace_info["project_type"] = "node"
        workspace_info["recommended_hooks"] = [
            "auto_proceed_while_running.py",
            "npm_install_optimizer.py"
        ]
    elif os.path.exists(os.path.join(workspace_path, "requirements.txt")) or os.path.exists(os.path.join(workspace_path, "pyproject.toml")):
        workspace_info["project_type"] = "python"
        workspace_info["recommended_hooks"] = [
            "todo_batch_processor.py",
            "pytest_auto_runner.py"
        ]
    elif os.path.exists(os.path.join(workspace_path, "Cargo.toml")):
        workspace_info["project_type"] = "rust"
        workspace_info["recommended_hooks"] = [
            "cargo_build_optimizer.py"
        ]
    
    return workspace_info

def main(hook_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle system startup and initialization.
    
    Args:
        hook_data: Contains hook_type, system_info, and context
        
    Returns:
        Dict with action and initialization results
    """
    
    hook_type = hook_data.get("hook_type")
    system_info = hook_data.get("system_info", {})
    
    state = load_system_state()
    startup_time = time.time()
    
    if hook_type == "EXTENSION_STARTUP":
        # Extension is starting up
        state["startup_count"] += 1
        state["last_startup"] = datetime.now().isoformat()
        
        # Check if this is first startup
        if state.get("first_startup", True):
            state["first_startup"] = False
            
            # Perform first-time setup
            health_report = check_hook_system_health()
            
            save_system_state(state)
            
            return {
                "action": "first_startup",
                "health_report": health_report,
                "log_message": "Hook system initialized for first time",
                "welcome_message": "Welcome to Roo Code Hook System! Your automation capabilities are now active."
            }
        else:
            # Regular startup
            health_report = check_hook_system_health()
            
            # Calculate startup performance
            if state["startup_count"] > 1:
                previous_avg = state["performance_stats"].get("average_startup_time", 0)
                current_startup_time = time.time() - startup_time
                new_avg = (previous_avg * (state["startup_count"] - 1) + current_startup_time) / state["startup_count"]
                state["performance_stats"]["average_startup_time"] = new_avg
            
            save_system_state(state)
            
            return {
                "action": "regular_startup", 
                "health_report": health_report,
                "startup_count": state["startup_count"],
                "log_message": f"Hook system startup #{state['startup_count']} completed"
            }
    
    elif hook_type == "WORKSPACE_OPENED":
        # New workspace opened
        workspace_path = system_info.get("workspace_path", "")
        
        if workspace_path:
            workspace_info = initialize_workspace(workspace_path)
            state["workspace_info"] = workspace_info
            
            save_system_state(state)
            
            return {
                "action": "workspace_initialized",
                "workspace_info": workspace_info,
                "log_message": f"Workspace initialized: {workspace_info['project_type']} project detected",
                "recommendations": workspace_info.get("recommended_hooks", [])
            }
    
    return {"action": "continue"}

if __name__ == "__main__":
    # Read hook data from stdin
    hook_data = json.loads(sys.stdin.read())
    
    # Execute hook logic
    result = main(hook_data)
    
    # Return result as JSON
    print(json.dumps(result))