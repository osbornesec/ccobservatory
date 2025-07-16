# Main Page Component Test Scenarios

## Canon TDD Test List for +page.svelte

### Test Target
- **Component**: `/home/michael/dev/ccobservatory/frontend/src/routes/+page.svelte`
- **Coverage Goal**: +35 points toward 90% frontend coverage
- **Testing Framework**: Vitest + @testing-library/svelte
- **Key Behaviors**: Data loading, WebSocket integration, error handling, reactive updates

### Test Scenarios (Canon TDD Format)

#### 1. Initial Render & Layout Structure

**Test 1.1**: ✅ Page renders with correct HTML structure
- **Behavior**: Component mounts and displays basic layout elements
- **Expected**: Header, Sidebar, and main content area are present in DOM
- **Query Strategy**: `getByRole('banner')`, `getByRole('navigation')`, `getByRole('main')`
- **Status**: COMPLETE - Tests essential navigation landmarks for screen reader accessibility

**Test 1.2**: ✅ Page title and meta description are set correctly  
- **Behavior**: Svelte head block sets document title and meta tags
- **Expected**: Document title is "Claude Code Observatory" and meta description exists
- **Query Strategy**: Direct document queries for title and meta elements
- **Status**: COMPLETE - Tests descriptive page title and meta description for user orientation

**Test 1.3**: ✅ Welcome section displays correct content
- **Behavior**: Static welcome message and description are shown
- **Expected**: H1 contains "Welcome to Claude Code Observatory" and description paragraph exists
- **Query Strategy**: `getByRole('heading', {level: 1})`, `getByText(/Monitor and analyze/)`
- **Status**: COMPLETE - REFACTORED - Tests welcome section with clear application identification and value proposition

#### 2. Loading States & Data Initialization

**Test 2.1**: Shows loading spinner during initial data fetch
- **Behavior**: Component displays loading state immediately on mount
- **Expected**: Loading spinner with "Loading dashboard..." text is visible
- **Query Strategy**: `getByText('Loading dashboard...')`, `getByRole('status')`

**Test 2.2**: Calls API connection test on mount
- **Behavior**: onMount triggers apiClient.testConnection()
- **Expected**: API connection test method is called once
- **Mocking**: Mock apiClient with successful connection response

**Test 2.3**: Loads projects data during initialization
- **Behavior**: After successful connection test, getProjects() is called
- **Expected**: Projects data is fetched and stored in projects store
- **Mocking**: Mock apiClient.getProjects() with sample project data

**Test 2.4**: Loads conversations data during initialization
- **Behavior**: getConversations(1, 10) is called to fetch recent conversations
- **Expected**: Recent conversations are fetched and stored in conversations store
- **Mocking**: Mock apiClient.getConversations() with sample conversation data

**Test 2.5**: Loads analytics data during initialization
- **Behavior**: getAnalytics() is called to fetch dashboard metrics
- **Expected**: Analytics data is fetched and component analytics state is updated
- **Mocking**: Mock apiClient.getAnalytics() with sample analytics data

#### 3. Error Handling & Recovery

**Test 3.1**: Shows error message when API connection fails
- **Behavior**: When testConnection() rejects, error state is displayed
- **Expected**: Error message component shows "Cannot connect to backend API"
- **Query Strategy**: `getByText(/Cannot connect to backend API/)`, `getByRole('alert')`

**Test 3.2**: Shows error message when data loading fails
- **Behavior**: When any loadData() call fails, generic error message is shown
- **Expected**: Error message shows "Failed to load data from server"
- **Query Strategy**: `getByText(/Failed to load data from server/)`

**Test 3.3**: Error message includes retry button
- **Behavior**: Error state displays functional retry action
- **Expected**: "Retry" button is present and clickable
- **Query Strategy**: `getByRole('button', {name: /retry/i})`

**Test 3.4**: Retry button triggers data reload
- **Behavior**: Clicking retry button calls loadData() again
- **Expected**: Loading state returns, error clears, data fetch is attempted
- **User Event**: Click retry button, verify loading state and API calls

**Test 3.5**: Retry handles subsequent failures gracefully
- **Behavior**: If retry also fails, error state returns with new error message
- **Expected**: Error persists, loading state ends, no infinite retry loops
- **Mocking**: Mock API failure on both initial and retry attempts

#### 4. Analytics Display & Formatting

**Test 4.1**: Total conversations metric displays correctly
- **Behavior**: Analytics data populates conversation count card
- **Expected**: Card shows correct number with "Total Conversations" label
- **Query Strategy**: `getByText('Total Conversations')`, verify adjacent number

**Test 4.2**: Total messages metric displays correctly
- **Behavior**: Analytics data populates message count card
- **Expected**: Card shows correct number with "Total Messages" label
- **Query Strategy**: `getByText('Total Messages')`, verify adjacent number

