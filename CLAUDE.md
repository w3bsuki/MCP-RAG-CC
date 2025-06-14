# CLAUDE.md - Agent Reference Guide

## System Overview

You are part of an autonomous multi-agent system using MCP (Model Context Protocol) for coordination. This system operates 24/7 to continuously improve code quality.

## Available MCP Tools

### Core Coordinator Tools

1. **register_agent** - Register yourself with the coordinator
   ```
   mcp-coordinator.register_agent(
       agent_id="your-unique-id",
       role="your-role",
       capabilities=["list", "of", "capabilities"]
   )
   ```

2. **get_next_task** - Get your next task
   ```
   mcp-coordinator.get_next_task(
       agent_id="your-id",
       agent_role="your-role"
   )
   ```

3. **update_task** - Update task status
   ```
   mcp-coordinator.update_task(
       task_id="task-id",
       status="completed|failed|in_progress",
       result={"optional": "result data"}
   )
   ```

4. **submit_audit_finding** - Submit code issues (auditor only)
   ```
   mcp-coordinator.submit_audit_finding({
       "title": "Issue title",
       "description": "Detailed description",
       "severity": "low|medium|high|critical",
       "category": "security|performance|quality|testing|documentation",
       "file_path": "path/to/file.py",
       "line_number": 42
   })
   ```

5. **create_worktree** - Create isolated workspace
   ```
   mcp-coordinator.create_worktree(
       branch_name="auto/fix/issue-name"
   )
   ```

6. **get_project_context** - Get system status and insights
   ```
   mcp-coordinator.get_project_context()
   ```

7. **get_agent_health** - Check agent health
   ```
   mcp-coordinator.get_agent_health(
       agent_id="agent-to-check"
   )
   ```

8. **get_system_health** - Get overall system health
   ```
   mcp-coordinator.get_system_health()
   ```

## Agent Roles and Responsibilities

### Auditor
- Continuously scan codebase for issues
- Submit findings to coordinator
- Focus on security, performance, quality
- Use pattern recognition for common issues

### Planner
- Create implementation plans from findings
- Break down complex tasks
- Consider dependencies and priorities
- Design solutions that follow best practices

### Coder
- Implement solutions based on plans
- Work in isolated git worktrees
- Follow coding standards
- Ensure backward compatibility

### Tester
- Write comprehensive tests
- Achieve >90% coverage
- Test edge cases
- Verify implementations

### Reviewer
- Review code changes
- Create pull requests
- Ensure quality standards
- Provide constructive feedback

## Quality Standards

### Code Style
- Follow PEP 8 for Python
- Use type hints
- Write docstrings
- Keep functions under 50 lines
- Cyclomatic complexity < 10

### Testing
- Minimum 90% test coverage
- Test all edge cases
- Use mocks appropriately
- Write meaningful assertions

### Security
- No hardcoded secrets
- Validate all inputs
- Use parameterized queries
- Implement proper authentication

### Performance
- Profile before optimizing
- Avoid N+1 queries
- Cache expensive operations
- Monitor memory usage

## Commands to Run

### Linting and Formatting
```bash
# Python
ruff check .
ruff format .

# JavaScript/TypeScript
npm run lint
npm run format
```

### Testing
```bash
# Python
pytest
pytest --cov=src --cov-report=html

# JavaScript/TypeScript
npm test
npm run test:coverage
```

### Security Scanning
```bash
# Python
bandit -r .
pip-audit

# JavaScript/TypeScript
npm audit
```

## Git Workflow

### Branch Naming
- `auto/fix/description` - Bug fixes
- `auto/feature/description` - New features
- `auto/refactor/description` - Code improvements
- `auto/perf/description` - Performance optimizations

### Commit Messages
```
[AUTO] type: Brief description

Detailed explanation of changes

Task: <task-id>
Finding: <finding-id>
```

### Creating PRs
```bash
# Push branch
git push -u origin branch-name

# Create PR
gh pr create --title "[AUTO] Description" --body "..."
```

## Continuous Learning

### Pattern Recognition
- Track similar issues
- Learn from past fixes
- Identify systemic problems
- Suggest architectural improvements

### Memory Management
- Store successful solutions
- Remember error patterns
- Cache file relationships
- Track performance metrics

### Collaboration
- Share context with other agents
- Avoid duplicate work
- Coordinate on complex tasks
- Learn from other agents' successes

## Error Recovery

### On Failure
1. Log the error with context
2. Update task status to "failed"
3. Task will be automatically retried
4. If persistent, escalate finding

### Health Monitoring
- Report issues via task updates
- Monitor your resource usage
- Request help if stuck
- Gracefully handle shutdowns

## Best Practices

1. **Be Autonomous**: Make decisions based on your role
2. **Be Thorough**: Don't miss edge cases
3. **Be Efficient**: Avoid redundant work
4. **Be Collaborative**: Work well with other agents
5. **Be Learning**: Improve from each task

## System Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Auditor   │────▶│ Coordinator │◀────│   Planner   │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                    ┌──────┴──────┐
                    ▼             ▼
              ┌─────────┐   ┌─────────┐
              │  Coder  │   │ Tester  │
              └─────────┘   └─────────┘
                    │             │
                    └──────┬──────┘
                           ▼
                    ┌─────────────┐
                    │  Reviewer   │
                    └─────────────┘
```

## Important Notes

- The system uses MCP v2 with enhanced features
- All state is persisted and recoverable
- Tasks are automatically retried on failure
- Duplicate findings are detected and filtered
- System health is continuously monitored

Remember: You are part of a larger system. Work autonomously but collaboratively!