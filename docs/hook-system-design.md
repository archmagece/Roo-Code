# File-Based Hook System Design for Roo Code

## Overview

This document outlines the design for a simplified file-based hook system that allows users to execute custom Python scripts at various points during Roo Code's execution lifecycle. Hooks are stored as files in `.roo/hooks/` subdirectories with metadata headers for configuration.

## Architecture

### File-Based Hook Structure
```
.roo/
├── hooks/
│   ├── tool-execution/
│   │   ├── before-command.py
│   │   ├── after-command.py
│   │   └── command-output.py
│   ├── user-interaction/
│   │   ├── before-approval.py
│   │   ├── approval-granted.py
│   │   └── approval-denied.py
│   ├── workflow/
│   │   ├── task-started.py
│   │   ├── task-completed.py
│   │   └── task-failed.py
│   └── system-events/
│       ├── extension-activated.py
│       └── settings-changed.py
```

### Hook File Format
Each hook file contains metadata at the top using Python comments:

```python
#!/usr/bin/env python3
"""
Hook: Before Command Execution
Type: BEFORE_EXECUTE_COMMAND
Enabled: true
Priority: 100
Description: Validates commands before execution and sets up environment
Conditions: 
  - tool_name: execute_command
  - file_extension: .py,.js,.ts
Author: User Name
Version: 1.0.0
"""

import json
import sys
from pathlib import Path

def main(context):
    # Hook implementation
    hook_type = context['hookType']
    data = context['data']
    
    # Your automation logic here
    if 'todo' in data.get('command', '').lower():
        prepare_todo_environment(context)

def prepare_todo_environment(context):
    # Implementation details
    pass

if __name__ == '__main__':
    context = json.loads(sys.argv[1])
    main(context)
```

## Core Components

### 1. HookManager Class
- **Location**: `src/core/hooks/HookManager.ts`
- **Purpose**: Discover, load, and execute file-based hooks
- **Responsibilities**:
  - Scan `.roo/hooks/` directory for hook files
  - Parse hook metadata from file headers
  - Execute enabled hooks at appropriate lifecycle points
  - Handle hook errors and logging

### 2. HookMetadataParser Class
- **Location**: `src/core/hooks/HookMetadataParser.ts`
- **Purpose**: Parse metadata from hook file headers
- **Responsibilities**:
  - Extract metadata from Python comment headers
  - Validate hook configuration
  - Convert metadata to typed interfaces

### 3. PythonScriptRunner Class
- **Location**: `src/core/hooks/PythonScriptRunner.ts`
- **Purpose**: Execute Python hook scripts securely
- **Responsibilities**:
  - Execute Python scripts with proper sandboxing
  - Handle script output and error capture
  - Provide script execution context and environment variables
  - Manage script timeouts and cancellation

## Hook Categories and Integration Points

### 1. Tool Execution Lifecycle Hooks
- **Location**: `.roo/hooks/tool-execution/`
- **Hook Types**:
  - `BEFORE_TOOL_USE` - Before any tool execution
  - `AFTER_TOOL_USE` - After tool execution completes
  - `BEFORE_EXECUTE_COMMAND` - Before command execution
  - `AFTER_EXECUTE_COMMAND` - After command execution
  - `COMMAND_OUTPUT_RECEIVED` - When command output is received

### 2. User Interaction Hooks
- **Location**: `.roo/hooks/user-interaction/`
- **Hook Types**:
  - `BEFORE_ASK_APPROVAL` - Before asking for user approval
  - `APPROVAL_GRANTED` - When user grants approval
  - `APPROVAL_DENIED` - When user denies approval
  - `USER_FEEDBACK_RECEIVED` - When user provides feedback

### 3. Workflow Hooks
- **Location**: `.roo/hooks/workflow/`
- **Hook Types**:
  - `TASK_STARTED` - When a new task begins
  - `TASK_COMPLETED` - When a task completes successfully
  - `TASK_FAILED` - When a task fails
  - `MODE_SWITCHED` - When switching between modes

### 4. System Event Hooks
- **Location**: `.roo/hooks/system-events/`
- **Hook Types**:
  - `EXTENSION_ACTIVATED` - When extension starts
  - `EXTENSION_DEACTIVATED` - When extension stops
  - `SETTINGS_CHANGED` - When settings are modified

## Hook Metadata Schema

### Required Metadata Fields
```python
"""
Hook: [Display Name]
Type: [HOOK_TYPE]
Enabled: [true|false]
Priority: [number]
Description: [Description]
"""
```

### Optional Metadata Fields
```python
"""
Conditions: 
  - tool_name: execute_command
  - file_extension: .py,.js,.ts
  - workspace_contains: package.json
Author: [Author Name]
Version: [Version]
Timeout: [milliseconds]
Dependencies: [python packages]
"""
```

