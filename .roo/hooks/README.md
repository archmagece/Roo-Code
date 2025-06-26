# Roo Code Hook System

The Roo Code Hook System provides a powerful way to automate and customize your development workflow through Python scripts that run at specific points during tool execution.

## Directory Structure

```
.roo/hooks/
├── README.md                           # This documentation
├── tool-execution/                     # Hooks that run during tool execution
│   ├── auto_proceed_while_running.py   # Auto-approve long-running commands
│   └── todo_batch_processor.py         # Batch process large TODO lists
├── user-interaction/                   # Hooks for user approval and interaction
│   └── approval_logger.py              # Log and analyze approval patterns
├── workflow/                           # Hooks for task and workflow management
│   └── task_progress_tracker.py        # Track task progress and productivity
└── system-events/                      # Hooks for system startup and events
    └── startup_initializer.py          # Initialize hook system on startup
```

## Hook Types

### Tool Execution Hooks
- `BEFORE_EXECUTE_COMMAND` - Run before any command execution
- `AFTER_EXECUTE_COMMAND` - Run after command completion
- `BEFORE_TOOL_USE` - Run before any tool is used
- `AFTER_TOOL_USE` - Run after tool execution
- `COMMAND_OUTPUT_RECEIVED` - Run when command output is received

### User Interaction Hooks
- `BEFORE_ASK_APPROVAL` - Run before asking user for approval
- `APPROVAL_GRANTED` - Run when user grants approval
- `APPROVAL_DENIED` - Run when user denies approval

### Workflow Hooks
- `TASK_STARTED` - Run when a new task begins
- `TASK_COMPLETED` - Run when a task is completed
- `TASK_FAILED` - Run when a task fails
- `MODE_SWITCHED` - Run when switching between modes

### System Event Hooks
- `EXTENSION_STARTUP` - Run when extension starts
- `WORKSPACE_OPENED` - Run when a workspace is opened

## Hook File Format

Each hook file must be a Python script with metadata in the docstring header:

```python
"""
Hook Metadata:
enabled: true|false
priority: 0-1000 (higher = runs first)
hook_types: ["HOOK_TYPE_1", "HOOK_TYPE_2"]
conditions: {"key": "value", "tool_name": "execute_command"}
description: "Brief description of what this hook does"
"""

import json
import sys
from typing import Dict, Any

def main(hook_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main hook function that processes the hook event.
    
    Args:
        hook_data: Dictionary containing:
            - hook_type: The type of hook being executed
            - tool_name: Name of the tool being used (if applicable)
            - parameters: Tool parameters (if applicable)
            - context: Additional context information
            - user_state: Current user/session state
    
    Returns:
        Dictionary with action and any modifications:
            - action: "continue" | "modify_execution" | "cancel" | "retry"
            - modifications: Dict of changes to apply
            - log_message: Optional message to log
            - suggestions: Optional suggestions for the user
    """
    
    # Your hook logic here
    
    return {"action": "continue"}

if __name__ == "__main__":
    hook_data = json.loads(sys.stdin.read())
    result = main(hook_data)
    print(json.dumps(result))
```

## Available Example Hooks

### 1. Auto Proceed While Running (`tool-execution/auto_proceed_while_running.py`)
Automatically approves `proceedWhileRunning` confirmations for long-running commands like builds, installations, and tests.

**Use Cases:**
- Auto-approve npm/yarn installations
- Auto-approve build processes
- Auto-approve test runs

### 2. TODO Batch Processor (`tool-execution/todo_batch_processor.py`)
Handles large TODO lists (100+ items) with automatic batching, interruption recovery, and retry logic.

**Features:**
- Batch processing of TODO items
- Automatic retry on failures
- Progress tracking and recovery
- State persistence across interruptions

### 3. Approval Logger (`user-interaction/approval_logger.py`)
Logs all user approval interactions and provides insights on approval patterns.

**Features:**
- Comprehensive approval logging
- Pattern analysis and suggestions
- Auto-approval recommendations
- Usage statistics

### 4. Task Progress Tracker (`workflow/task_progress_tracker.py`)
Tracks task progress, completion rates, and provides productivity insights.

**Features:**
- Task duration tracking
- Productivity scoring
- Mode switch analysis
- Performance recommendations

### 5. Startup Initializer (`system-events/startup_initializer.py`)
Initializes the hook system and performs health checks on startup.

**Features:**
- First-time setup
- Hook system health checks
- Workspace type detection
- Performance monitoring

## Hook Data Structure

Hooks receive data in the following format:

```typescript
interface HookData {
  hook_type: string;
  tool_name?: string;
  parameters?: Record<string, any>;
  context?: {
    session_id: string;
    user_id: string;
    workspace_path: string;
    current_mode: string;
  };
  user_state?: Record<string, any>;
  system_info?: Record<string, any>;
}
```

## Hook Response Format

Hooks must return responses in this format:

```typescript
interface HookResponse {
  action: "continue" | "modify_execution" | "cancel" | "retry" | "suggest_auto_approval";
  modifications?: Record<string, any>;
  log_message?: string;
  suggestions?: string | Record<string, any>;
  next_command?: string;
  auto_approve?: boolean;
}
```

## Creating Custom Hooks

1. Create a new Python file in the appropriate category directory
2. Add the metadata header with your hook configuration
3. Implement the `main()` function with your hook logic
4. Test your hook by enabling it and triggering the relevant events
5. The hook system will automatically discover and load your hook

## Hook Execution Order

Hooks are executed in priority order (highest first), then by:
1. System event hooks (priority 200+)
2. Tool execution hooks (priority 100+) 
3. Workflow hooks (priority 75+)
4. User interaction hooks (priority 50+)

## Settings

The hook system can be enabled/disabled globally in VSCode settings:
- `rooCode.hooks.enabled`: Enable/disable the entire hook system

Individual hooks can be enabled/disabled by changing the `enabled` flag in their metadata.

## State Persistence

Hooks can persist state using JSON files in `.roo/hooks/`:
- `todo_batch_state.json` - TODO batch processing state
- `approval_log.jsonl` - Approval interaction logs
- `task_progress.json` - Task progress and productivity data
- `system_state.json` - System startup and health data

## Best Practices

1. **Keep hooks lightweight** - Hooks should execute quickly to avoid slowing down the UI
2. **Handle errors gracefully** - Always include error handling in your hook logic
3. **Use appropriate priorities** - Higher priority hooks run first and can influence later hooks
4. **Test thoroughly** - Test your hooks with various scenarios before enabling them
5. **Document your hooks** - Include clear descriptions and usage examples
6. **Use conditions wisely** - Use the conditions field to ensure hooks only run when relevant

## Troubleshooting

If hooks aren't working:
1. Check that `rooCode.hooks.enabled` is set to `true`
2. Verify the hook file has correct metadata format
3. Check the VS Code console for Python execution errors
4. Ensure Python is available in your system PATH
5. Review hook file permissions and syntax

## Security Considerations

- Hooks execute Python code with your user permissions
- Only enable hooks from trusted sources
- Review hook code before enabling
- Use the `enabled: false` flag to disable suspicious hooks
- Hook files in `.roo/hooks/` should be treated as executable code