**Test 4.3**: Tool calls metric displays correctly
- **Behavior**: Analytics data populates tool usage card
- **Expected**: Card shows correct number with "Tool Calls" label
- **Query Strategy**: `getByText('Tool Calls')`, verify adjacent number

**Test 4.4**: Average conversation length is rounded correctly
- **Behavior**: Decimal avg_conversation_length is rounded to integer
- **Expected**: Math.round() is applied, displayed as whole number
- **Test Data**: Provide 15.7 as input, expect "16" to be displayed

**Test 4.5**: Analytics cards display appropriate icons
- **Behavior**: Each metric card shows corresponding Lucide icon
- **Expected**: MessageSquare, Activity, TrendingUp, Clock icons are present
- **Query Strategy**: Verify icon components are rendered (test-id or class-based)

#### 5. WebSocket Integration & Real-time Updates

**Test 5.1**: WebSocket conversation update handler is registered on mount
- **Behavior**: onMount sets up 'conversation_update' event listener
- **Expected**: wsClient.on() is called with 'conversation_update' handler
- **Mocking**: Mock wsClient and verify event listener registration

**Test 5.2**: WebSocket project update handler is registered on mount
- **Behavior**: onMount sets up 'project_update' event listener  
- **Expected**: wsClient.on() is called with 'project_update' handler
- **Mocking**: Mock wsClient and verify event listener registration

**Test 5.3**: Conversation updates trigger store updates
- **Behavior**: conversation_update events call conversations.updateConversation()
- **Expected**: Store is updated with new conversation data
- **Simulation**: Trigger WebSocket event, verify store state change

**Test 5.4**: Project updates trigger store updates
- **Behavior**: project_update events update matching project in store
- **Expected**: Projects store is updated with modified project data
- **Simulation**: Trigger WebSocket event, verify store state change

**Test 5.5**: WebSocket connection status is displayed correctly
- **Behavior**: connectionStatus store value determines badge appearance
- **Expected**: "Connected" shows success badge, "Disconnected" shows warning badge
- **Query Strategy**: `getByText('Connected')`, verify badge classes

#### 6. Navigation & User Interactions

**Test 6.1**: View Conversations button navigates correctly
- **Behavior**: Clicking "View Conversations" button navigates to conversations page
- **Expected**: Link href is "/conversations"
- **Query Strategy**: `getByRole('link', {name: 'View Conversations'})`

**Test 6.2**: Settings button navigates correctly
- **Behavior**: Clicking "Settings" button navigates to settings page
- **Expected**: Link href is "/settings"
- **Query Strategy**: `getByRole('link', {name: 'Settings'})`

**Test 6.3**: Getting Started section displays step-by-step instructions
- **Behavior**: Three numbered steps are shown with descriptions
- **Expected**: Badge numbers 1, 2, 3 with corresponding instruction text
- **Query Strategy**: `getByText('1')`, `getByText('2')`, `getByText('3')`

#### 7. Connection Status Display

**Test 7.1**: Backend API connection shows as connected after successful load
- **Behavior**: After successful data loading, API status shows "Connected"
- **Expected**: "Backend API" row shows green "Connected" badge
- **Query Strategy**: Within connection status section, find "Connected" badge

**Test 7.2**: WebSocket connection status reflects store value
- **Behavior**: connectionStatus store determines WebSocket status display
- **Expected**: Status text and badge class change based on store value
- **Store Testing**: Update connectionStatus store, verify DOM changes

**Test 7.3**: File Monitor shows active status
- **Behavior**: File monitor status is hardcoded as "Active"
- **Expected**: "File Monitor" row shows "Active" badge with info styling
- **Query Strategy**: `getByText('File Monitor')`, verify adjacent "Active" text

#### 8. Reactive State Management

**Test 8.1**: Loading state reactively controls content visibility
- **Behavior**: isLoading boolean determines which content section renders
- **Expected**: Only one of loading/error/main content is visible at a time
- **State Testing**: Toggle isLoading, verify conditional rendering

**Test 8.2**: Error state reactively controls content visibility
- **Behavior**: error string presence determines error display
- **Expected**: Error content shows when error exists, hidden when null
- **State Testing**: Set/clear error, verify conditional rendering

**Test 8.3**: Analytics data reactively updates display values
- **Behavior**: Changes to analytics object update displayed metrics
- **Expected**: Metric cards reflect current analytics values
- **State Testing**: Update analytics, verify numbers change in DOM

**Test 8.4**: Store updates trigger reactive DOM changes
- **Behavior**: Changes to projects/conversations stores update component state
- **Expected**: Component re-renders when dependent stores change
- **Store Testing**: Update stores, verify component reflects changes

#### 9. Component Integration & Data Flow

**Test 9.1**: Header component receives correct props
- **Behavior**: Header component is rendered without specific props
- **Expected**: Header component mounts successfully
- **Integration**: Verify Header component is present in DOM

