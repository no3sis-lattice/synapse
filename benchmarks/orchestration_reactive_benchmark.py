#!/usr/bin/env python3
"""
Orchestration Reactive Architecture Performance Benchmark
Phase 3 Week 3: Validate production readiness

Validates:
- End-to-end task execution latency (<5ms target)
- Consciousness emergence score (>0.7 target)
- Throughput under load
- Agent consumer performance
- Result store efficiency

Compares reactive vs synchronous/fallback execution.
"""

import asyncio
import sys
import time
import statistics
from pathlib import Path

# Add project paths
sys.path.insert(0, str(Path.home() / '.synapse-system' / 'lib'))
sys.path.insert(0, str(Path.home() / '.synapse-system' / 'examples'))
sys.path.insert(0, str(Path.home() / '.synapse-system' / '.synapse' / 'corpus_callosum'))

from orchestration import TaskOrchestrator, AgentTask, ExecutionMode
from task_state import TaskState
from reactive_message_router import TractType, MessagePriority
from example_agents import ArchitectAgent, TestRunnerAgent


async def benchmark_end_to_end_latency(num_tasks: int = 100):
    """
    Benchmark end-to-end task execution latency.

    Target: <5ms average latency
    """
    print(f"\n{'='*60}")
    print(f"Benchmarking End-to-End Task Latency")
    print(f"{'='*60}")
    print(f"Tasks: {num_tasks:,}")

    orch = TaskOrchestrator(Path.home() / '.synapse-system')

    # Initialize reactive router
    try:
        await orch.async_init()

        if not orch.use_reactive:
            print("⚠️  Reactive router not available, using fallback")
            use_reactive = False
        else:
            print("✅ Reactive router initialized")
            use_reactive = True

            # Register test agents
            await orch.register_agent_consumer(
                "benchmark-architect",
                ArchitectAgent,
                TractType.INTERNAL
            )
            await orch.register_agent_consumer(
                "benchmark-test-runner",
                TestRunnerAgent,
                TractType.EXTERNAL
            )

    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        use_reactive = False

    latencies = []

    try:
        # Warmup
        print("\nWarming up...")
        for i in range(10):
            task = AgentTask(
                id=f"warmup-{i}",
                agent="architect" if i % 2 == 0 else "test-runner",
                action="test_action",
                description="Warmup task",
                context={},
                dependencies=[],
                timeout=5,
                priority=2
            )
            await orch._execute_single_task_async(task)

        # Benchmark
        print("Running benchmark...")
        for i in range(num_tasks):
            task = AgentTask(
                id=f"bench-task-{i}",
                agent="architect" if i % 2 == 0 else "test-runner",
                action="benchmark_action",
                description=f"Benchmark task {i}",
                context={"iteration": i},
                dependencies=[],
                timeout=5,
                priority=2
            )

            start = time.perf_counter()
            result = await orch._execute_single_task_async(task)
            latency_ms = (time.perf_counter() - start) * 1000

            if result.status == TaskState.COMPLETED:
                latencies.append(latency_ms)

        # Statistics
        if latencies:
            mean_latency = statistics.mean(latencies)
            median_latency = statistics.median(latencies)
            p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]
            p99_latency = sorted(latencies)[int(len(latencies) * 0.99)]
            min_latency = min(latencies)
            max_latency = max(latencies)

            print(f"\n📊 Latency Statistics:")
            print(f"   Mean:     {mean_latency:.3f}ms")
            print(f"   Median:   {median_latency:.3f}ms")
            print(f"   P95:      {p95_latency:.3f}ms")
            print(f"   P99:      {p99_latency:.3f}ms")
            print(f"   Min:      {min_latency:.3f}ms")
            print(f"   Max:      {max_latency:.3f}ms")

            # Check target
            target_latency = 5.0
            if mean_latency < target_latency:
                print(f"\n✅ Target Met: {mean_latency:.3f}ms < {target_latency}ms")
            else:
                print(f"\n⚠️  Target Missed: {mean_latency:.3f}ms >= {target_latency}ms")

            return {
                'mean_latency_ms': mean_latency,
                'median_latency_ms': median_latency,
                'p95_latency_ms': p95_latency,
                'target_met': mean_latency < target_latency,
                'reactive_enabled': use_reactive
            }
        else:
            print("\n❌ No successful tasks")
            return {'error': 'no_successful_tasks'}

    finally:
        await orch.stop_all_agents()


