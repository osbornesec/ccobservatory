# Claude Code Observatory - Integration Test Suite

This directory contains comprehensive integration tests for the file monitoring system, validating end-to-end functionality, performance requirements, and error handling capabilities.

## Test Structure

### Core Test Files

- **`test_contracts.py`** - Validates Pydantic data contracts and schema compliance
- **`test_file_monitoring_integration.py`** - End-to-end integration tests for the complete pipeline
- **`test_performance_benchmarks.py`** - Performance validation tests for <100ms SLA requirements
- **`test_database_schema.py`** - Database schema validation and constraint testing
- **`conftest.py`** - Pytest configuration and shared fixtures

### Test Runner

- **`run_integration_tests.py`** - Comprehensive test runner that executes all test suites and generates reports

## Running Tests

### Quick Start

```bash
# Run all integration tests
cd backend/tests
python run_integration_tests.py

# Run specific test suites
pytest test_file_monitoring_integration.py -v
pytest test_performance_benchmarks.py -v -m performance
pytest test_contracts.py -v
```

### Test Categories

#### Integration Tests
```bash
pytest -m integration -v
```
Tests the complete file monitoring pipeline: file events → parsing → database storage

#### Performance Tests
```bash
pytest -m performance -v
```
Validates <100ms detection latency SLA and throughput requirements

#### Security Tests
```bash
pytest -m security -v
```
Tests security constraints and access controls

### Environment Setup

#### Database Configuration
The tests require a test database. Set these environment variables:

```bash
export TEST_DB_HOST=localhost
export TEST_DB_PORT=54322
export TEST_DB_USER=postgres
export TEST_DB_PASSWORD=postgres
export TEST_DB_NAME=postgres
```

#### Local Supabase (Recommended)
```bash
# Start local Supabase for testing
supabase start
```

## Test Coverage

### File Monitoring System
- [x] ClaudeFileHandler event filtering and processing
- [x] JSONLParser conversation data extraction
- [x] DatabaseWriter storage and relationship management  
- [x] FileMonitor orchestration and coordination
- [x] PerformanceMonitor metrics collection and SLA validation

### Performance Requirements
- [x] <100ms detection latency (95th percentile)
- [x] Concurrent file processing throughput
- [x] Memory usage stability
- [x] Error recovery performance impact

### Error Handling
- [x] Invalid JSON file handling
- [x] Missing required fields validation
- [x] Permission denied scenarios
- [x] Large file processing
- [x] Database connection failures

### Data Integrity
- [x] Conversation and message relationship consistency
- [x] Tool usage extraction and mapping
- [x] Timestamp parsing and validation
- [x] Database constraint enforcement

## Performance Benchmarks

The test suite validates these performance requirements:

| Metric | Requirement | Test Coverage |
|--------|-------------|---------------|
| Detection Latency | <100ms (P95) | ✅ Single file and concurrent load |
| Processing Throughput | >5 files/sec | ✅ Concurrent processing tests |
| Memory Usage | <50MB growth | ✅ Extended operation tests |
| Error Recovery | <120ms avg latency | ✅ Mixed error scenarios |

## Continuous Integration

### GitHub Actions Integration
```yaml
# Example CI configuration
name: Integration Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Start test database
        run: docker run -d -p 54322:5432 -e POSTGRES_PASSWORD=postgres postgres:15
      - name: Run integration tests
        run: python backend/tests/run_integration_tests.py
```

### Local Development
```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-json-report psutil

# Run quick smoke tests
pytest tests/test_contracts.py -v

# Run full integration suite
python run_integration_tests.py
```

## Test Reports

The test runner generates comprehensive reports:

### Console Output
- Real-time test progress and results
- Performance metrics summary
- SLA compliance verification
- Error details and debugging information

### JSON Report
```json
{
  "timestamp": 1643723400.0,
  "total_duration": 45.2,
  "test_results": {
    "Contract Validation": {
      "status": "passed",
      "tests_passed": 15,
      "tests_failed": 0,
      "duration": 2.1
    },
    "File Monitoring Integration": {
      "status": "passed", 
      "tests_passed": 12,
      "tests_failed": 0,
      "duration": 25.8
    }
  },
  "performance_data": {
    "Single File Latency": 42.5,
    "Concurrent Processing": 8.3,
    "Memory Usage": 23.1
  },
  "summary": {
    "total_tests": 27,
    "total_passed": 27,
    "total_failed": 0,
    "all_passed": true
  }
}
```

## Debugging Failed Tests

### Common Issues

1. **Database Connection Errors**
   ```bash
   # Check database is running
   docker ps | grep postgres
   
   # Test connection manually
   psql -h localhost -p 54322 -U postgres
   ```

2. **Performance Test Failures**
   ```bash
   # Run with verbose performance output
   pytest test_performance_benchmarks.py -v -s
   
   # Check system resources
   htop  # Monitor CPU/memory during tests
   ```

3. **File Permission Issues**
   ```bash
   # Ensure test directory is writable
   ls -la /tmp/
   
   # Check Python has file system access
   python -c "import tempfile; print(tempfile.gettempdir())"
   ```

### Verbose Debugging
```bash
# Maximum verbosity and debugging
pytest test_file_monitoring_integration.py -vvv -s --tb=long

# Run single test with debugging
pytest test_file_monitoring_integration.py::TestFileMonitoringIntegration::test_end_to_end_file_processing_pipeline -vvv -s
```

## Contributing

When adding new tests:

1. Follow the existing test structure and naming conventions
2. Add appropriate pytest markers (`@pytest.mark.integration`, `@pytest.mark.performance`)
3. Include comprehensive error scenarios and edge cases
4. Update this README with new test coverage
5. Ensure tests are deterministic and can run in parallel

### Test Quality Guidelines

- **Isolation**: Each test should be independent and not rely on side effects
- **Performance**: Tests should complete within reasonable time limits
- **Reliability**: Tests should pass consistently across different environments
- **Coverage**: Tests should cover both happy path and error scenarios
- **Documentation**: Complex test logic should be well-commented

## Architecture Validation

The integration tests validate this architecture:

```
FileEvent → ClaudeFileHandler → JSONLParser → ConversationData → DatabaseWriter → Supabase
     ↓              ↓              ↓              ↓              ↓
PerformanceMonitor collects metrics at each stage
     ↓
FileMonitor orchestrates and provides health monitoring
```

Each component is tested individually and as part of the complete pipeline to ensure:
- Correct data flow and transformations
- Performance requirements compliance
- Error handling and recovery
- Resource management and cleanup