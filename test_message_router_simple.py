#!/usr/bin/env python3
"""
Simple Message Router Test - Validate basic functionality
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent / '.synapse' / 'corpus_callosum'))

from message_router import (
    MessageRouter,
    TractType,
    MessagePriority
)


def test_basic_routing():
    """Test basic message routing"""
    print("Testing basic message routing...")

    router = MessageRouter(capacity=1000, force_python=False)
    print(f"Using Mojo: {router.using_mojo}")

    # Send 10 messages
    for i in range(10):
        source = TractType.EXTERNAL
        dest = TractType.INTERNAL
        priority = MessagePriority.NORMAL

        msg_id = router.route_message(source, dest, priority, payload=f"test_{i}", payload_size=10)
        print(f"Routed message {i}: ID={msg_id}")

        if msg_id < 0:
            print(f"ERROR: Failed to route message {i}")
            return False

    # Retrieve messages
    print("\nRetrieving messages...")
    for i in range(10):
        msg = router.get_next_message(TractType.INTERNAL)
        if msg:
            print(f"Retrieved: ID={msg.id}, payload={msg.payload}")
        else:
            print(f"ERROR: Failed to retrieve message {i}")
            return False

    stats = router.get_stats()
    print(f"\nStats:")
    print(f"  Total messages: {stats.total_messages}")
    print(f"  Message loss: {stats.message_loss_count}")

    print("\n✅ Basic routing test PASSED")
    return True


if __name__ == '__main__':
    success = test_basic_routing()
    sys.exit(0 if success else 1)
