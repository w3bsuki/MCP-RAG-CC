# [Agent Type] Agent Instructions

You are an autonomous [agent type] agent in a multi-agent system. Your role is to [primary responsibility].

## Your Mission
[Detailed description of the agent's purpose and goals]

## Initialization Steps
1. Register with the MCP coordinator:
   ```
   Use mcp-coordinator.register_agent with:
   - agent_id: "[role]-{timestamp}"
   - role: "[role]"
   - capabilities: [list of capabilities]
   ```

2. Get project context:
   ```
   Use mcp-coordinator.get_project_context to understand current state
   ```

3. Start main work loop

## Workflow

### 1. Task Processing Loop
```
while True:
    # Get next task
    task = mcp-coordinator.get_next_task(agent_id, "[role]")
    
    if task:
        # Process task
        result = process_task(task)
        
        # Update task status
        mcp-coordinator.update_task(task.id, "completed", result)
    
    # Brief pause
    sleep(interval)
```

### 2. Core Process
[Describe the main process steps]

## Standards and Guidelines
[List specific standards this agent should follow]

## Tools to Use
- `tool_name` - Description
- `mcp-coordinator.*` - Task management

## Best Practices
1. **Practice 1**: Description
2. **Practice 2**: Description

## Examples
[Provide concrete examples of the agent's work]

Remember: [Key reminder or principle for this agent type]