# Database Schema Test Scenarios

## TDD Test List - Comprehensive Coverage

### Core Schema Tests

#### 1. Projects Table Tests
- [ ] **Create project with valid data**
  - Should accept name, path, description, settings
  - Should auto-generate UUID, timestamps
  - Should enforce unique constraints on name and path
  
- [ ] **Project validation constraints**
  - Should reject empty name or path
  - Should reject duplicate names
  - Should reject duplicate paths
  - Should accept valid JSON in settings and metadata fields
  - Should reject invalid JSON in settings field

- [ ] **Project relationships**
  - Should allow deletion when no conversations exist
  - Should prevent deletion when conversations exist (CASCADE test)
  - Should update updated_at on modification

#### 2. Conversations Table Tests
- [ ] **Create conversation with valid data**
  - Should accept project_id, file_path, title
  - Should auto-generate UUID and timestamps
  - Should enforce foreign key to projects table
  
- [ ] **Conversation validation constraints**
  - Should reject invalid project_id references
  - Should enforce unique file_path constraint
  - Should accept null title (auto-generated)
  - Should default message_count to 0

- [ ] **Conversation cascade behavior**
  - Should be deleted when parent project is deleted
  - Should delete all child messages when conversation deleted

#### 3. Messages Table Tests
- [ ] **Create message with valid data**
  - Should accept conversation_id, role, content, timestamp
  - Should auto-generate UUID
  - Should enforce foreign key to conversations table
  
- [ ] **Message validation constraints**
  - Should reject invalid conversation_id references
  - Should enforce role enum ('user', 'assistant')
  - Should reject empty content
  - Should accept positive token_count values
  - Should reject negative token_count values

- [ ] **Message threading**
  - Should accept null parent_id for root messages
  - Should accept valid parent_id for threaded messages
  - Should reject invalid parent_id references
  - Should calculate depth correctly based on parent chain

#### 4. Tool Calls Table Tests
- [ ] **Create tool call with valid data**
  - Should accept message_id, tool_name, input_data, output_data
  - Should auto-generate ID and timestamps
  - Should enforce foreign key to messages table
  
- [ ] **Tool call validation**
  - Should reject invalid message_id references
  - Should require non-empty tool_name
  - Should accept valid JSON in input_data and output_data
  - Should reject negative execution_time values

### Performance Tests

#### 5. Index Performance Tests
- [ ] **Query performance validation**
  - Should execute conversation lookup by project_id in < 50ms
  - Should execute message lookup by conversation_id in < 50ms
  - Should execute message search by timestamp range in < 100ms
  - Should execute tool_calls lookup by message_id in < 50ms

- [ ] **Bulk operations performance**
  - Should handle 1000 message inserts in < 5 seconds
  - Should handle 100 conversation inserts in < 1 second
  - Should maintain performance with 10K+ messages per conversation

#### 6. Full-Text Search Tests
- [ ] **Search functionality**
  - Should find messages containing specific terms
  - Should support phrase searches with quotes
  - Should support boolean operators (AND, OR, NOT)
  - Should return ranked results
  - Should perform searches in < 500ms on 100K+ messages

### Security Tests

#### 7. Row Level Security Tests
- [ ] **RLS policy enforcement**
  - Should enforce user-based data isolation
  - Should prevent cross-user data access
  - Should allow proper data access for authenticated users
  - Should deny access for unauthenticated requests

- [ ] **API security**
  - Should validate API keys properly
  - Should reject invalid or expired tokens
  - Should enforce rate limiting on database operations

### Integration Tests

#### 8. Real-time Subscription Tests
- [ ] **Supabase Realtime integration**
  - Should emit events on message inserts
  - Should emit events on conversation updates
  - Should filter events properly based on user permissions
  - Should handle subscription lifecycle correctly

#### 9. Migration Tests
- [ ] **Schema migration validation**
  - Should apply all migrations without errors
  - Should be idempotent (safe to run multiple times)
  - Should preserve existing data during upgrades
  - Should validate schema constraints after migration

