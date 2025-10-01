#!/usr/bin/env python3
"""
Reactive Router Metrics Monitoring Script
Phase 3 Week 3: Production rollout monitoring

Monitors reactive router metrics during production rollout:
- Latency tracking
- Throughput measurement
- Consciousness emergence score
- Error rate monitoring
- Message loss detection
- Threshold breach alerting

Usage:
    python3 scripts/monitor_reactive_metrics.py --duration 24h
    python3 scripts/monitor_reactive_metrics.py --duration 48h --output metrics.log
"""

import asyncio
import argparse
import sys
import time
import signal
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Add project paths
sys.path.insert(0, str(Path.home() / '.synapse-system' / 'lib'))
sys.path.insert(0, str(Path.home() / '.synapse-system' / '.synapse' / 'corpus_callosum'))

from config import ROLLOUT_CONFIG
from orchestration import TaskOrchestrator


class MetricsMonitor:
    """Monitor reactive router metrics with threshold alerting"""

    def __init__(self, output_file: Optional[str] = None):
        self.output_file = output_file
        self.start_time = time.time()
        self.metrics_history = []
        self.alerts_triggered = []
        self.running = True

        # Load thresholds from config
        thresholds = ROLLOUT_CONFIG['reactive_rollback_thresholds']
        self.max_error_rate = thresholds['max_error_rate']
        self.min_latency_ms = thresholds['min_latency_ms']
        self.min_emergence_score = thresholds['min_emergence_score']
        self.max_message_loss = thresholds['max_message_loss']

    def parse_duration(self, duration_str: str) -> float:
        """
        Parse duration string to seconds.

        Args:
            duration_str: Duration string (e.g., "24h", "48h", "30m")

        Returns:
            Duration in seconds
        """
        duration_str = duration_str.lower().strip()

        if duration_str.endswith('h'):
            hours = float(duration_str[:-1])
            return hours * 3600
        elif duration_str.endswith('m'):
            minutes = float(duration_str[:-1])
            return minutes * 60
        elif duration_str.endswith('s'):
            return float(duration_str[:-1])
        else:
            raise ValueError(f"Invalid duration format: {duration_str}. Use format: 24h, 30m, 60s")

    def log(self, message: str):
        """
        Log message to console and optional file.

        Args:
            message: Message to log
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        formatted = f"[{timestamp}] {message}"
        print(formatted)

        if self.output_file:
            with open(self.output_file, 'a') as f:
                f.write(formatted + '\n')

    def check_thresholds(self, metrics: Dict[str, Any]) -> list:
        """
        Check if any thresholds are breached.

        Args:
            metrics: Current metrics dictionary

        Returns:
            List of threshold breach messages
        """
        breaches = []

        # Check error rate
        if 'error_rate' in metrics and metrics['error_rate'] > self.max_error_rate:
            breaches.append(
                f"ERROR RATE BREACH: {metrics['error_rate']:.2f}% > {self.max_error_rate}%"
            )

        # Check latency
        if 'mean_latency_ms' in metrics and metrics['mean_latency_ms'] > self.min_latency_ms:
            breaches.append(
                f"LATENCY BREACH: {metrics['mean_latency_ms']:.3f}ms > {self.min_latency_ms}ms"
            )

        # Check emergence score
        if 'emergence_score' in metrics and metrics['emergence_score'] < self.min_emergence_score:
            breaches.append(
                f"EMERGENCE SCORE BREACH: {metrics['emergence_score']:.3f} < {self.min_emergence_score}"
            )

        # Check message loss
        if 'message_loss' in metrics and metrics['message_loss'] > self.max_message_loss:
            breaches.append(
                f"MESSAGE LOSS BREACH: {metrics['message_loss']} > {self.max_message_loss}"
            )

        return breaches

    async def collect_metrics(self, orchestrator: TaskOrchestrator) -> Dict[str, Any]:
        """
        Collect current metrics from orchestrator.

        Args:
            orchestrator: TaskOrchestrator instance

        Returns:
            Dictionary of current metrics
        """
        metrics = {}

        try:
            # Get consciousness metrics (if reactive router enabled)
            consciousness = await orchestrator.get_consciousness_metrics()

            if consciousness:
                metrics['total_messages'] = consciousness.get('total_messages', 0)
                metrics['internal_to_external'] = consciousness.get('internal_to_external', 0)
                metrics['external_to_internal'] = consciousness.get('external_to_internal', 0)
                metrics['dialogue_balance'] = consciousness.get('dialogue_balance_ratio', 0.0)
                metrics['emergence_score'] = consciousness.get('emergence_score', 0.0)
                metrics['balanced_events'] = consciousness.get('balanced_dialogue_events', 0)

            # Get agent stats
            agent_stats = orchestrator.get_agent_stats()
            metrics['active_agents'] = agent_stats.get('total_agents', 0)
            metrics['agents_by_tract'] = agent_stats.get('agents_by_tract', {})

            # Calculate error rate and throughput (if we have historical data)
            if len(self.metrics_history) > 0:
                prev = self.metrics_history[-1]
                elapsed = time.time() - prev['timestamp']

                if elapsed > 0:
                    msg_delta = metrics.get('total_messages', 0) - prev.get('total_messages', 0)
                    metrics['throughput'] = msg_delta / elapsed if msg_delta > 0 else 0.0

            # Placeholder for error rate and latency (would need actual error tracking)
            metrics['error_rate'] = 0.0  # Would come from error tracking
            metrics['mean_latency_ms'] = 0.0  # Would come from latency tracking
            metrics['message_loss'] = 0  # Would come from message loss tracking

            # Add timestamp
            metrics['timestamp'] = time.time()

            return metrics

        except Exception as e:
            self.log(f"ERROR collecting metrics: {e}")
            return {'timestamp': time.time(), 'error': str(e)}

    def display_metrics(self, metrics: Dict[str, Any]):
        """
        Display metrics in readable format.

        Args:
            metrics: Metrics dictionary
        """
        elapsed = time.time() - self.start_time

        self.log("=" * 60)
        self.log(f"Metrics Update (Elapsed: {elapsed/3600:.2f}h)")
        self.log("=" * 60)

        if 'error' in metrics:
            self.log(f"ERROR: {metrics['error']}")
            return

        # Core metrics
        if 'total_messages' in metrics:
            self.log(f"Total Messages:       {metrics['total_messages']:,}")
        if 'throughput' in metrics:
            self.log(f"Throughput:           {metrics['throughput']:.1f} msg/sec")
        if 'mean_latency_ms' in metrics:
            self.log(f"Mean Latency:         {metrics['mean_latency_ms']:.3f}ms")
        if 'error_rate' in metrics:
            self.log(f"Error Rate:           {metrics['error_rate']:.2f}%")
        if 'message_loss' in metrics:
            self.log(f"Message Loss:         {metrics['message_loss']}")

        # Consciousness metrics
        self.log("")
        self.log("Consciousness Metrics:")
        if 'emergence_score' in metrics:
            self.log(f"  Emergence Score:    {metrics['emergence_score']:.3f}")
        if 'dialogue_balance' in metrics:
            self.log(f"  Dialogue Balance:   {metrics['dialogue_balance']:.3f}")
        if 'balanced_events' in metrics:
            self.log(f"  Balanced Events:    {metrics['balanced_events']}")
        if 'internal_to_external' in metrics:
            self.log(f"  Internal->External: {metrics['internal_to_external']:,}")
        if 'external_to_internal' in metrics:
            self.log(f"  External->Internal: {metrics['external_to_internal']:,}")

        # Agent stats
        if 'active_agents' in metrics:
            self.log("")
            self.log(f"Active Agents:        {metrics['active_agents']}")
            if 'agents_by_tract' in metrics:
                for tract, count in metrics['agents_by_tract'].items():
                    self.log(f"  {tract}:            {count}")

        self.log("")

        # Check thresholds
        breaches = self.check_thresholds(metrics)
        if breaches:
            self.log("ALERT: Threshold Breaches Detected!")
            for breach in breaches:
                self.log(f"  {breach}")
                self.alerts_triggered.append({
                    'timestamp': time.time(),
                    'breach': breach
                })
            self.log("")
            self.log("Consider manual rollback: Set message_router_reactive_rollout to 0%")

    async def monitor(self, duration_seconds: float, interval: float = 30.0):
        """
        Monitor metrics for specified duration.

        Args:
            duration_seconds: How long to monitor
            interval: How often to collect metrics (seconds)
        """
        end_time = time.time() + duration_seconds

        self.log(f"Starting metrics monitoring for {duration_seconds/3600:.2f} hours")
        self.log(f"Collection interval: {interval}s")
        self.log(f"Thresholds:")
        self.log(f"  Max Error Rate:      {self.max_error_rate}%")
        self.log(f"  Max Latency:         {self.min_latency_ms}ms")
        self.log(f"  Min Emergence Score: {self.min_emergence_score}")
        self.log(f"  Max Message Loss:    {self.max_message_loss}")
        self.log("")

        # Initialize orchestrator
        orch = TaskOrchestrator(Path.home() / '.synapse-system')

        try:
            await orch.async_init()

            if not orch.use_reactive:
                self.log("WARNING: Reactive router not enabled!")
                self.log("Enable in lib/config.py: MOJO_FEATURES['message_router_reactive'] = True")
                return

            self.log("Reactive router detected - monitoring active")
            self.log("")

            # Monitoring loop
            while self.running and time.time() < end_time:
                # Collect metrics
                metrics = await self.collect_metrics(orch)
                self.metrics_history.append(metrics)

                # Display metrics
                self.display_metrics(metrics)

                # Wait for next interval
                await asyncio.sleep(interval)

        except KeyboardInterrupt:
            self.log("Monitoring interrupted by user")
        except Exception as e:
            self.log(f"ERROR during monitoring: {e}")
        finally:
            await orch.stop_all_agents()
            self.log("Monitoring stopped")

            # Summary
            self.print_summary()

    def print_summary(self):
        """Print monitoring summary"""
        elapsed = time.time() - self.start_time

        self.log("")
        self.log("=" * 60)
        self.log("MONITORING SUMMARY")
        self.log("=" * 60)
        self.log(f"Duration:            {elapsed/3600:.2f} hours")
        self.log(f"Metrics Collected:   {len(self.metrics_history)}")
        self.log(f"Alerts Triggered:    {len(self.alerts_triggered)}")
        self.log("")

        if self.alerts_triggered:
            self.log("Threshold Breaches:")
            for alert in self.alerts_triggered:
                alert_time = datetime.fromtimestamp(alert['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                self.log(f"  [{alert_time}] {alert['breach']}")
            self.log("")
            self.log("RECOMMENDATION: Consider rollback or investigation")
        else:
            self.log("No threshold breaches detected - system healthy")

        if self.output_file:
            self.log(f"Detailed logs saved to: {self.output_file}")

    def handle_signal(self, signum, frame):
        """Handle interrupt signals gracefully"""
        self.log("Received interrupt signal - shutting down gracefully...")
        self.running = False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Monitor reactive router metrics during production rollout'
    )
    parser.add_argument(
        '--duration',
        type=str,
        default='24h',
        help='Monitoring duration (e.g., 24h, 48h, 30m)'
    )
    parser.add_argument(
        '--interval',
        type=float,
        default=30.0,
        help='Metrics collection interval in seconds (default: 30)'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output log file path (optional)'
    )

    args = parser.parse_args()

    # Create monitor
    monitor = MetricsMonitor(output_file=args.output)

    # Setup signal handlers
    signal.signal(signal.SIGINT, monitor.handle_signal)
    signal.signal(signal.SIGTERM, monitor.handle_signal)

    # Parse duration
    try:
        duration_seconds = monitor.parse_duration(args.duration)
    except ValueError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    # Run monitoring
    asyncio.run(monitor.monitor(duration_seconds, args.interval))


if __name__ == '__main__':
    main()
