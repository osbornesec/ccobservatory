# Claude Code File System Research

## Directory Structure

Claude Code organizes conversation data in `~/.claude/` with the following structure:

```
~/.claude/
├── projects/                    # Conversation transcripts by project
│   ├── -home-michael-dev-vai/   # Project: /home/michael/dev/vai/
│   ├── -home-michael-dev-ccobservatory/  # Project: /home/michael/dev/ccobservatory/
│   └── -mnt-d-cases/           # Project: /mnt/d/cases/
├── hooks/                      # System hooks and caching
├── todos/                      # Task management files
├── commands/                   # Custom command definitions
└── shell-snapshots/           # Terminal state snapshots
```

### Project Directory Naming

Projects are named by converting the working directory path:
- Leading slash becomes leading dash: `/home/michael/` → `-home-michael/`
- Internal slashes become dashes: `/home/michael/dev/vai/` → `-home-michael-dev-vai/`
- Trailing slashes are omitted

### JSONL File Organization

- **File naming:** `{session-uuid}.jsonl` (e.g., `a0143bf2-168f-4092-83da-758b360f1d47.jsonl`)
- **Current count:** 79 files across all projects
- **Size range:** 90KB to 45MB (largest file has 25,000+ lines)
- **Real-time updates:** Files are appended during active conversations

## JSONL Message Format

### Core Message Structure

Every message includes these base fields:

```json
{
  "type": "user|assistant|system|summary",
  "uuid": "unique-message-id",
  "timestamp": "2025-07-14T19:19:18.739Z",
  "sessionId": "session-uuid",
  "version": "1.0.51",
  "cwd": "/working/directory/path",
  "userType": "external",
  "isSidechain": false,
  "parentUuid": "parent-message-uuid|null"
}
```

### Message Type Details

#### User Messages
```json
{
  "type": "user",
  "message": {
    "role": "user",
    "content": "text or array of content objects"
  },
  "isMeta": true|false,
  // ... base fields
}
```

#### Assistant Messages
```json
{
  "type": "assistant", 
  "message": {
    "id": "msg_xxx",
    "type": "message",
    "role": "assistant",
    "model": "claude-sonnet-4-20250514",
    "content": [
      {"type": "text", "text": "response text"},
      {"type": "tool_use", "id": "tool_id", "name": "ToolName", "input": {...}}
    ],
    "usage": {
      "input_tokens": 3,
      "cache_creation_input_tokens": 63407,
      "cache_read_input_tokens": 0,
      "output_tokens": 5,
      "service_tier": "standard"
    }
  },
  "requestId": "req_xxx",
  // ... base fields
}
```

#### System Messages (Hook execution)
```json
{
  "type": "system",
  "content": "Hook execution info or system message",
  "level": "info",
  "toolUseID": "associated-tool-id",
  "isMeta": false,
  // ... base fields
}
```

#### Tool Results
```json
{
  "type": "system",
  "toolUseResult": {
    "stdout": "command output",
    "stderr": "error output",
    "interrupted": false,
    "isImage": false
  },
  "toolUseID": "tool-use-id",
  // ... base fields
}
```

#### Summary Messages
```json
{
  "type": "summary",
  "summary": "Conversation title/description",
  "leafUuid": "final-message-uuid",
  // ... base fields
}
```

## Message Threading

Messages form conversation trees through `parentUuid` references:
- `parentUuid: null` - Root messages (conversation start)
- `parentUuid: "uuid"` - Replies to specific messages
- Linear flow with branching for tool use/results

## Hook System Integration

The JSONL captures extensive hook execution data:

### Pre-Tool Hooks
- `command-validator.py` - Command validation
- `observability-pre-tool-use.py` - Monitoring
- `intelligent-resource-governor.py` - Resource optimization

### Post-Tool Hooks  
- `error-analyzer.py` - Error analysis
- `adaptive-error-learning-system.py` - Learning from errors
- `context-memory-engine.py` - Context tracking
- `enhanced-observability-post-tool-use.py` - Enhanced monitoring

## Implementation Insights

### File Monitoring Strategy
1. **Watch Pattern:** `~/.claude/projects/**/*.jsonl`
2. **Incremental Reading:** Track file size to read only new lines
3. **Real-time Updates:** Files appended during active conversations
4. **Performance:** Some files >40MB require streaming approach

### Parsing Strategy
1. **Line-by-Line:** Each line is independent JSON
2. **Message Ordering:** Use `timestamp` for chronological sort
3. **Session Grouping:** Group by `sessionId` for conversations
4. **Project Detection:** Extract from file path structure

### Database Design Implications
- Store normalized message data with JSONB for flexibility
- Track token usage across conversations
- Monitor hook performance and errors
- Enable analytics on tool usage patterns
- Support real-time conversation reconstruction

This research provides the foundation for implementing accurate Claude Code conversation monitoring and analysis.