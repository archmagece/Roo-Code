"""
Hook Metadata:
enabled: true
priority: 75
hook_types: ["TASK_STARTED", "TASK_COMPLETED", "TASK_FAILED", "MODE_SWITCHED"]
conditions: {}
description: "Track task progress and provide workflow insights"
"""

import json
import sys
import os
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Progress tracking file
PROGRESS_FILE = ".roo/hooks/task_progress.json"

def load_progress() -> Dict[str, Any]:
    """Load task progress data"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {
        "sessions": [],
        "current_session": None,
        "stats": {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "average_completion_time": 0,
            "mode_switches": 0
        }
    }

def save_progress(progress: Dict[str, Any]) -> None:
    """Save task progress data"""
    os.makedirs(os.path.dirname(PROGRESS_FILE), exist_ok=True)
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)

def calculate_productivity_insights(progress: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate productivity insights from progress data"""
    stats = progress.get("stats", {})
    sessions = progress.get("sessions", [])
    
    insights = {
        "productivity_score": 0,
        "recommendations": [],
        "patterns": {},
        "recent_performance": {}
    }
    
    # Calculate productivity score (0-100)
    if stats.get("total_tasks", 0) > 0:
        completion_rate = stats.get("completed_tasks", 0) / stats.get("total_tasks", 1)
        avg_time = stats.get("average_completion_time", 0)
        
        # Higher completion rate and reasonable time = higher score
        insights["productivity_score"] = min(100, int(completion_rate * 80 + (1 / max(avg_time/60, 1)) * 20))
    
    # Analyze recent sessions (last 7 days)
    recent_sessions = []
    cutoff_time = datetime.now() - timedelta(days=7)
    
    for session in sessions[-10:]:  # Last 10 sessions
        session_time = datetime.fromisoformat(session.get("start_time", ""))
        if session_time > cutoff_time:
            recent_sessions.append(session)
    
    if recent_sessions:
        recent_completions = sum(1 for s in recent_sessions if s.get("status") == "completed")
        insights["recent_performance"] = {
            "sessions": len(recent_sessions),
            "completions": recent_completions,
            "success_rate": recent_completions / len(recent_sessions) if recent_sessions else 0
        }
    
    # Generate recommendations
    if completion_rate < 0.7:
        insights["recommendations"].append("Consider breaking down complex tasks into smaller steps")
    
    if stats.get("mode_switches", 0) > stats.get("completed_tasks", 1) * 2:
        insights["recommendations"].append("Frequent mode switching detected - try to stay focused on one approach")
    
    if avg_time > 1800:  # 30 minutes
        insights["recommendations"].append("Tasks taking longer than expected - consider time-boxing or seeking help")
    
    return insights

def main(hook_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Track task progress and provide workflow insights.
    
    Args:
        hook_data: Contains hook_type, task_info, mode_info, and context
        
    Returns:
        Dict with action and insights
    """
    
    hook_type = hook_data.get("hook_type")
    progress = load_progress()
    
    if hook_type == "TASK_STARTED":
        # Start new task tracking
        task_info = hook_data.get("task_info", {})
        
        new_session = {
            "session_id": f"task_{int(time.time())}",
            "start_time": datetime.now().isoformat(),
            "task_description": task_info.get("description", "Unknown task"),
            "mode": task_info.get("mode", "unknown"),
            "status": "in_progress",
            "tool_uses": [],
            "mode_switches": []
        }
        
        progress["current_session"] = new_session
        progress["stats"]["total_tasks"] += 1
        
        save_progress(progress)
        
        return {
            "action": "track_start",
            "log_message": f"Started tracking task: {task_info.get('description', 'Unknown')}"
        }
    
    elif hook_type == "TASK_COMPLETED":
        # Complete current task
        if progress.get("current_session"):
            session = progress["current_session"]
            session.update({
                "end_time": datetime.now().isoformat(),
                "status": "completed",
                "duration": time.time() - time.mktime(datetime.fromisoformat(session["start_time"]).timetuple())
            })
            
            progress["sessions"].append(session)
            progress["current_session"] = None
            progress["stats"]["completed_tasks"] += 1
            
            # Update average completion time
            completed_sessions = [s for s in progress["sessions"] if s.get("status") == "completed"]
            if completed_sessions:
                total_time = sum(s.get("duration", 0) for s in completed_sessions)
                progress["stats"]["average_completion_time"] = total_time / len(completed_sessions)
            
            save_progress(progress)
            
            # Generate insights
            insights = calculate_productivity_insights(progress)
            
            return {
                "action": "task_completed",
                "insights": insights,
                "log_message": f"Task completed in {session.get('duration', 0):.1f}s. Productivity score: {insights.get('productivity_score', 0)}"
            }
    
    elif hook_type == "TASK_FAILED":
        # Mark current task as failed
        if progress.get("current_session"):
            session = progress["current_session"]
            session.update({
                "end_time": datetime.now().isoformat(),
                "status": "failed",
                "failure_reason": hook_data.get("failure_reason", "Unknown"),
                "duration": time.time() - time.mktime(datetime.fromisoformat(session["start_time"]).timetuple())
            })
            
            progress["sessions"].append(session)
            progress["current_session"] = None
            progress["stats"]["failed_tasks"] += 1
            
            save_progress(progress)
            
            return {
                "action": "task_failed",
                "log_message": f"Task failed: {hook_data.get('failure_reason', 'Unknown reason')}",
                "suggestion": "Consider reviewing the approach or breaking down the task"
            }
    
    elif hook_type == "MODE_SWITCHED":
        # Track mode switches
        if progress.get("current_session"):
            mode_info = hook_data.get("mode_info", {})
            
            progress["current_session"]["mode_switches"].append({
                "timestamp": datetime.now().isoformat(),
                "from_mode": mode_info.get("from_mode"),
                "to_mode": mode_info.get("to_mode"),
                "reason": mode_info.get("reason")
            })
            
            progress["stats"]["mode_switches"] += 1
            save_progress(progress)
            
            return {
                "action": "mode_switched",
                "log_message": f"Mode switch tracked: {mode_info.get('from_mode')} → {mode_info.get('to_mode')}"
            }
    
    return {"action": "continue"}

if __name__ == "__main__":
    # Read hook data from stdin
    hook_data = json.loads(sys.stdin.read())
    
    # Execute hook logic
    result = main(hook_data)
    
    # Return result as JSON
    print(json.dumps(result))