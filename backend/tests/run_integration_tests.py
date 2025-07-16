#!/usr/bin/env python3
"""
Integration test runner for Claude Code Observatory file monitoring system.

Executes comprehensive test suites and generates performance reports
to validate the system meets all requirements.
"""

import asyncio
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Any

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


class IntegrationTestRunner:
    """Comprehensive integration test runner."""

    def __init__(self):
        self.test_results = {}
        self.performance_data = {}
        self.start_time = None

    def run_all_tests(self):
        """Run all integration test suites and collect results."""
        print("🚀 Starting Claude Code Observatory Integration Test Suite")
        print("=" * 70)

        self.start_time = time.time()

        # Test suites to run
        test_suites = [
            ("Contract Validation", self._run_contract_tests),
            ("File Monitoring Integration", self._run_integration_tests),
            ("Performance Benchmarks", self._run_performance_tests),
            ("Database Schema Validation", self._run_database_tests),
            ("Error Handling & Recovery", self._run_error_tests),
        ]

        # Run each test suite
        for suite_name, test_function in test_suites:
            print(f"\n📋 Running {suite_name}...")
            try:
                result = test_function()
                self.test_results[suite_name] = result
                self._print_suite_result(suite_name, result)
            except Exception as e:
                self.test_results[suite_name] = {
                    "status": "failed",
                    "error": str(e),
                    "tests_passed": 0,
                    "tests_failed": 1,
                    "duration": 0,
                }
                print(f"❌ {suite_name} failed with error: {e}")

        # Generate final report
        self._generate_final_report()

    def _run_contract_tests(self) -> Dict[str, Any]:
        """Run contract validation tests."""
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            "tests/test_contracts.py",
            "-v",
            "--tb=short",
            "--json-report",
            "--json-report-file=test_results_contracts.json",
        ]

        return self._execute_pytest_command(cmd, "test_results_contracts.json")

    def _run_integration_tests(self) -> Dict[str, Any]:
        """Run comprehensive integration tests."""
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            "tests/test_file_monitoring_integration.py",
            "-v",
            "--tb=short",
            "-m",
            "integration",
            "--json-report",
            "--json-report-file=test_results_integration.json",
        ]

        return self._execute_pytest_command(cmd, "test_results_integration.json")

    def _run_performance_tests(self) -> Dict[str, Any]:
        """Run performance benchmark tests."""
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            "tests/test_performance_benchmarks.py",
            "-v",
            "--tb=short",
            "-m",
            "performance",
            "--json-report",
            "--json-report-file=test_results_performance.json",
        ]

        result = self._execute_pytest_command(cmd, "test_results_performance.json")

        # Extract performance metrics if available
        self._extract_performance_metrics(result)

        return result

    def _run_database_tests(self) -> Dict[str, Any]:
        """Run database schema validation tests."""
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            "tests/test_database_schema.py",
            "-v",
            "--tb=short",
            "--json-report",
            "--json-report-file=test_results_database.json",
        ]

        return self._execute_pytest_command(cmd, "test_results_database.json")

    def _run_error_tests(self) -> Dict[str, Any]:
        """Run error handling and recovery tests."""
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            "tests/test_file_monitoring_integration.py::TestFileMonitoringErrorScenarios",
            "-v",
            "--tb=short",
            "--json-report",
            "--json-report-file=test_results_errors.json",
        ]

        return self._execute_pytest_command(cmd, "test_results_errors.json")

    def _execute_pytest_command(self, cmd: List[str], json_file: str) -> Dict[str, Any]:
        """Execute a pytest command and parse results."""
        start_time = time.time()

        try:
            # Change to backend directory for test execution
            result = subprocess.run(
                cmd,
                cwd=backend_dir,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            duration = time.time() - start_time

            # Parse JSON results if available
            json_path = backend_dir / json_file
            if json_path.exists():
                with open(json_path) as f:
                    json_results = json.load(f)

                return {
                    "status": "passed" if result.returncode == 0 else "failed",
                    "tests_passed": json_results.get("summary", {}).get("passed", 0),
                    "tests_failed": json_results.get("summary", {}).get("failed", 0),
                    "tests_skipped": json_results.get("summary", {}).get("skipped", 0),
                    "duration": duration,
                    "output": result.stdout,
                    "errors": result.stderr,
                    "detailed_results": json_results,
                }
            else:
                # Fallback parsing from stdout
                return {
                    "status": "passed" if result.returncode == 0 else "failed",
                    "tests_passed": result.stdout.count(" PASSED"),
                    "tests_failed": result.stdout.count(" FAILED"),
                    "tests_skipped": result.stdout.count(" SKIPPED"),
                    "duration": duration,
                    "output": result.stdout,
                    "errors": result.stderr,
                }

        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "tests_passed": 0,
                "tests_failed": 1,
                "duration": 300,
                "output": "",
                "errors": "Test suite timed out after 5 minutes",
            }
        except Exception as e:
            return {
                "status": "error",
                "tests_passed": 0,
                "tests_failed": 1,
                "duration": time.time() - start_time,
                "output": "",
                "errors": str(e),
            }

    def _extract_performance_metrics(self, result: Dict[str, Any]):
        """Extract performance metrics from test output."""
        output = result.get("output", "")

        # Parse performance results from test output
        performance_patterns = [
            ("Single File Latency", "Average: ", "ms"),
            ("Concurrent Processing", "Throughput: ", " files/sec"),
            ("Large Content Processing", "Average processing time: ", "ms"),
            ("Memory Usage", "Total growth: ", "MB"),
        ]

        for metric_name, pattern, unit in performance_patterns:
            try:
                start_idx = output.find(pattern)
                if start_idx != -1:
                    start_idx += len(pattern)
                    end_idx = output.find(unit, start_idx)
                    if end_idx != -1:
                        value_str = output[start_idx:end_idx].strip()
                        self.performance_data[metric_name] = float(value_str)
            except (ValueError, IndexError):
                continue

    def _print_suite_result(self, suite_name: str, result: Dict[str, Any]):
        """Print formatted result for a test suite."""
        status = result["status"]
        passed = result["tests_passed"]
        failed = result["tests_failed"]
        duration = result["duration"]

        if status == "passed":
            status_icon = "✅"
        elif status == "failed":
            status_icon = "❌"
        elif status == "timeout":
            status_icon = "⏰"
        else:
            status_icon = "⚠️"

        print(
            f"{status_icon} {suite_name}: {passed} passed, {failed} failed ({duration:.2f}s)"
        )

        if failed > 0 and "errors" in result:
            print(f"   Errors: {result['errors'][:200]}...")

    def _generate_final_report(self):
        """Generate comprehensive final test report."""
        total_time = time.time() - self.start_time

        print("\n" + "=" * 70)
        print("📊 FINAL INTEGRATION TEST REPORT")
        print("=" * 70)

        # Overall statistics
        total_passed = sum(r["tests_passed"] for r in self.test_results.values())
        total_failed = sum(r["tests_failed"] for r in self.test_results.values())
        total_tests = total_passed + total_failed

        print(f"📈 Overall Results:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {total_passed}")
        print(f"   Failed: {total_failed}")
        print(
            f"   Success Rate: {(total_passed/total_tests*100):.1f}%"
            if total_tests > 0
            else "   Success Rate: N/A"
        )
        print(f"   Total Duration: {total_time:.2f}s")

        # Suite breakdown
        print(f"\n📋 Test Suite Breakdown:")
        for suite_name, result in self.test_results.items():
            status = "✅" if result["status"] == "passed" else "❌"
            print(
                f"   {status} {suite_name}: {result['tests_passed']}/{result['tests_passed'] + result['tests_failed']}"
            )

        # Performance summary
        if self.performance_data:
            print(f"\n⚡ Performance Summary:")
            for metric_name, value in self.performance_data.items():
                print(f"   {metric_name}: {value}")

        # SLA compliance check
        self._check_sla_compliance()

        # Generate detailed JSON report
        self._save_detailed_report()

        # Final status
        all_passed = all(r["status"] == "passed" for r in self.test_results.values())
        if all_passed and total_failed == 0:
            print(f"\n🎉 ALL TESTS PASSED! System is ready for deployment.")
            exit_code = 0
        else:
            print(f"\n⚠️  Some tests failed. Review errors before deployment.")
            exit_code = 1

        print("=" * 70)
        return exit_code

    def _check_sla_compliance(self):
        """Check if system meets SLA requirements."""
        print(f"\n🎯 SLA Compliance Check:")

        sla_requirements = {
            "Detection Latency": {
                "threshold": 100.0,
                "unit": "ms",
                "metric": "Single File Latency",
            },
            "Processing Throughput": {
                "threshold": 5.0,
                "unit": "files/sec",
                "metric": "Concurrent Processing",
            },
            "Memory Growth": {
                "threshold": 50.0,
                "unit": "MB",
                "metric": "Memory Usage",
            },
        }

        for sla_name, config in sla_requirements.items():
            metric_value = self.performance_data.get(config["metric"])
            if metric_value is not None:
                if sla_name == "Processing Throughput":
                    compliant = metric_value >= config["threshold"]
                else:
                    compliant = metric_value <= config["threshold"]

                status = "✅" if compliant else "❌"
                print(
                    f"   {status} {sla_name}: {metric_value}{config['unit']} (limit: {config['threshold']}{config['unit']})"
                )
            else:
                print(f"   ⚠️  {sla_name}: No data available")

    def _save_detailed_report(self):
        """Save detailed JSON report."""
        report = {
            "timestamp": time.time(),
            "total_duration": time.time() - self.start_time,
            "test_results": self.test_results,
            "performance_data": self.performance_data,
            "summary": {
                "total_tests": sum(
                    r["tests_passed"] + r["tests_failed"]
                    for r in self.test_results.values()
                ),
                "total_passed": sum(
                    r["tests_passed"] for r in self.test_results.values()
                ),
                "total_failed": sum(
                    r["tests_failed"] for r in self.test_results.values()
                ),
                "all_passed": all(
                    r["status"] == "passed" for r in self.test_results.values()
                ),
            },
        }

        report_file = backend_dir / "integration_test_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Detailed report saved to: {report_file}")