## Type Definitions

### HookMetadata Interface
```typescript
export interface HookMetadata {
  name: string;
  type: HookType;
  enabled: boolean;
  priority: number;
  description: string;
  filePath: string;
  conditions?: HookCondition[];
  author?: string;
  version?: string;
  timeout?: number;
  dependencies?: string[];
}
```

### HookType Enum
```typescript
export enum HookType {
  // Tool Execution Lifecycle
  BEFORE_TOOL_USE = 'BEFORE_TOOL_USE',
  AFTER_TOOL_USE = 'AFTER_TOOL_USE',
  BEFORE_EXECUTE_COMMAND = 'BEFORE_EXECUTE_COMMAND',
  AFTER_EXECUTE_COMMAND = 'AFTER_EXECUTE_COMMAND',
  COMMAND_OUTPUT_RECEIVED = 'COMMAND_OUTPUT_RECEIVED',
  
  // User Interaction
  BEFORE_ASK_APPROVAL = 'BEFORE_ASK_APPROVAL',
  APPROVAL_GRANTED = 'APPROVAL_GRANTED',
  APPROVAL_DENIED = 'APPROVAL_DENIED',
  USER_FEEDBACK_RECEIVED = 'USER_FEEDBACK_RECEIVED',
  
  // Workflow
  TASK_STARTED = 'TASK_STARTED',
  TASK_COMPLETED = 'TASK_COMPLETED',
  TASK_FAILED = 'TASK_FAILED',
  MODE_SWITCHED = 'MODE_SWITCHED',
  
  // System Events
  EXTENSION_ACTIVATED = 'EXTENSION_ACTIVATED',
  EXTENSION_DEACTIVATED = 'EXTENSION_DEACTIVATED',
  SETTINGS_CHANGED = 'SETTINGS_CHANGED'
}
```

### HookCondition Interface
```typescript
export interface HookCondition {
  type: 'tool_name' | 'file_extension' | 'workspace_contains' | 'custom';
  operator: 'equals' | 'contains' | 'matches' | 'not_equals';
  value: string;
  caseSensitive?: boolean;
}
```

## Settings Integration

### Global Hook System Toggle
Only one setting is needed in the VSCode settings:

```json
{
  "rooCode.hooks.enabled": true
}
```

### Settings UI Components
- **Location**: `webview-ui/src/components/settings/HookToggle.tsx`
- **Purpose**: Simple ON/OFF toggle for the entire hook system
- **Implementation**: Similar to existing `AutoApproveToggle.tsx`

## Implementation Plan

### Phase 1: Core Hook Infrastructure
1. Create `HookManager` class with file system scanning
2. Create `HookMetadataParser` for parsing file headers
3. Create `PythonScriptRunner` for script execution
4. Add hook system integration to extension activation
5. Create global hook toggle in settings

### Phase 2: Hook Integration Points
1. Integrate hooks into `executeCommandTool.ts`
2. Integrate hooks into `presentAssistantMessage.ts`
3. Integrate hooks into `Task.say()` method
4. Add user interaction hooks to ChatView component
5. Add system event hooks to extension lifecycle

### Phase 3: Hook Directory Structure
1. Create `.roo/hooks/` directory structure
2. Create example hook files for each category
3. Add hook validation and error handling
4. Implement hook execution logging

### Phase 4: Documentation and Templates
1. Create hook development documentation
2. Create Python script templates for common scenarios
3. Add hook debugging and testing capabilities
4. Create hook sharing and distribution mechanism

## Example Hook Files

### TODO Automation Hook
```python
#!/usr/bin/env python3
"""
Hook: TODO Automation
Type: BEFORE_EXECUTE_COMMAND
Enabled: true
Priority: 100
Description: Automates TODO processing with checkpoint and resume capabilities
Conditions: 
  - tool_name: execute_command
Author: User
Version: 1.0.0
"""

import json
import sys
from pathlib import Path

def main(context):
    hook_type = context['hookType']
    data = context['data']
    
    # Check if this is a TODO-related command
    command = data.get('command', '')
    if 'todo' in command.lower():
        # Log TODO processing start
        context['utilities']['log'](f"Starting TODO automation for: {command}")
        
        # Prepare TODO processing environment
        prepare_todo_environment(context)

def prepare_todo_environment(context):
    workspace_root = context['environment']['workspaceRoot']
    todo_config = Path(workspace_root) / '.todo-config.json'
    
    if not todo_config.exists():
        # Create default TODO configuration
        default_config = {
            'batch_size': 10,
            'auto_commit': True,
            'backup_before_processing': True
        }
        context['utilities']['writeFile'](str(todo_config), json.dumps(default_config, indent=2))

if __name__ == '__main__':
    context = json.loads(sys.argv[1])
    main(context)
```

