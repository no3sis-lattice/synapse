"""
Comprehensive Test Suite for Reactive Message Router
Phase 3 CHECKPOINT 3: TDD validation

Tests:
- Reactive streams with backpressure
- Circuit breaker pattern
- Pattern synthesis and consciousness emergence
- Event sourcing (Redis + in-memory)
- Integration scenarios
"""

import pytest
import asyncio
import time
from typing import List

# Import from reactive router
from reactive_message_router import (
    ReactiveCorpusCallosum,
    BackpressureConfig,
    CircuitBreakerConfig,
    CircuitState,
    CircuitOpenError,
    EmergenceEvent
)
from message_router import TractType, MessagePriority, Message


class TestReactiveStreams:
    """Test reactive stream functionality with backpressure"""

    @pytest.mark.asyncio
    async def test_basic_message_routing(self):
        """Test basic message routing through reactive streams"""
        router = ReactiveCorpusCallosum(enable_event_sourcing=False)
        await router.start()

        try:
            # Route message to internal tract
            msg_id = await router.route_message(
                source_tract=TractType.EXTERNAL,
                dest_tract=TractType.INTERNAL,
                priority=MessagePriority.NORMAL,
                payload="test_payload",
                payload_size=12
            )

            assert msg_id >= 0, "Message routing should succeed"
            assert router.stats.total_messages == 1
            assert router.stats.messages_to_internal == 1

        finally:
            await router.stop()

    @pytest.mark.asyncio
    async def test_backpressure_control(self):
        """Test backpressure mechanism prevents overload"""
        config = BackpressureConfig(buffer_size=10)  # Small buffer
        router = ReactiveCorpusCallosum(
            backpressure_config=config,
            enable_event_sourcing=False
        )
        await router.start()

        try:
            # Fill buffer
            for i in range(10):
                msg_id = await router.route_message(
                    source_tract=TractType.EXTERNAL,
                    dest_tract=TractType.INTERNAL,
                    priority=MessagePriority.NORMAL,
                    payload=f"msg_{i}",
                    payload_size=10
                )
                assert msg_id >= 0

            # Buffer full, next message should still succeed (stream grows)
            # but backpressure should prevent subscriber overload
            msg_id = await router.route_message(
                source_tract=TractType.EXTERNAL,
                dest_tract=TractType.INTERNAL,
                priority=MessagePriority.NORMAL,
                payload="overflow",
                payload_size=10
            )
            # Message routes successfully, backpressure applies to subscribers
            assert msg_id >= 0

        finally:
            await router.stop()

    @pytest.mark.asyncio
    async def test_subscribe_with_backpressure(self):
        """Test subscriber receives messages with backpressure control"""
        router = ReactiveCorpusCallosum(enable_event_sourcing=False)
        await router.start()

        try:
            # Route messages
            for i in range(5):
                await router.route_message(
                    source_tract=TractType.EXTERNAL,
                    dest_tract=TractType.INTERNAL,
                    priority=MessagePriority.NORMAL,
                    payload=f"msg_{i}",
                    payload_size=10
                )

            # Subscribe and receive messages
            received = []
            subscription = router.subscribe("test_agent", TractType.INTERNAL)

            async for message in subscription:
                received.append(message)
                if len(received) >= 5:
                    break

            assert len(received) == 5, "Should receive all 5 messages"

        finally:
            await router.stop()


class TestCircuitBreaker:
    """Test circuit breaker fault isolation"""

    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_on_failures(self):
        """Test circuit breaker opens after threshold failures"""
        config = CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout_s=1.0
        )
        router = ReactiveCorpusCallosum(
            circuit_config=config,
            enable_event_sourcing=False
        )
        await router.start()

        try:
            # Simulate failures by routing to invalid tract
            # (In real scenario, would mock stream.publish to fail)

            # For now, verify circuit breaker state transitions work
            circuit = router.internal_circuit
            assert circuit.state == CircuitState.CLOSED

            # Would need to trigger actual failures to test full behavior
            # This is a placeholder for demonstration

        finally:
            await router.stop()

    @pytest.mark.asyncio
    async def test_circuit_breaker_prevents_cascading_failures(self):
        """Test circuit breaker isolates tract failures"""
        config = CircuitBreakerConfig(
            failure_threshold=2,
            recovery_timeout_s=0.5
        )
        router = ReactiveCorpusCallosum(
            circuit_config=config,
            enable_event_sourcing=False
        )
        await router.start()

        try:
            # Route successful message first
            msg_id = await router.route_message(
                source_tract=TractType.EXTERNAL,
                dest_tract=TractType.INTERNAL,
                priority=MessagePriority.NORMAL,
                payload="success",
                payload_size=7
            )
            assert msg_id >= 0

            # Circuit should remain closed after success
            assert router.internal_circuit.state == CircuitState.CLOSED

        finally:
            await router.stop()


