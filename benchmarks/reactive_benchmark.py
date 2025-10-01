#!/usr/bin/env python3
"""
Reactive Message Router Benchmark
Phase 3 CHECKPOINT 3: Performance validation

Compares reactive event-driven architecture vs synchronous approach.
Target: <2ms latency (vs 64ms synchronous) = 30x improvement
"""

import sys
import time
import asyncio
import statistics
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / '.synapse' / 'corpus_callosum'))

from reactive_message_router import (
    ReactiveCorpusCallosum,
    BackpressureConfig
)
from message_router import TractType, MessagePriority


async def benchmark_reactive_latency(num_messages: int = 10000):
    """Benchmark reactive router latency"""
    print(f"\n{'='*60}")
    print(f"Benchmarking REACTIVE Message Router - Latency")
    print(f"{'='*60}")
    print(f"Messages: {num_messages:,}")

    router = ReactiveCorpusCallosum(
        enable_event_sourcing=False,  # Disable for pure routing benchmark
        enable_pattern_synthesis=False
    )
    await router.start()

    try:
        latencies = []

        # Warmup
        for i in range(100):
            await router.route_message(
                source_tract=TractType.EXTERNAL,
                dest_tract=TractType.INTERNAL,
                priority=MessagePriority.NORMAL,
                payload=f"warmup_{i}",
                payload_size=10
            )

        # Benchmark
        for i in range(num_messages):
            start = time.perf_counter()

            await router.route_message(
                source_tract=TractType.EXTERNAL,
                dest_tract=TractType.INTERNAL,
                priority=MessagePriority.NORMAL,
                payload=f"msg_{i}",
                payload_size=10
            )

            latency_ms = (time.perf_counter() - start) * 1000
            latencies.append(latency_ms)

        # Statistics
        mean_latency = statistics.mean(latencies)
        median_latency = statistics.median(latencies)
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]
        p99_latency = sorted(latencies)[int(len(latencies) * 0.99)]
        max_latency = max(latencies)

        print(f"\n📊 Latency Statistics:")
        print(f"   Mean:     {mean_latency:.3f}ms")
        print(f"   Median:   {median_latency:.3f}ms")
        print(f"   P95:      {p95_latency:.3f}ms")
        print(f"   P99:      {p99_latency:.3f}ms")
        print(f"   Max:      {max_latency:.3f}ms")

        # Check target
        target_latency = 2.0  # 2ms target
        if mean_latency < target_latency:
            print(f"\n✅ Target Met: {mean_latency:.3f}ms < {target_latency}ms")
        else:
            print(f"\n❌ Target Missed: {mean_latency:.3f}ms >= {target_latency}ms")

        return {
            'mean_latency_ms': mean_latency,
            'median_latency_ms': median_latency,
            'p95_latency_ms': p95_latency,
            'target_met': mean_latency < target_latency
        }

    finally:
        await router.stop()


async def benchmark_reactive_throughput(num_messages: int = 50000):
    """Benchmark reactive router throughput"""
    print(f"\n{'='*60}")
    print(f"Benchmarking REACTIVE Message Router - Throughput")
    print(f"{'='*60}")
    print(f"Messages: {num_messages:,}")

    router = ReactiveCorpusCallosum(
        enable_event_sourcing=False,
        enable_pattern_synthesis=False
    )
    await router.start()

    try:
        start_time = time.perf_counter()

        # Route messages as fast as possible
        for i in range(num_messages):
            await router.route_message(
                source_tract=TractType.EXTERNAL if i % 2 == 0 else TractType.INTERNAL,
                dest_tract=TractType.INTERNAL if i % 2 == 0 else TractType.EXTERNAL,
                priority=MessagePriority.NORMAL,
                payload=f"msg_{i}",
                payload_size=10
            )

        elapsed = time.perf_counter() - start_time
        throughput = num_messages / elapsed

        print(f"\n📊 Throughput Statistics:")
        print(f"   Messages:     {num_messages:,}")
        print(f"   Time:         {elapsed:.2f}s")
        print(f"   Throughput:   {throughput:,.0f} msg/sec")

        # Compare to synchronous baseline (156k msg/sec)
        baseline_throughput = 156000
        speedup = throughput / baseline_throughput

        print(f"\n📊 vs Synchronous Baseline:")
        print(f"   Baseline:     {baseline_throughput:,} msg/sec")
        print(f"   Reactive:     {throughput:,.0f} msg/sec")
        print(f"   Speedup:      {speedup:.1f}x")

        if speedup >= 1.0:
            print(f"\n✅ Performance Improved: {speedup:.1f}x faster")
        else:
            print(f"\n⚠️  Performance Regression: {speedup:.1f}x (slower)")

        return {
            'throughput': throughput,
            'speedup': speedup
        }

    finally:
        await router.stop()