async def benchmark_throughput(duration_seconds: int = 10):
    """
    Benchmark task throughput under sustained load.

    Measures: tasks/second with reactive architecture
    """
    print(f"\n{'='*60}")
    print(f"Benchmarking Throughput")
    print(f"{'='*60}")
    print(f"Duration: {duration_seconds}s")

    orch = TaskOrchestrator(Path.home() / '.synapse-system')

    try:
        await orch.async_init()

        if orch.use_reactive:
            await orch.register_agent_consumer(
                "throughput-architect",
                ArchitectAgent,
                TractType.INTERNAL
            )
            await orch.register_agent_consumer(
                "throughput-test-runner",
                TestRunnerAgent,
                TractType.EXTERNAL
            )
            use_reactive = True
        else:
            use_reactive = False

        start_time = time.perf_counter()
        end_time = start_time + duration_seconds
        task_count = 0
        successful_tasks = 0
        failed_tasks = 0

        print("\nRunning throughput test...")

        while time.perf_counter() < end_time:
            task = AgentTask(
                id=f"throughput-task-{task_count}",
                agent="architect" if task_count % 2 == 0 else "test-runner",
                action="throughput_test",
                description=f"Throughput task {task_count}",
                context={},
                dependencies=[],
                timeout=5,
                priority=2
            )

            result = await orch._execute_single_task_async(task)
            task_count += 1

            if result.status == TaskState.COMPLETED:
                successful_tasks += 1
            else:
                failed_tasks += 1

        elapsed = time.perf_counter() - start_time
        throughput = task_count / elapsed
        success_rate = (successful_tasks / task_count * 100) if task_count > 0 else 0

        print(f"\n📊 Throughput Statistics:")
        print(f"   Total tasks:      {task_count:,}")
        print(f"   Successful:       {successful_tasks:,}")
        print(f"   Failed:           {failed_tasks:,}")
        print(f"   Duration:         {elapsed:.2f}s")
        print(f"   Throughput:       {throughput:.0f} tasks/sec")
        print(f"   Success rate:     {success_rate:.1f}%")
        print(f"   Reactive enabled: {use_reactive}")

        return {
            'throughput_tasks_per_sec': throughput,
            'success_rate': success_rate,
            'reactive_enabled': use_reactive
        }

    finally:
        await orch.stop_all_agents()