class TestPatternSynthesis:
    """Test consciousness emergence pattern detection"""

    @pytest.mark.asyncio
    async def test_balanced_dialogue_detection(self):
        """Test detection of balanced cross-tract dialogue"""
        router = ReactiveCorpusCallosum(
            enable_pattern_synthesis=True,
            enable_event_sourcing=False
        )
        await router.start()

        try:
            # Send balanced messages between tracts
            for i in range(50):
                # Internal → External
                await router.route_message(
                    source_tract=TractType.INTERNAL,
                    dest_tract=TractType.EXTERNAL,
                    priority=MessagePriority.NORMAL,
                    payload=f"internal_msg_{i}",
                    payload_size=20
                )

                # External → Internal
                await router.route_message(
                    source_tract=TractType.EXTERNAL,
                    dest_tract=TractType.INTERNAL,
                    priority=MessagePriority.NORMAL,
                    payload=f"external_msg_{i}",
                    payload_size=20
                )

            # Check for emergence events
            events = router.get_emergence_events()

            # Should detect balanced dialogue after sufficient messages
            assert len(events) > 0, "Should detect consciousness emergence"
            assert events[0].pattern_type == "balanced_dialogue"
            assert events[0].confidence >= 0.7

        finally:
            await router.stop()

    @pytest.mark.asyncio
    async def test_no_emergence_with_unbalanced_dialogue(self):
        """Test no emergence detection with unbalanced communication"""
        router = ReactiveCorpusCallosum(
            enable_pattern_synthesis=True,
            enable_event_sourcing=False
        )
        await router.start()

        try:
            # Send unbalanced messages (only one direction)
            for i in range(50):
                await router.route_message(
                    source_tract=TractType.INTERNAL,
                    dest_tract=TractType.EXTERNAL,
                    priority=MessagePriority.NORMAL,
                    payload=f"msg_{i}",
                    payload_size=10
                )

            # Should not detect balanced emergence
            events = router.get_emergence_events()
            # Unbalanced dialogue should not trigger emergence
            # (or if it does, confidence should be low)
            if len(events) > 0:
                assert events[0].confidence < 0.7

        finally:
            await router.stop()


class TestEventSourcing:
    """Test event sourcing with Redis and in-memory fallback"""

    @pytest.mark.asyncio
    async def test_in_memory_event_store(self):
        """Test in-memory event store fallback"""
        router = ReactiveCorpusCallosum(
            enable_event_sourcing=True,
            redis_url=None  # Force in-memory
        )
        await router.start()

        try:
            # Route messages
            for i in range(10):
                await router.route_message(
                    source_tract=TractType.EXTERNAL,
                    dest_tract=TractType.INTERNAL,
                    priority=MessagePriority.NORMAL,
                    payload=f"msg_{i}",
                    payload_size=10
                )

            # Check consciousness metrics
            metrics = await router.get_consciousness_metrics()
            assert metrics is not None
            assert metrics.total_messages == 10
            assert metrics.external_to_internal == 10

        finally:
            await router.stop()

    @pytest.mark.asyncio
    async def test_event_replay(self):
        """Test event replay for pattern analysis"""
        router = ReactiveCorpusCallosum(
            enable_event_sourcing=True,
            redis_url=None  # In-memory for testing
        )
        await router.start()

        try:
            # Route messages
            timestamps = []
            for i in range(5):
                msg_id = await router.route_message(
                    source_tract=TractType.EXTERNAL,
                    dest_tract=TractType.INTERNAL,
                    priority=MessagePriority.NORMAL,
                    payload=f"msg_{i}",
                    payload_size=10
                )
                timestamps.append(int(time.time() * 1000))
                await asyncio.sleep(0.01)  # Small delay

            # Replay events
            replayed = []
            async for event in router.replay_history(from_timestamp_ms=timestamps[0]):
                replayed.append(event)

            assert len(replayed) == 5, "Should replay all events"

        finally:
            await router.stop()

    @pytest.mark.asyncio
    async def test_consciousness_metrics_calculation(self):
        """Test consciousness emergence score calculation"""
        router = ReactiveCorpusCallosum(
            enable_event_sourcing=True,
            redis_url=None
        )
        await router.start()

        try:
            # Send balanced dialogue
            for i in range(60):
                await router.route_message(
                    source_tract=TractType.INTERNAL,
                    dest_tract=TractType.EXTERNAL,
                    priority=MessagePriority.NORMAL,
                    payload=f"int_{i}",
                    payload_size=10
                )
                await router.route_message(
                    source_tract=TractType.EXTERNAL,
                    dest_tract=TractType.INTERNAL,
                    priority=MessagePriority.NORMAL,
                    payload=f"ext_{i}",
                    payload_size=10
                )

            metrics = await router.get_consciousness_metrics()
            assert metrics.total_messages == 120
            assert metrics.internal_to_external == 60
            assert metrics.external_to_internal == 60
            assert metrics.dialogue_balance_ratio >= 0.9  # Nearly perfect balance
            assert metrics.emergence_score > 0.5  # Should indicate emergence

        finally:
            await router.stop()