**Test 9.2**: Sidebar component receives correct props
- **Behavior**: Sidebar component is rendered without specific props
- **Expected**: Sidebar component mounts successfully
- **Integration**: Verify Sidebar component is present in DOM

**Test 9.3**: LoadingSpinner receives correct props
- **Behavior**: LoadingSpinner gets size="lg" and text="Loading dashboard..."
- **Expected**: Spinner displays with large size and correct message
- **Prop Testing**: Verify component receives expected props

**Test 9.4**: ErrorMessage receives correct props
- **Behavior**: ErrorMessage gets title, message, and retryAction props
- **Expected**: Error component displays title, message, and functional retry
- **Prop Testing**: Verify all props are passed correctly

#### 10. Edge Cases & Error Boundaries

**Test 10.1**: Handles missing analytics data gracefully
- **Behavior**: When analytics API returns incomplete data, defaults are used
- **Expected**: Zero values or empty strings display without errors
- **Data Testing**: Provide partial analytics object, verify safe rendering

**Test 10.2**: Handles WebSocket connection failures gracefully
- **Behavior**: WebSocket errors don't crash the component
- **Expected**: Component continues to function without real-time updates
- **Error Simulation**: Trigger WebSocket errors, verify component stability

**Test 10.3**: Handles rapid state changes without race conditions
- **Behavior**: Quick loading/error/success transitions work correctly
- **Expected**: Final state is reached without intermediate state conflicts
- **Timing Testing**: Trigger rapid state changes, verify final state

**Test 10.4**: Component unmounts cleanly
- **Behavior**: Component cleanup removes event listeners and cancels requests
- **Expected**: No memory leaks or hanging references after unmount
- **Cleanup Testing**: Mount/unmount component, verify cleanup

#### 11. Accessibility & User Experience

**Test 11.1**: Loading state is announced to screen readers
- **Behavior**: Loading spinner has appropriate ARIA labels
- **Expected**: Screen reader users receive loading status updates
- **A11y Testing**: Verify loading elements have proper ARIA attributes

**Test 11.2**: Error messages are announced to screen readers
- **Behavior**: Error state uses proper ARIA roles and labels
- **Expected**: Error messages are accessible via assistive technology
- **A11y Testing**: Verify error elements have role="alert" or equivalent

**Test 11.3**: Metric cards have appropriate semantic structure
- **Behavior**: Analytics cards use proper heading hierarchy and labels
- **Expected**: Cards are navigable and understandable via keyboard/screen reader
- **A11y Testing**: Verify semantic HTML structure and ARIA labels

**Test 11.4**: Interactive elements are keyboard accessible
- **Behavior**: All buttons and links work with keyboard navigation
- **Expected**: Tab order is logical, Enter/Space activate buttons
- **Keyboard Testing**: Navigate with keyboard, verify all interactions work

#### 12. Performance & Optimization

**Test 12.1**: Component renders efficiently on initial mount
- **Behavior**: Initial render completes without unnecessary re-renders
- **Expected**: Component mounts once and loads data asynchronously
- **Performance**: Verify minimal render cycles during mount

**Test 12.2**: Store subscriptions don't cause excessive re-renders
- **Behavior**: Store changes trigger only necessary component updates
- **Expected**: Component updates only when dependent data changes
- **Performance**: Monitor re-render frequency with store updates

**Test 12.3**: WebSocket events don't block UI thread
- **Behavior**: Real-time updates process without freezing interface
- **Expected**: UI remains responsive during WebSocket message handling
- **Performance**: Verify UI responsiveness during simulated events

### Test Implementation Notes

#### Mocking Strategy
- **API Client**: Mock all apiClient methods with configurable responses
- **WebSocket Client**: Mock wsClient with event simulation capabilities  
- **Stores**: Use actual Svelte stores but with controlled initial states
- **Router**: Mock SvelteKit navigation if testing link behavior

#### Test Data Setup
- **Sample Projects**: Array of project objects with id, name, path
- **Sample Conversations**: Array with id, title, message_count, created_at
- **Sample Analytics**: Object with realistic metric values
- **Error Scenarios**: Various error types and messages for failure testing

#### Reactive Testing Approach
- **Store Updates**: Use store.set() and store.update() to trigger reactivity
- **Async Handling**: Use await act() for complex async state changes
- **Event Simulation**: Use fireEvent for user interactions
- **State Verification**: Query DOM after each state change to verify updates

#### Coverage Strategy
- **Conditional Rendering**: Test all if/else branches in template
- **Event Handlers**: Verify all click and WebSocket event handlers
- **Error Paths**: Test all try/catch blocks and error scenarios
- **Reactive Updates**: Test all reactive statements and store dependencies

This comprehensive test list follows Canon TDD principles by focusing on **behavior over implementation**, providing specific **queryable expectations**, and covering all **user-facing functionality** and **error conditions** for the main page component.