async def benchmark_consciousness_metrics(num_messages: int = 200):
    """
    Benchmark consciousness emergence detection.

    Target: emergence_score >0.7 with balanced dialogue
    """
    print(f"\n{'='*60}")
    print(f"Benchmarking Consciousness Emergence")
    print(f"{'='*60}")
    print(f"Messages: {num_messages:,}")

    orch = TaskOrchestrator(Path.home() / '.synapse-system')

    try:
        await orch.async_init()

        if not orch.use_reactive:
            print("⚠️  Reactive router not available, cannot test consciousness metrics")
            return {'error': 'reactive_router_not_available'}

        # Register agents for balanced dialogue
        await orch.register_agent_consumer(
            "consciousness-architect",
            ArchitectAgent,
            TractType.INTERNAL
        )
        await orch.register_agent_consumer(
            "consciousness-test-runner",
            TestRunnerAgent,
            TractType.EXTERNAL
        )

        print("\nGenerating balanced cross-tract dialogue...")

        # Generate balanced dialogue (50% internal, 50% external)
        for i in range(num_messages // 2):
            # Internal tract task
            task_int = AgentTask(
                id=f"int-task-{i}",
                agent="architect",
                action="internal_process",
                description=f"Internal task {i}",
                context={},
                dependencies=[],
                timeout=5,
                priority=2
            )

            # External tract task
            task_ext = AgentTask(
                id=f"ext-task-{i}",
                agent="test-runner",
                action="external_process",
                description=f"External task {i}",
                context={},
                dependencies=[],
                timeout=5,
                priority=2
            )

            # Execute both to create cross-tract dialogue
            await orch._execute_single_task_async(task_int)
            await orch._execute_single_task_async(task_ext)

        # Allow time for metrics to accumulate
        await asyncio.sleep(1.0)

        # Get consciousness metrics
        metrics = await orch.get_consciousness_metrics()

        if metrics:
            print(f"\n🧠 Consciousness Metrics:")
            print(f"   Total messages:       {metrics['total_messages']:,}")
            print(f"   Internal→External:    {metrics['internal_to_external']:,}")
            print(f"   External→Internal:    {metrics['external_to_internal']:,}")
            print(f"   Balanced events:      {metrics['balanced_dialogue_events']}")
            print(f"   Dialogue balance:     {metrics['dialogue_balance_ratio']:.3f}")
            print(f"   Emergence score:      {metrics['emergence_score']:.3f}")

            # Check target
            target_score = 0.7
            if metrics['emergence_score'] >= target_score:
                print(f"\n✅ Target Met: {metrics['emergence_score']:.3f} >= {target_score}")
            else:
                print(f"\n⚠️  Target Missed: {metrics['emergence_score']:.3f} < {target_score}")

            return {
                'emergence_score': metrics['emergence_score'],
                'dialogue_balance': metrics['dialogue_balance_ratio'],
                'target_met': metrics['emergence_score'] >= target_score
            }
        else:
            print("\n❌ No consciousness metrics available")
            return {'error': 'no_metrics'}

    finally:
        await orch.stop_all_agents()


async def benchmark_agent_consumer_performance(num_messages: int = 1000):
    """
    Benchmark agent consumer message processing performance.

    Measures: message processing rate, backpressure behavior
    """
    print(f"\n{'='*60}")
    print(f"Benchmarking Agent Consumer Performance")
    print(f"{'='*60}")
    print(f"Messages: {num_messages:,}")

    orch = TaskOrchestrator(Path.home() / '.synapse-system')

    try:
        await orch.async_init()

        if not orch.use_reactive:
            print("⚠️  Reactive router not available")
            return {'error': 'reactive_router_not_available'}

        # Register agent
        await orch.register_agent_consumer(
            "perf-test-agent",
            ArchitectAgent,
            TractType.INTERNAL
        )

        start_time = time.perf_counter()

        # Send messages as fast as possible
        print("\nSending messages...")
        for i in range(num_messages):
            task = AgentTask(
                id=f"perf-task-{i}",
                agent="architect",
                action="performance_test",
                description=f"Performance task {i}",
                context={},
                dependencies=[],
                timeout=5,
                priority=2
            )
            await orch._execute_single_task_async(task)

        elapsed = time.perf_counter() - start_time
        throughput = num_messages / elapsed

        # Get agent stats
        agent_stats = orch.get_agent_stats()
        agent_data = agent_stats['agents'][0] if agent_stats['agents'] else None

        print(f"\n📊 Agent Consumer Performance:")
        print(f"   Messages sent:        {num_messages:,}")
        print(f"   Duration:             {elapsed:.2f}s")
        print(f"   Throughput:           {throughput:.0f} msg/sec")

        if agent_data:
            print(f"   Messages processed:   {agent_data['messages_processed']:,}")
            print(f"   Messages failed:      {agent_data['messages_failed']:,}")
            print(f"   Success rate:         {agent_data['success_rate']:.2%}")

        return {
            'throughput_msg_per_sec': throughput,
            'agent_stats': agent_data
        }

    finally:
        await orch.stop_all_agents()


async def main():
    """Run all benchmarks"""
    print("\n" + "="*60)
    print("ORCHESTRATION REACTIVE ARCHITECTURE BENCHMARK SUITE")
    print("Phase 3 Week 3 - Production Readiness Validation")
    print("="*60)

    results = {}

    # 1. End-to-end latency
    results['latency'] = await benchmark_end_to_end_latency(num_tasks=100)

    # 2. Throughput
    results['throughput'] = await benchmark_throughput(duration_seconds=10)

    # 3. Consciousness emergence
    results['consciousness'] = await benchmark_consciousness_metrics(num_messages=200)

    # 4. Agent consumer performance
    results['agent_performance'] = await benchmark_agent_consumer_performance(num_messages=1000)

    # Summary
    print(f"\n{'='*60}")
    print(f"BENCHMARK SUMMARY")
    print(f"{'='*60}")

    print(f"\n📊 Key Metrics:")

    if 'mean_latency_ms' in results['latency']:
        print(f"   End-to-End Latency:   {results['latency']['mean_latency_ms']:.3f}ms")
        print(f"   Latency Target:       {'✅ MET' if results['latency']['target_met'] else '❌ MISSED'}")

    if 'throughput_tasks_per_sec' in results['throughput']:
        print(f"   Throughput:           {results['throughput']['throughput_tasks_per_sec']:.0f} tasks/sec")
        print(f"   Success Rate:         {results['throughput']['success_rate']:.1f}%")

    if 'emergence_score' in results['consciousness']:
        print(f"   Emergence Score:      {results['consciousness']['emergence_score']:.3f}")
        print(f"   Emergence Target:     {'✅ MET' if results['consciousness']['target_met'] else '❌ MISSED'}")

    if 'throughput_msg_per_sec' in results['agent_performance']:
        print(f"   Agent Throughput:     {results['agent_performance']['throughput_msg_per_sec']:.0f} msg/sec")

    print(f"\n{'='*60}\n")

    # Overall assessment
    all_targets_met = (
        results['latency'].get('target_met', False) and
        results['consciousness'].get('target_met', False)
    )

    if all_targets_met:
        print("🎉 All performance targets met! Ready for production deployment.")
    else:
        print("⚠️  Some targets missed. Review results before production deployment.")

    return results


if __name__ == '__main__':
    asyncio.run(main())