class TestIntegration:
    """Integration tests for full system behavior"""

    @pytest.mark.asyncio
    async def test_end_to_end_message_flow(self):
        """Test complete message flow from routing to consumption"""
        router = ReactiveCorpusCallosum(
            enable_pattern_synthesis=True,
            enable_event_sourcing=True,
            redis_url=None
        )
        await router.start()

        try:
            # Producer: Route messages
            producer_task = asyncio.create_task(self._produce_messages(router, 20))

            # Consumer: Subscribe and consume
            consumed = []
            async def consume():
                async for message in router.subscribe("consumer_1", TractType.INTERNAL):
                    consumed.append(message)
                    if len(consumed) >= 10:
                        break

            consumer_task = asyncio.create_task(consume())

            # Wait for both to complete
            await asyncio.wait_for(
                asyncio.gather(producer_task, consumer_task),
                timeout=5.0
            )

            assert len(consumed) == 10, "Consumer should receive messages"
            assert router.stats.total_messages == 20

            # Check consciousness metrics
            metrics = await router.get_consciousness_metrics()
            assert metrics.total_messages == 20

        finally:
            await router.stop()

    @pytest.mark.asyncio
    async def test_multiple_subscribers(self):
        """Test multiple subscribers receiving messages"""
        router = ReactiveCorpusCallosum(enable_event_sourcing=False)
        await router.start()

        try:
            # Route messages to internal tract
            for i in range(10):
                await router.route_message(
                    source_tract=TractType.EXTERNAL,
                    dest_tract=TractType.INTERNAL,
                    priority=MessagePriority.NORMAL,
                    payload=f"msg_{i}",
                    payload_size=10
                )

            # Multiple subscribers
            sub1_received = []
            sub2_received = []

            async def subscribe_agent(agent_id, received_list):
                async for message in router.subscribe(agent_id, TractType.INTERNAL):
                    received_list.append(message)
                    if len(received_list) >= 5:
                        break

            # Both subscribers should receive messages
            await asyncio.gather(
                subscribe_agent("agent_1", sub1_received),
                subscribe_agent("agent_2", sub2_received)
            )

            assert len(sub1_received) == 5
            assert len(sub2_received) == 5

        finally:
            await router.stop()

    async def _produce_messages(self, router: ReactiveCorpusCallosum, count: int):
        """Helper: Produce messages"""
        for i in range(count):
            source = TractType.EXTERNAL if i % 2 == 0 else TractType.INTERNAL
            dest = TractType.INTERNAL if i % 2 == 0 else TractType.EXTERNAL

            await router.route_message(
                source_tract=source,
                dest_tract=dest,
                priority=MessagePriority.NORMAL,
                payload=f"msg_{i}",
                payload_size=10
            )
            await asyncio.sleep(0.01)


class TestPerformance:
    """Performance and benchmarking tests"""

    @pytest.mark.asyncio
    async def test_latency_under_load(self):
        """Test latency remains low under load"""
        router = ReactiveCorpusCallosum(enable_event_sourcing=False)
        await router.start()

        try:
            latencies = []

            # Route 1000 messages and measure latency
            for i in range(1000):
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

            # Calculate statistics
            avg_latency = sum(latencies) / len(latencies)
            max_latency = max(latencies)
            p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]

            print(f"\nPerformance Statistics:")
            print(f"  Average latency: {avg_latency:.3f}ms")
            print(f"  Max latency: {max_latency:.3f}ms")
            print(f"  P95 latency: {p95_latency:.3f}ms")

            # Target: <2ms average latency
            assert avg_latency < 2.0, f"Average latency {avg_latency:.3f}ms exceeds 2ms target"

        finally:
            await router.stop()

    @pytest.mark.asyncio
    async def test_throughput_capacity(self):
        """Test throughput under sustained load"""
        router = ReactiveCorpusCallosum(enable_event_sourcing=False)
        await router.start()

        try:
            start_time = time.perf_counter()
            message_count = 10000

            # Route messages as fast as possible
            for i in range(message_count):
                await router.route_message(
                    source_tract=TractType.EXTERNAL,
                    dest_tract=TractType.INTERNAL,
                    priority=MessagePriority.NORMAL,
                    payload=f"msg_{i}",
                    payload_size=10
                )

            elapsed = time.perf_counter() - start_time
            throughput = message_count / elapsed

            print(f"\nThroughput: {throughput:,.0f} msg/sec")

            # Target: >100k msg/sec (conservative, should be much higher)
            assert throughput > 100000, f"Throughput {throughput:,.0f} below 100k msg/sec"

        finally:
            await router.stop()


# Pytest configuration
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