def main():
    """Main entry point for integration test runner."""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Claude Code Observatory Integration Test Runner")
        print("Usage: python run_integration_tests.py")
        print("\nEnvironment variables:")
        print("  TEST_DB_HOST - Test database host (default: localhost)")
        print("  TEST_DB_PORT - Test database port (default: 54322)")
        print("  TEST_DB_USER - Test database user (default: postgres)")
        print("  TEST_DB_PASSWORD - Test database password (default: postgres)")
        return 0

    # Check prerequisites
    print("🔍 Checking prerequisites...")

    # Check Python packages
    required_packages = ["pytest", "asyncio", "asyncpg", "watchdog", "supabase"]
    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Install with: pip install " + " ".join(missing_packages))
        return 1

    # Check test database connection
    print("🔗 Checking test database connection...")
    try:
        import asyncpg

        async def check_db():
            conn = await asyncpg.connect(
                host=os.getenv("TEST_DB_HOST", "localhost"),
                port=int(os.getenv("TEST_DB_PORT", "54322")),
                user=os.getenv("TEST_DB_USER", "postgres"),
                password=os.getenv("TEST_DB_PASSWORD", "postgres"),
                database=os.getenv("TEST_DB_NAME", "postgres"),
            )
            await conn.close()

        asyncio.run(check_db())
        print("✅ Database connection successful")

    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("Ensure test database is running and accessible")
        return 1

    # Run integration tests
    runner = IntegrationTestRunner()
    exit_code = runner.run_all_tests()

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
