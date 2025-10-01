#!/usr/bin/env python3
"""
Smoke test for Corpus Callosum Message Router
Tests basic functionality of Mojo FFI integration
"""

import sys
from message_router import (
    MessageRouter,
    TractType,
    MessagePriority,
    get_message_router
)


def test_initialization():
    """Test router initialization"""
    print("Test 1: Router initialization...")
    router = MessageRouter(capacity=1000)
    print(f"  ✓ Router created (using_mojo={router.using_mojo})")
    return router


def test_message_routing(router):
    """Test basic message routing"""
    print("\nTest 2: Message routing...")

    # Route messages to both tracts
    msg_id_1 = router.route_message(
        source_tract=TractType.EXTERNAL,
        dest_tract=TractType.INTERNAL,
        priority=MessagePriority.CRITICAL,
        payload={"test": "data1"}
    )
    print(f"  ✓ Routed message to Internal tract (id={msg_id_1})")

    msg_id_2 = router.route_message(
        source_tract=TractType.INTERNAL,
        dest_tract=TractType.EXTERNAL,
        priority=MessagePriority.NORMAL,
        payload={"test": "data2"}
    )
    print(f"  ✓ Routed message to External tract (id={msg_id_2})")

    msg_id_3 = router.route_message(
        source_tract=TractType.EXTERNAL,
        dest_tract=TractType.INTERNAL,
        priority=MessagePriority.URGENT,
        payload={"test": "data3"}
    )
    print(f"  ✓ Routed message to Internal tract (id={msg_id_3})")

    return [msg_id_1, msg_id_2, msg_id_3]


def test_queue_depth(router):
    """Test queue depth tracking"""
    print("\nTest 3: Queue depth...")

    internal_depth = router.get_queue_depth(TractType.INTERNAL)
    external_depth = router.get_queue_depth(TractType.EXTERNAL)
    total_depth = router.get_total_queue_depth()

    print(f"  ✓ Internal queue depth: {internal_depth}")
    print(f"  ✓ External queue depth: {external_depth}")
    print(f"  ✓ Total queue depth: {total_depth}")

    assert total_depth == internal_depth + external_depth, "Queue depth mismatch"
    print("  ✓ Queue depth validation passed")


def test_priority_ordering(router):
    """Test priority-based message ordering"""
    print("\nTest 4: Priority ordering...")

    # Dequeue from Internal tract (should get CRITICAL first, then URGENT)
    msg1 = router.get_next_message(TractType.INTERNAL)
    assert msg1 is not None, "Expected message from Internal tract"
    assert msg1.priority == MessagePriority.CRITICAL, f"Expected CRITICAL, got {msg1.priority}"
    print(f"  ✓ Got highest priority message first (CRITICAL, id={msg1.id})")

    msg2 = router.get_next_message(TractType.INTERNAL)
    assert msg2 is not None, "Expected second message from Internal tract"
    assert msg2.priority == MessagePriority.URGENT, f"Expected URGENT, got {msg2.priority}"
    print(f"  ✓ Got second priority message (URGENT, id={msg2.id})")

    # Dequeue from External tract
    msg3 = router.get_next_message(TractType.EXTERNAL)
    assert msg3 is not None, "Expected message from External tract"
    assert msg3.priority == MessagePriority.NORMAL, f"Expected NORMAL, got {msg3.priority}"
    print(f"  ✓ Got message from External tract (NORMAL, id={msg3.id})")


def test_statistics(router):
    """Test statistics collection"""
    print("\nTest 5: Statistics...")

    stats = router.get_stats()
    print(f"  ✓ Total messages: {stats.total_messages}")
    print(f"  ✓ Messages to Internal: {stats.messages_to_internal}")
    print(f"  ✓ Messages to External: {stats.messages_to_external}")
    print(f"  ✓ Message loss count: {stats.message_loss_count}")
    print(f"  ✓ Peak queue depth: {stats.peak_queue_depth}")

    assert stats.total_messages == 3, f"Expected 3 total messages, got {stats.total_messages}"
    assert stats.messages_to_internal == 2, f"Expected 2 Internal messages, got {stats.messages_to_internal}"
    assert stats.messages_to_external == 1, f"Expected 1 External message, got {stats.messages_to_external}"
    assert stats.message_loss_count == 0, f"Expected 0 lost messages, got {stats.message_loss_count}"
    print("  ✓ Statistics validation passed")


def test_empty_queue(router):
    """Test behavior with empty queue"""
    print("\nTest 6: Empty queue behavior...")

    # Both queues should now be empty
    msg = router.get_next_message(TractType.INTERNAL)
    assert msg is None, "Expected None from empty Internal queue"
    print("  ✓ Internal queue empty (returns None)")

    msg = router.get_next_message(TractType.EXTERNAL)
    assert msg is None, "Expected None from empty External queue"
    print("  ✓ External queue empty (returns None)")


def main():
    """Run all smoke tests"""
    print("=" * 60)
    print("Corpus Callosum Message Router - Smoke Test")
    print("=" * 60)

    try:
        # Run tests
        router = test_initialization()
        test_message_routing(router)
        test_queue_depth(router)
        test_priority_ordering(router)
        test_statistics(router)
        test_empty_queue(router)

        # Success
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        return 0

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return 1

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
