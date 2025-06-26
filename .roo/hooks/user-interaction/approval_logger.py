"""
Hook Metadata:
enabled: true
priority: 50
hook_types: ["BEFORE_ASK_APPROVAL", "APPROVAL_GRANTED", "APPROVAL_DENIED"]
conditions: {}
description: "Log all user approval interactions for audit and analysis"
"""

import json
import sys
import os
import time
from datetime import datetime
from typing import Dict, Any

# Log file for approval interactions
LOG_FILE = ".roo/hooks/approval_log.jsonl"

def log_approval_event(event_type: str, data: Dict[str, Any]) -> None:
    """Log approval event to JSONL file"""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "session_id": data.get("session_id", "unknown"),
        "tool_name": data.get("tool_name"),
        "approval_type": data.get("approval_type"),
        "user_response": data.get("user_response"),
        "context": data.get("context", {}),
        "metadata": data.get("metadata", {})
    }
    
    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

def analyze_approval_patterns() -> Dict[str, Any]:
    """Analyze approval patterns from log file"""
    if not os.path.exists(LOG_FILE):
        return {"total_approvals": 0, "patterns": {}}
    
    patterns = {
        "total_approvals": 0,
        "auto_approved": 0,
        "manually_approved": 0,
        "denied": 0,
        "tool_stats": {},
        "recent_activity": []
    }
    
    try:
        with open(LOG_FILE, 'r') as f:
            for line in f:
                entry = json.loads(line.strip())
                
                patterns["total_approvals"] += 1
                
                if entry["event_type"] == "APPROVAL_GRANTED":
                    if entry.get("metadata", {}).get("auto_approved"):
                        patterns["auto_approved"] += 1
                    else:
                        patterns["manually_approved"] += 1
                elif entry["event_type"] == "APPROVAL_DENIED":
                    patterns["denied"] += 1
                
                # Track tool usage patterns
                tool_name = entry.get("tool_name")
                if tool_name:
                    patterns["tool_stats"][tool_name] = patterns["tool_stats"].get(tool_name, 0) + 1
                
                # Keep recent activity (last 10 entries)
                patterns["recent_activity"].append({
                    "timestamp": entry["timestamp"],
                    "event": entry["event_type"],
                    "tool": tool_name
                })
                
                if len(patterns["recent_activity"]) > 10:
                    patterns["recent_activity"].pop(0)
    
    except Exception as e:
        patterns["error"] = str(e)
    
    return patterns

def main(hook_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Log user approval interactions and provide insights.
    
    Args:
        hook_data: Contains hook_type, tool_name, context, and user interaction data
        
    Returns:
        Dict with action and any insights or modifications
    """
    
    hook_type = hook_data.get("hook_type")
    tool_name = hook_data.get("tool_name")
    
    # Log the approval event
    log_approval_event(hook_type, hook_data)
    
    if hook_type == "BEFORE_ASK_APPROVAL":
        # Before asking for approval, analyze patterns to suggest auto-approval
        patterns = analyze_approval_patterns()
        
        # Check if this tool has high approval rate (>80%)
        tool_stats = patterns.get("tool_stats", {})
        total_for_tool = tool_stats.get(tool_name, 0)
        
        if total_for_tool > 5:  # Only suggest if we have enough data
            # In a real implementation, you'd calculate approval rate
            # For now, suggest auto-approval for frequently used tools
            frequently_approved_tools = ["read_file", "list_files", "search_files"]
            
            if tool_name in frequently_approved_tools:
                return {
                    "action": "suggest_auto_approval",
                    "suggestion": {
                        "message": f"Tool '{tool_name}' has been approved {total_for_tool} times recently. Consider enabling auto-approval?",
                        "confidence": "high" if total_for_tool > 10 else "medium"
                    }
                }
    
    elif hook_type == "APPROVAL_GRANTED":
        # Track successful approvals
        return {
            "action": "log_success",
            "log_message": f"Approval granted for {tool_name}"
        }
    
    elif hook_type == "APPROVAL_DENIED":
        # Track denials and potentially suggest alternatives
        return {
            "action": "log_denial",
            "log_message": f"Approval denied for {tool_name}",
            "suggestion": "Consider reviewing the tool request or providing more specific instructions"
        }
    
    return {"action": "continue"}

if __name__ == "__main__":
    # Read hook data from stdin
    hook_data = json.loads(sys.stdin.read())
    
    # Execute hook logic
    result = main(hook_data)
    
    # Return result as JSON
    print(json.dumps(result))