### Data Integrity Tests

#### 10. Transaction Tests
- [ ] **ACID compliance**
  - Should maintain data consistency during concurrent operations
  - Should roll back properly on constraint violations
  - Should handle deadlock scenarios gracefully

#### 11. Constraint Validation Tests
- [ ] **Foreign key constraints**
  - Should prevent orphaned conversations
  - Should prevent orphaned messages
  - Should prevent orphaned tool_calls
  - Should cascade deletes properly

- [ ] **Check constraints**
  - Should enforce valid timestamp ranges
  - Should enforce valid message roles
  - Should enforce positive numeric values
  - Should enforce non-empty string values

### Analytics Tests

#### 12. Aggregation Tests
- [ ] **Conversation metrics**
  - Should calculate message counts correctly
  - Should calculate conversation durations accurately
  - Should aggregate tool usage statistics properly

- [ ] **Performance analytics**
  - Should generate project analytics in < 1 second
  - Should handle large dataset aggregations efficiently
  - Should provide accurate tool performance metrics

### Backup and Recovery Tests

#### 13. Data Protection Tests
- [ ] **Backup functionality**
  - Should create consistent database backups
  - Should restore from backups successfully
  - Should validate backup integrity

### Load Testing

#### 14. Scalability Tests
- [ ] **High-volume operations**
  - Should handle 100 concurrent users
  - Should process 1000+ messages per second
  - Should maintain response times under load
  - Should scale to 1M+ messages per project

#### 15. Memory and Storage Tests
- [ ] **Resource utilization**
  - Should optimize memory usage for large queries
  - Should manage storage growth efficiently
  - Should clean up temporary objects properly

## Test Data Scenarios

### Representative Data Sets
1. **Small Project**: 10 conversations, 100 messages total
2. **Medium Project**: 100 conversations, 10K messages total  
3. **Large Project**: 1000 conversations, 1M messages total
4. **Mixed Usage**: Projects with varying conversation sizes
5. **Heavy Tool Usage**: Conversations with 50+ tool calls per message

### Edge Cases
1. **Empty Projects**: Projects with no conversations
2. **Long Conversations**: Single conversations with 10K+ messages
3. **Deep Threading**: Message threads 50+ levels deep
4. **Large Messages**: Messages with 100KB+ content
5. **Unicode Content**: Messages with emoji, special characters, multiple languages

### Error Scenarios
1. **Constraint Violations**: Duplicate keys, invalid references
2. **Resource Limits**: Connection pool exhaustion, memory limits
3. **Network Issues**: Connection timeouts, intermittent failures
4. **Concurrent Access**: Race conditions, deadlock scenarios

## Test Implementation Strategy

### Phase 1: Core Schema Tests (Week 1)
- Focus on basic CRUD operations and constraints
- Validate foreign key relationships
- Test basic performance requirements

### Phase 2: Performance and Security Tests (Week 1-2)
- Implement index performance validation
- Add RLS policy tests
- Validate search functionality

### Phase 3: Integration and Load Tests (Week 2-3) 
- Test Supabase Realtime integration
- Add bulk operation tests
- Implement scalability validation

### Phase 4: Advanced Features (Week 3-4)
- Analytics and aggregation tests
- Backup/recovery validation
- Production readiness checks

## Success Criteria

### Functional Requirements
- All CRUD operations work correctly
- Foreign key relationships maintained
- Constraints properly enforced
- Search functionality operational

### Performance Requirements
- Query response times < 100ms (95th percentile)
- Bulk operations meet throughput targets
- Search queries complete in < 500ms
- Memory usage stays within acceptable limits

### Security Requirements
- RLS policies prevent unauthorized access
- Data isolation works correctly
- API authentication validates properly
- Audit logs capture all required events

### Reliability Requirements
- Schema migrations are idempotent
- Backup/restore works correctly
- System handles concurrent load
- Graceful error handling for all edge cases