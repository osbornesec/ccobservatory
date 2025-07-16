"""
PerformanceMonitor implementation for tracking system performance metrics.

This module collects, aggregates, and analyzes performance data to ensure
the system meets the <100ms detection latency requirement.
"""

import logging
import statistics
import time
from collections import deque
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from app.models.contracts import PerformanceMetrics, ComponentStatus

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """
    Monitor and analyze system performance metrics.

    Tracks detection latency, processing times, and throughput to ensure
    the system meets performance requirements and provides alerting
    when SLAs are breached.
    """

    def __init__(self, max_samples: int = 1000, sla_threshold_ms: float = 100.0):
        """
        Initialize the performance monitor.

        Args:
            max_samples: Maximum number of samples to keep in memory
            sla_threshold_ms: SLA threshold in milliseconds for detection latency
        """
        self.max_samples = max_samples
        self.sla_threshold_ms = sla_threshold_ms

        # Ring buffers for metrics (FIFO with fixed size)
        self.detection_latencies = deque(maxlen=max_samples)
        self.processing_latencies = deque(maxlen=max_samples)
        self.throughput_samples = deque(maxlen=max_samples)

        # Aggregated statistics
        self.stats = {
            "total_samples": 0,
            "sla_violations": 0,
            "last_reset": datetime.utcnow(),
            "peak_detection_latency_ms": 0.0,
            "peak_processing_latency_ms": 0.0,
            "peak_throughput_msgs_per_sec": 0.0,
        }

        logger.info(f"PerformanceMonitor initialized (SLA: {sla_threshold_ms}ms)")

    def record_metrics(self, metrics: PerformanceMetrics) -> None:
        """
        Record a performance metrics sample.

        Args:
            metrics: PerformanceMetrics object to record
        """
        try:
            # Record individual metrics
            self.detection_latencies.append(metrics.detection_latency_ms)
            self.processing_latencies.append(metrics.processing_latency_ms)
            self.throughput_samples.append(metrics.throughput_msgs_per_sec)

            # Update statistics
            self.stats["total_samples"] += 1

            # Check for SLA violations
            if metrics.detection_latency_ms > self.sla_threshold_ms:
                self.stats["sla_violations"] += 1
                logger.warning(
                    f"SLA violation: Detection latency {metrics.detection_latency_ms:.2f}ms "
                    f"exceeds threshold {self.sla_threshold_ms}ms"
                )

            # Update peak values
            if metrics.detection_latency_ms > self.stats["peak_detection_latency_ms"]:
                self.stats["peak_detection_latency_ms"] = metrics.detection_latency_ms

            if metrics.processing_latency_ms > self.stats["peak_processing_latency_ms"]:
                self.stats["peak_processing_latency_ms"] = metrics.processing_latency_ms

            if (
                metrics.throughput_msgs_per_sec
                > self.stats["peak_throughput_msgs_per_sec"]
            ):
                self.stats["peak_throughput_msgs_per_sec"] = (
                    metrics.throughput_msgs_per_sec
                )

            logger.debug(
                f"Recorded metrics: detection={metrics.detection_latency_ms:.2f}ms, "
                f"processing={metrics.processing_latency_ms:.2f}ms, "
                f"throughput={metrics.throughput_msgs_per_sec:.1f} msg/s"
            )

        except Exception as e:
            logger.error(f"Error recording performance metrics: {e}")

    def get_summary(self) -> Dict[str, any]:
        """
        Get comprehensive performance summary with statistical analysis.

        Returns:
            Dictionary containing performance statistics and analysis
        """
        if not self.detection_latencies:
            return {
                "status": "no_data",
                "message": "No performance data available",
                **self.stats,
            }

        try:
            # Calculate statistics for detection latency
            detection_stats = self._calculate_stats(list(self.detection_latencies))
            processing_stats = self._calculate_stats(list(self.processing_latencies))
            throughput_stats = self._calculate_stats(list(self.throughput_samples))

            # Determine performance status
            sla_compliance_rate = 1.0 - (
                self.stats["sla_violations"] / max(1, self.stats["total_samples"])
            )

            if sla_compliance_rate >= 0.99:  # 99% compliance
                performance_status = ComponentStatus.OK
            elif sla_compliance_rate >= 0.95:  # 95% compliance
                performance_status = ComponentStatus.DEGRADED
            else:
                performance_status = ComponentStatus.UNAVAILABLE

            # Calculate recent trend (last 10% of samples)
            recent_count = max(1, len(self.detection_latencies) // 10)
            recent_latencies = list(self.detection_latencies)[-recent_count:]
            recent_avg = statistics.mean(recent_latencies) if recent_latencies else 0

            return {
                "status": performance_status.value,
                "sla_threshold_ms": self.sla_threshold_ms,
                "sla_compliance_rate": sla_compliance_rate,
                "detection_latency": {
                    **detection_stats,
                    "sla_violations": self.stats["sla_violations"],
                    "recent_avg_ms": recent_avg,
                },
                "processing_latency": processing_stats,
                "throughput": throughput_stats,
                "samples": {
                    "total": self.stats["total_samples"],
                    "current_buffer_size": len(self.detection_latencies),
                    "max_buffer_size": self.max_samples,
                },
                "peaks": {
                    "detection_latency_ms": self.stats["peak_detection_latency_ms"],
                    "processing_latency_ms": self.stats["peak_processing_latency_ms"],
                    "throughput_msgs_per_sec": self.stats[
                        "peak_throughput_msgs_per_sec"
                    ],
                },
                "last_reset": self.stats["last_reset"].isoformat(),
            }

        except Exception as e:
            logger.error(f"Error calculating performance summary: {e}")
            return {
                "status": "error",
                "message": f"Error calculating statistics: {str(e)}",
                **self.stats,
            }

    def _calculate_stats(self, values: List[float]) -> Dict[str, float]:
        """
        Calculate statistical metrics for a list of values.

        Args:
            values: List of numeric values

        Returns:
            Dictionary of statistical metrics
        """
        if not values:
            return {
                "min": 0.0,
                "max": 0.0,
                "mean": 0.0,
                "median": 0.0,
                "p95": 0.0,
                "p99": 0.0,
                "std_dev": 0.0,
            }

        sorted_values = sorted(values)

        return {
            "min": min(values),
            "max": max(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "p95": self._percentile(sorted_values, 95),
            "p99": self._percentile(sorted_values, 99),
            "std_dev": statistics.stdev(values) if len(values) > 1 else 0.0,
        }

    def _percentile(self, sorted_values: List[float], percentile: float) -> float:
        """
        Calculate percentile value from sorted list.

        Args:
            sorted_values: Pre-sorted list of values
            percentile: Percentile to calculate (0-100)

        Returns:
            Percentile value
        """
        if not sorted_values:
            return 0.0

        k = (len(sorted_values) - 1) * (percentile / 100)
        f = int(k)
        c = f + 1

        if c >= len(sorted_values):
            return sorted_values[-1]

        return sorted_values[f] + (k - f) * (sorted_values[c] - sorted_values[f])

    def check_sla_compliance(self) -> bool:
        """
        Check if the system is currently meeting SLA requirements.

        Returns:
            True if SLA is being met, False otherwise
        """
        if not self.detection_latencies:
            return True  # No data means no violations

        # Check recent performance (last 10 samples)
        recent_samples = list(self.detection_latencies)[-10:]
        recent_violations = sum(
            1 for latency in recent_samples if latency > self.sla_threshold_ms
        )

        # Allow up to 10% violations in recent samples
        return recent_violations / len(recent_samples) <= 0.1

    def get_alerts(self) -> List[Dict[str, any]]:
        """
        Get current performance alerts and warnings.

        Returns:
            List of alert dictionaries
        """
        alerts = []

        if not self.detection_latencies:
            return alerts

        try:
            # Check SLA compliance
            if not self.check_sla_compliance():
                recent_avg = statistics.mean(list(self.detection_latencies)[-10:])
                alerts.append(
                    {
                        "level": "warning",
                        "component": "detection_latency",
                        "message": f"Recent average detection latency ({recent_avg:.2f}ms) "
                        f"approaching SLA threshold ({self.sla_threshold_ms}ms)",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )

            # Check for high violation rate
            violation_rate = self.stats["sla_violations"] / max(
                1, self.stats["total_samples"]
            )
            if violation_rate > 0.05:  # More than 5% violations
                alerts.append(
                    {
                        "level": "error",
                        "component": "sla_compliance",
                        "message": f"High SLA violation rate: {violation_rate:.1%} "
                        f"({self.stats['sla_violations']} of {self.stats['total_samples']} samples)",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )

            # Check for performance degradation (increasing trend)
            if len(self.detection_latencies) >= 20:
                early_avg = statistics.mean(list(self.detection_latencies)[:10])
                recent_avg = statistics.mean(list(self.detection_latencies)[-10:])

                if recent_avg > early_avg * 1.5:  # 50% increase
                    alerts.append(
                        {
                            "level": "warning",
                            "component": "performance_trend",
                            "message": f"Performance degradation detected: "
                            f"recent avg ({recent_avg:.2f}ms) vs "
                            f"earlier avg ({early_avg:.2f}ms)",
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    )

        except Exception as e:
            logger.error(f"Error generating alerts: {e}")
            alerts.append(
                {
                    "level": "error",
                    "component": "monitoring",
                    "message": f"Error in performance monitoring: {str(e)}",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

        return alerts

    def reset_stats(self) -> None:
        """Reset all performance statistics and samples."""
        self.detection_latencies.clear()
        self.processing_latencies.clear()
        self.throughput_samples.clear()

        self.stats = {
            "total_samples": 0,
            "sla_violations": 0,
            "last_reset": datetime.utcnow(),
            "peak_detection_latency_ms": 0.0,
            "peak_processing_latency_ms": 0.0,
            "peak_throughput_msgs_per_sec": 0.0,
        }

        logger.info("Performance statistics reset")

    def export_metrics(self, include_raw_data: bool = False) -> Dict[str, any]:
        """
        Export metrics for external analysis or storage.

        Args:
            include_raw_data: Whether to include raw sample data

        Returns:
            Comprehensive metrics export
        """
        export_data = {
            "summary": self.get_summary(),
            "alerts": self.get_alerts(),
            "configuration": {
                "max_samples": self.max_samples,
                "sla_threshold_ms": self.sla_threshold_ms,
            },
            "export_timestamp": datetime.utcnow().isoformat(),
        }

        if include_raw_data:
            export_data["raw_data"] = {
                "detection_latencies": list(self.detection_latencies),
                "processing_latencies": list(self.processing_latencies),
                "throughput_samples": list(self.throughput_samples),
            }

        return export_data