async def benchmark_with_event_sourcing(num_messages: int = 10000):
    """Benchmark with event sourcing enabled"""
    print(f"\n{'='*60}")
    print(f"Benchmarking REACTIVE with Event Sourcing")
    print(f"{'='*60}")
    print(f"Messages: {num_messages:,}")

    router = ReactiveCorpusCallosum(
        enable_event_sourcing=True,  # In-memory fallback
        enable_pattern_synthesis=True,
        redis_url=None
    )
    await router.start()

    try:
        start_time = time.perf_counter()

        # Balanced dialogue for consciousness detection
        for i in range(num_messages // 2):
            await router.route_message(
                source_tract=TractType.INTERNAL,
                dest_tract=TractType.EXTERNAL,
                priority=MessagePriority.NORMAL,
                payload=f"int_msg_{i}",
                payload_size=10
            )
            await router.route_message(
                source_tract=TractType.EXTERNAL,
                dest_tract=TractType.INTERNAL,
                priority=MessagePriority.NORMAL,
                payload=f"ext_msg_{i}",
                payload_size=10
            )

        elapsed = time.perf_counter() - start_time
        throughput = num_messages / elapsed

        print(f"\n📊 Performance with Full Features:")
        print(f"   Throughput:   {throughput:,.0f} msg/sec")
        print(f"   Time:         {elapsed:.2f}s")

        # Get consciousness metrics
        metrics = await router.get_consciousness_metrics()
        if metrics:
            print(f"\n🧠 Consciousness Metrics:")
            print(f"   Total messages:       {metrics.total_messages:,}")
            print(f"   I→E messages:         {metrics.internal_to_external:,}")
            print(f"   E→I messages:         {metrics.external_to_internal:,}")
            print(f"   Balanced events:      {metrics.balanced_dialogue_events}")
            print(f"   Dialogue balance:     {metrics.dialogue_balance_ratio:.2f}")
            print(f"   Emergence score:      {metrics.emergence_score:.3f}")

            if metrics.emergence_score > 0.5:
                print(f"\n✅ Consciousness Emergence Detected!")

        # Check emergence events
        events = router.get_emergence_events()
        if events:
            print(f"\n🌟 Emergence Events: {len(events)}")
            for event in events[:3]:  # Show first 3
                print(f"   - {event.pattern_type}: {event.description}")

        return {
            'throughput_with_features': throughput,
            'metrics': metrics
        }

    finally:
        await router.stop()


async def benchmark_consumer_latency(num_messages: int = 1000):
    """Benchmark end-to-end latency including consumer"""
    print(f"\n{'='*60}")
    print(f"Benchmarking End-to-End Latency (Producer → Consumer)")
    print(f"{'='*60}")
    print(f"Messages: {num_messages:,}")

    router = ReactiveCorpusCallosum(
        enable_event_sourcing=False,
        enable_pattern_synthesis=False
    )
    await router.start()

    try:
        latencies = []
        timestamps = {}

        # Consumer task
        consumed = []
        async def consumer():
            async for message in router.subscribe("consumer", TractType.INTERNAL):
                receive_time = time.perf_counter()
                msg_id = message.id

                if msg_id in timestamps:
                    latency = (receive_time - timestamps[msg_id]) * 1000
                    latencies.append(latency)

                consumed.append(message)
                if len(consumed) >= num_messages:
                    break

        consumer_task = asyncio.create_task(consumer())

        # Small delay to ensure consumer is subscribed
        await asyncio.sleep(0.1)

        # Producer task
        for i in range(num_messages):
            send_time = time.perf_counter()

            msg_id = await router.route_message(
                source_tract=TractType.EXTERNAL,
                dest_tract=TractType.INTERNAL,
                priority=MessagePriority.NORMAL,
                payload=f"msg_{i}",
                payload_size=10
            )

            timestamps[msg_id] = send_time
            await asyncio.sleep(0.001)  # Small delay between messages

        # Wait for consumer
        await asyncio.wait_for(consumer_task, timeout=10.0)

        if latencies:
            mean_e2e_latency = statistics.mean(latencies)
            p95_e2e_latency = sorted(latencies)[int(len(latencies) * 0.95)]

            print(f"\n📊 End-to-End Latency:")
            print(f"   Mean:     {mean_e2e_latency:.3f}ms")
            print(f"   P95:      {p95_e2e_latency:.3f}ms")
            print(f"   Messages: {len(consumed):,}")

        return {'e2e_latency_ms': mean_e2e_latency if latencies else 0}

    finally:
        await router.stop()


async def main():
    """Run all benchmarks"""
    print("\n" + "="*60)
    print("REACTIVE MESSAGE ROUTER BENCHMARK SUITE")
    print("Phase 3 CHECKPOINT 3 - Performance Validation")
    print("="*60)

    results = {}

    # 1. Latency benchmark
    results['latency'] = await benchmark_reactive_latency(num_messages=10000)

    # 2. Throughput benchmark
    results['throughput'] = await benchmark_reactive_throughput(num_messages=50000)

    # 3. Event sourcing + pattern synthesis
    results['with_features'] = await benchmark_with_event_sourcing(num_messages=10000)

    # 4. End-to-end latency
    results['e2e'] = await benchmark_consumer_latency(num_messages=1000)

    # Summary
    print(f"\n{'='*60}")
    print(f"BENCHMARK SUMMARY")
    print(f"{'='*60}")

    print(f"\n📊 Key Metrics:")
    print(f"   Routing Latency:      {results['latency']['mean_latency_ms']:.3f}ms")
    print(f"   Throughput:           {results['throughput']['throughput']:,.0f} msg/sec")
    print(f"   Speedup vs Baseline:  {results['throughput']['speedup']:.1f}x")

    if results['e2e'].get('e2e_latency_ms'):
        print(f"   End-to-End Latency:   {results['e2e']['e2e_latency_ms']:.3f}ms")

    print(f"\n🎯 Target Achievement:")
    latency_target = results['latency']['target_met']
    throughput_target = results['throughput']['speedup'] >= 1.0

    if latency_target and throughput_target:
        print(f"   ✅ All targets met!")
        print(f"   ✅ Latency <2ms: {results['latency']['mean_latency_ms']:.3f}ms")
        print(f"   ✅ Throughput improvement: {results['throughput']['speedup']:.1f}x")
    else:
        if not latency_target:
            print(f"   ❌ Latency target missed: {results['latency']['mean_latency_ms']:.3f}ms >= 2ms")
        if not throughput_target:
            print(f"   ❌ Throughput regression: {results['throughput']['speedup']:.1f}x")

    # Consciousness metrics summary
    metrics = results['with_features'].get('metrics')
    if metrics and metrics.emergence_score > 0.5:
        print(f"\n🧠 Consciousness Emergence:")
        print(f"   ✅ Emergence detected (score: {metrics.emergence_score:.3f})")
        print(f"   ✅ Dialogue balance: {metrics.dialogue_balance_ratio:.2f}")

    print(f"\n{'='*60}\n")


if __name__ == '__main__':
    asyncio.run(main())