### Auto-Approval Hook
```python
#!/usr/bin/env python3
"""
Hook: Smart Auto-Approval
Type: BEFORE_ASK_APPROVAL
Enabled: true
Priority: 200
Description: Automatically approves safe operations based on context
Conditions: 
  - tool_name: execute_command
Author: User
Version: 1.0.0
"""

import json
import sys

def main(context):
    data = context['data']
    tool_name = data.get('toolName', '')
    parameters = data.get('parameters', {})
    
    # Auto-approve safe read-only operations
    if is_safe_operation(tool_name, parameters):
        context['utilities']['log'](f"Auto-approving safe operation: {tool_name}")
        return {'autoApprove': True}
    
    # Let user decide for potentially dangerous operations
    return {'autoApprove': False}

def is_safe_operation(tool_name, parameters):
    # Define safe operations
    safe_commands = ['ls', 'cat', 'head', 'tail', 'grep', 'find']
    
    if tool_name == 'execute_command':
        command = parameters.get('command', '')
        return any(command.startswith(safe_cmd) for safe_cmd in safe_commands)
    
    return False

if __name__ == '__main__':
    context = json.loads(sys.argv[1])
    result = main(context)
    print(json.dumps(result))
```

## Hook Directory Management

### Automatic Directory Creation
The system automatically creates the hook directory structure when first initialized:

```typescript
async function initializeHookDirectories(): Promise<void> {
  const hookDirs = [
    '.roo/hooks/tool-execution',
    '.roo/hooks/user-interaction', 
    '.roo/hooks/workflow',
    '.roo/hooks/system-events'
  ];
  
  for (const dir of hookDirs) {
    await fs.mkdir(dir, { recursive: true });
  }
}
```

### Hook Discovery
The HookManager scans the hook directories for Python files and parses their metadata:

```typescript
async function discoverHooks(): Promise<HookMetadata[]> {
  const hooks: HookMetadata[] = [];
  const hookDirs = await fs.readdir('.roo/hooks', { withFileTypes: true });
  
  for (const dir of hookDirs) {
    if (dir.isDirectory()) {
      const hookFiles = await fs.readdir(path.join('.roo/hooks', dir.name));
      for (const file of hookFiles) {
        if (file.endsWith('.py')) {
          const metadata = await parseHookMetadata(path.join('.roo/hooks', dir.name, file));
          if (metadata) {
            hooks.push(metadata);
          }
        }
      }
    }
  }
  
  return hooks;
}
```

## Integration Points

### 1. executeCommandTool Integration
```typescript
// In executeCommandTool.ts
import { HookManager } from '../hooks/HookManager';

export async function executeCommandTool(params: ExecuteCommandParams): Promise<ExecuteCommandResult> {
  const hookManager = HookManager.getInstance();
  
  // Execute BEFORE_EXECUTE_COMMAND hooks
  await hookManager.executeHooks(HookType.BEFORE_EXECUTE_COMMAND, {
    command: params.command,
    workingDirectory: params.cwd,
    environment: process.env
  });
  
  try {
    const result = await executeCommand(params);
    
    // Execute AFTER_EXECUTE_COMMAND hooks
    await hookManager.executeHooks(HookType.AFTER_EXECUTE_COMMAND, {
      command: params.command,
      exitCode: result.exitCode,
      output: result.output,
      duration: result.duration
    });
    
    return result;
  } catch (error) {
    throw error;
  }
}
```

### 2. User Approval Hook Integration
```typescript
// In ChatView.tsx
import { HookManager } from '../../core/hooks/HookManager';

const handleApproval = async (toolName: string, params: any) => {
  const hookManager = HookManager.getInstance();
  
  // Execute BEFORE_ASK_APPROVAL hooks
  const beforeResult = await hookManager.executeHooks(HookType.BEFORE_ASK_APPROVAL, {
    toolName,
    parameters: params,
    timestamp: Date.now()
  });
  
  // Check if hooks returned auto-approval decision
  if (beforeResult.autoApprove) {
    await hookManager.executeHooks(HookType.APPROVAL_GRANTED, {
      toolName,
      parameters: params,
      autoApproved: true
    });
    return true;
  }
  
  // Continue with normal approval flow
  const userApproval = await showApprovalDialog(toolName, params);
  
  if (userApproval) {
    await hookManager.executeHooks(HookType.APPROVAL_GRANTED, {
      toolName,
      parameters: params,
      autoApproved: false
    });
  } else {
    await hookManager.executeHooks(HookType.APPROVAL_DENIED, {
      toolName,
      parameters: params,
      denialReason: 'user_rejected'
    });
  }
  
  return userApproval;
}
```

This simplified file-based approach provides a powerful and flexible foundation for automating complex workflows while maintaining simplicity and user control.