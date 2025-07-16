# Test Coverage 90% Roadmap

## Current Status

### Backend Coverage: 82% → 90% Target (8 points needed)
### Frontend Coverage: 45.68% → 90% Target (44.32 points needed)

---

## Backend Path to 90% Coverage

### Current State
- **Total Coverage**: 82% (764/907 lines)
- **Tests Passing**: 112/163 (69%)
- **Tests Failing**: 15 (mostly Supabase environment issues)
- **Tests Skipped**: 34

### Critical Components Status
- ✅ **WebSocket Handler**: 100% (Perfect)
- ✅ **File Handler**: 93% (Excellent)
- ✅ **Database Writer**: 82% (Good)
- ✅ **File Monitor**: 81% (Good)
- ⚠️ **API Conversations**: 63% (Needs improvement)
- ⚠️ **API Projects**: 63% (Needs improvement)
- ⚠️ **Supabase Client**: 56% (Needs improvement)

### Required Actions for 90% Backend Coverage

#### 1. Fix Environment Configuration (HIGH PRIORITY)
```bash
# Set up Supabase environment variables for integration tests
cp backend/env.template backend/.env
# Configure: SUPABASE_URL, SUPABASE_KEY, SUPABASE_SERVICE_ROLE_KEY
```

#### 2. API Layer Testing (+6 points)
**File: `app/api/conversations.py`**
- Add error handling tests for invalid session IDs
- Test pagination edge cases
- Test query parameter validation
- Test response format validation

**File: `app/api/projects.py`**
- Add error handling tests for invalid project paths
- Test project discovery edge cases
- Test file system permission errors
- Test malformed project metadata

#### 3. Database Client Testing (+5 points)
**File: `app/database/supabase_client.py`**
- Add comprehensive error scenario testing
- Test connection failure handling
- Test authentication failure scenarios
- Test service initialization errors

#### 4. Integration Testing (BONUS)
- Enable end-to-end pipeline tests
- Test complete file monitoring → database → API flow
- Validate performance requirements (<100ms latency)

### Implementation Priority
1. **Environment setup** (1 day)
2. **API error handling tests** (2 days)
3. **Database client completion** (1 day)
4. **Integration testing** (1 day)

---

## Frontend Path to 90% Coverage

### Current State
- **Total Coverage**: 45.68% (614/1,344 lines)
- **Tests Passing**: 120 total tests
- **Primary Blocker**: Zero Svelte component coverage

### Coverage Breakdown
- ✅ **Stores**: 100% (theme.ts, conversations.ts)
- ✅ **Core Library**: 100% (config.ts, supabase.ts)
- ⚠️ **API Client**: 83.91% (nearly complete)
- ⚠️ **WebSocket**: 52.33% (moderate)
- ❌ **Svelte Components**: 0% (491 lines uncovered)
- ❌ **Route Components**: 0% (266 lines uncovered)

### Required Actions for 90% Frontend Coverage

#### 1. Install Component Testing Dependencies
```bash
cd frontend
npm install -D @testing-library/svelte @testing-library/jest-dom @testing-library/user-event
```

#### 2. Svelte Component Testing (+35 points)
**Priority Order:**

**A. Main Page Component (`+page.svelte` - 246 lines)**
- Test data loading states
- Test error handling
- Test WebSocket integration
- Test user interactions
- Test reactive updates

**B. Header Component (`Header.svelte` - 98 lines)**
- Test theme toggle functionality
- Test connection status display
- Test navigation menu
- Test stats display
- Test responsive behavior

**C. Sidebar Component (`Sidebar.svelte` - 87 lines)**
- Test project navigation
- Test route highlighting
- Test project switching
- Test search functionality
- Test icons and styling

**D. Layout Component (`+layout.svelte` - 20 lines)**
- Test component mounting
- Test global state initialization
- Test error boundaries

**E. Utility Components**
- `ErrorMessage.svelte` (22 lines)
- `LoadingSpinner.svelte` (18 lines)

#### 3. API Client Completion (+7 points)
**File: `src/lib/api/client.ts`**
- Complete error handling test coverage
- Test timeout scenarios
- Test retry logic
- Test request/response middleware

#### 4. WebSocket Client Completion (+4 points)
**File: `src/lib/api/websocket.ts`**
- Test browser environment detection
- Test connection lifecycle
- Test message queuing
- Test reconnection logic

### Implementation Priority
1. **Component testing setup** (1 day)
2. **Main page component tests** (2 days)
3. **Header and Sidebar tests** (2 days)
4. **Utility component tests** (1 day)
5. **API client completion** (1 day)

---

## Technical Implementation Details

### Backend Testing Patterns
```python
# API Error Handling Test Example
def test_get_conversations_invalid_session():
    response = client.get("/api/conversations?session_id=invalid")
    assert response.status_code == 404
    assert "Session not found" in response.json()["detail"]

# Database Client Error Test Example
def test_supabase_client_connection_failure():
    with patch('supabase.create_client') as mock_create:
        mock_create.side_effect = Exception("Connection failed")
        with pytest.raises(DatabaseConnectionError):
            SupabaseClient()
```

### Frontend Testing Patterns
```typescript
// Svelte Component Test Example
import { render, screen, fireEvent } from '@testing-library/svelte'
import Header from './Header.svelte'

test('header displays connection status', () => {
  render(Header, {
    props: { connectionStatus: 'connected' }
  })
  expect(screen.getByText('Connected')).toBeInTheDocument()
})

// API Client Test Example
test('handles API timeout errors', async () => {
  vi.mocked(fetch).mockRejectedValueOnce(new Error('timeout'))
  
  await expect(apiClient.getConversations()).rejects.toThrow('timeout')
})
```

---

## Timeline and Milestones

### Week 1: Backend 90% Achievement
- **Day 1**: Environment setup and integration test fixes
- **Day 2-3**: API layer error handling tests
- **Day 4**: Database client completion
- **Day 5**: Integration testing and validation

### Week 2: Frontend 90% Achievement
- **Day 1**: Component testing infrastructure setup
- **Day 2-3**: Main page and header component tests
- **Day 4**: Sidebar and utility component tests
- **Day 5**: API client completion and final validation

### Success Metrics
- **Backend**: 90%+ coverage with all tests passing
- **Frontend**: 90%+ coverage with comprehensive component testing
- **Integration**: End-to-end pipeline validation
- **Performance**: Tests validate <100ms latency requirements

---

## Risk Mitigation

### Backend Risks
- **Environment Configuration**: Have fallback mock implementations
- **Supabase Dependencies**: Ensure proper mocking for CI/CD
- **Integration Complexity**: Break down into smaller testable units

### Frontend Risks
- **Component Testing Complexity**: Start with simple components first
- **SvelteKit Mocking**: Use established patterns from existing tests
- **Browser Environment**: Ensure proper jsdom configuration

---

## Completion Criteria

### Backend (90% Target)
- [ ] All integration tests passing
- [ ] API error handling comprehensive
- [ ] Database client fully tested
- [ ] Performance requirements validated
- [ ] No failing tests

### Frontend (90% Target)
- [ ] All Svelte components tested
- [ ] API client completion
- [ ] WebSocket client completion
- [ ] Component interactions tested
- [ ] User workflows validated

### Quality Gates
- [ ] No regressions in existing functionality
- [ ] All tests follow Canon TDD principles
- [ ] Test execution time <30 seconds
- [ ] Coverage reports generated and accessible
- [ ] Documentation updated with testing patterns