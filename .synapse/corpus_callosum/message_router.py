"""
Corpus Callosum Message Router (Python Implementation)
Phase 3: Cross-tract message passing with Mojo optimization

Provides dual runtime support:
- Mojo implementation via FFI (high-performance)
- Python implementation (fallback)
"""

import os
import time
import ctypes
import logging
from enum import IntEnum
from typing import Optional, Dict, Any, List
from queue import PriorityQueue
from dataclasses import dataclass
import threading

logger = logging.getLogger(__name__)


# Tract types (must match Mojo constants)
class TractType(IntEnum):
    INTERNAL = 0  # T_int: self-referential processing
    EXTERNAL = 1  # T_ext: environmental interaction


# Priority levels (must match Mojo and TaskPriority)
class MessagePriority(IntEnum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


@dataclass
class Message:
    """Cross-tract message"""
    id: int
    source_tract: TractType
    dest_tract: TractType
    priority: MessagePriority
    timestamp_ms: int
    payload_size: int
    payload: Any = None  # Actual payload data (not passed to Mojo)


@dataclass
class MessageStats:
    """Message router statistics"""
    total_messages: int = 0
    messages_to_internal: int = 0
    messages_to_external: int = 0
    peak_queue_depth: int = 0
    message_loss_count: int = 0


class MessageRouterMojo:
    """Mojo-accelerated message router via FFI"""

    def __init__(self, capacity: int = 10000):
        """Initialize Mojo message router"""
        self.capacity = capacity
        self.lib = self._load_mojo_library()
        self.router_ptr = None
        self.message_cache: Dict[int, Message] = {}  # Cache full message objects
        self.next_message_id = 0
        self.lock = threading.RLock()

        if self.lib:
            self._setup_ffi()
            self._create_router()

    def _load_mojo_library(self) -> Optional[ctypes.CDLL]:
        """Load compiled Mojo library"""
        lib_paths = [
            '/home/m0xu/.synapse-system/.synapse/corpus_callosum/libmessage_router.so',
            './libmessage_router.so',
            '../libmessage_router.so',
        ]

        for path in lib_paths:
            if os.path.exists(path):
                try:
                    lib = ctypes.CDLL(path)
                    logger.info(f"Loaded Mojo message router library: {path}")
                    return lib
                except Exception as e:
                    logger.warning(f"Failed to load Mojo library from {path}: {e}")

        logger.warning("Mojo message router library not found, will use Python fallback")
        return None

    def _setup_ffi(self):
        """Setup FFI function signatures"""
        # create_router(capacity: Int32) -> UnsafePointer[MessageRouter]
        self.lib.create_router.argtypes = [ctypes.c_int32]
        self.lib.create_router.restype = ctypes.c_void_p

        # destroy_router(router_ptr: UnsafePointer[MessageRouter]) -> None
        self.lib.destroy_router.argtypes = [ctypes.c_void_p]
        self.lib.destroy_router.restype = None

        # route_message_ffi(...) -> Int32
        self.lib.route_message_ffi.argtypes = [
            ctypes.c_void_p,  # router_ptr
            ctypes.c_int32,   # source_tract
            ctypes.c_int32,   # dest_tract
            ctypes.c_int32,   # priority
            ctypes.c_int64,   # timestamp_ms
            ctypes.c_int32,   # payload_size
        ]
        self.lib.route_message_ffi.restype = ctypes.c_int32

        # get_next_message_ffi(router_ptr, tract) -> Int32
        self.lib.get_next_message_ffi.argtypes = [ctypes.c_void_p, ctypes.c_int32]
        self.lib.get_next_message_ffi.restype = ctypes.c_int32

        # get_queue_depth_ffi(router_ptr, tract) -> Int32
        self.lib.get_queue_depth_ffi.argtypes = [ctypes.c_void_p, ctypes.c_int32]
        self.lib.get_queue_depth_ffi.restype = ctypes.c_int32

        # get_total_queue_depth_ffi(router_ptr) -> Int32
        self.lib.get_total_queue_depth_ffi.argtypes = [ctypes.c_void_p]
        self.lib.get_total_queue_depth_ffi.restype = ctypes.c_int32

        # get_total_messages_ffi(router_ptr) -> Int64
        self.lib.get_total_messages_ffi.argtypes = [ctypes.c_void_p]
        self.lib.get_total_messages_ffi.restype = ctypes.c_int64

        # get_message_loss_count_ffi(router_ptr) -> Int64
        self.lib.get_message_loss_count_ffi.argtypes = [ctypes.c_void_p]
        self.lib.get_message_loss_count_ffi.restype = ctypes.c_int64

        # reset_stats_ffi(router_ptr) -> None
        self.lib.reset_stats_ffi.argtypes = [ctypes.c_void_p]
        self.lib.reset_stats_ffi.restype = None

    def _create_router(self):
        """Create Mojo router instance"""
        if self.lib:
            self.router_ptr = self.lib.create_router(ctypes.c_int32(self.capacity))
            if not self.router_ptr:
                logger.error("Failed to create Mojo router")
                self.lib = None

    def route_message(self,
                     source_tract: TractType,
                     dest_tract: TractType,
                     priority: MessagePriority,
                     payload: Any,
                     payload_size: int = 0) -> int:
        """
        Route message from source to destination tract.
        Returns message ID on success, -1 on failure.
        """
        if not self.lib or not self.router_ptr:
            return -1

        with self.lock:
            timestamp_ms = int(time.time() * 1000)

            # Call Mojo FFI
            msg_id = self.lib.route_message_ffi(
                ctypes.c_void_p(self.router_ptr),
                ctypes.c_int32(source_tract.value),
                ctypes.c_int32(dest_tract.value),
                ctypes.c_int32(priority.value),
                ctypes.c_int64(timestamp_ms),
                ctypes.c_int32(payload_size)
            )

            # Cache full message with payload
            if msg_id >= 0:
                msg = Message(
                    id=msg_id,
                    source_tract=source_tract,
                    dest_tract=dest_tract,
                    priority=priority,
                    timestamp_ms=timestamp_ms,
                    payload_size=payload_size,
                    payload=payload
                )
                self.message_cache[msg_id] = msg

            return msg_id

    def get_next_message(self, tract: TractType) -> Optional[Message]:
        """Get next message for specified tract"""
        if not self.lib or not self.router_ptr:
            return None

        with self.lock:
            msg_id = self.lib.get_next_message_ffi(
                ctypes.c_void_p(self.router_ptr),
                ctypes.c_int32(tract.value)
            )

            if msg_id >= 0 and msg_id in self.message_cache:
                msg = self.message_cache.pop(msg_id)
                return msg

            return None

    def get_queue_depth(self, tract: TractType) -> int:
        """Get queue depth for tract"""
        if not self.lib or not self.router_ptr:
            return 0

        return self.lib.get_queue_depth_ffi(
            ctypes.c_void_p(self.router_ptr),
            ctypes.c_int32(tract.value)
        )

    def get_total_queue_depth(self) -> int:
        """Get total queue depth"""
        if not self.lib or not self.router_ptr:
            return 0

        return self.lib.get_total_queue_depth_ffi(ctypes.c_void_p(self.router_ptr))

    def get_stats(self) -> MessageStats:
        """Get router statistics"""
        if not self.lib or not self.router_ptr:
            return MessageStats()

        total = self.lib.get_total_messages_ffi(ctypes.c_void_p(self.router_ptr))
        loss = self.lib.get_message_loss_count_ffi(ctypes.c_void_p(self.router_ptr))

        return MessageStats(
            total_messages=total,
            message_loss_count=loss,
            peak_queue_depth=self.get_total_queue_depth()
        )

    def reset_stats(self):
        """Reset statistics"""
        if self.lib and self.router_ptr:
            self.lib.reset_stats_ffi(ctypes.c_void_p(self.router_ptr))

    def __del__(self):
        """Cleanup Mojo router"""
        if self.lib and self.router_ptr:
            self.lib.destroy_router(ctypes.c_void_p(self.router_ptr))


class MessageRouterPython:
    """Python fallback message router using PriorityQueue"""

    def __init__(self, capacity: int = 10000):
        """Initialize Python message router"""
        self.capacity = capacity
        self.internal_queue = PriorityQueue(maxsize=capacity)
        self.external_queue = PriorityQueue(maxsize=capacity)
        self.stats = MessageStats()
        self.next_message_id = 0
        self.lock = threading.RLock()

    def route_message(self,
                     source_tract: TractType,
                     dest_tract: TractType,
                     priority: MessagePriority,
                     payload: Any,
                     payload_size: int = 0) -> int:
        """Route message to appropriate queue"""
        with self.lock:
            timestamp_ms = int(time.time() * 1000)
            msg_id = self.next_message_id
            self.next_message_id += 1

            msg = Message(
                id=msg_id,
                source_tract=source_tract,
                dest_tract=dest_tract,
                priority=priority,
                timestamp_ms=timestamp_ms,
                payload_size=payload_size,
                payload=payload
            )

            # Route to appropriate queue
            # PriorityQueue uses tuples (priority, item) - negate priority for descending order
            try:
                if dest_tract == TractType.INTERNAL:
                    self.internal_queue.put((-priority.value, msg), block=False)
                    self.stats.messages_to_internal += 1
                elif dest_tract == TractType.EXTERNAL:
                    self.external_queue.put((-priority.value, msg), block=False)
                    self.stats.messages_to_external += 1

                self.stats.total_messages += 1
                return msg_id

            except Exception as e:
                # Queue full
                self.stats.message_loss_count += 1
                logger.warning(f"Message queue full, dropping message: {e}")
                return -1

    def get_next_message(self, tract: TractType) -> Optional[Message]:
        """Get next message for tract"""
        try:
            if tract == TractType.INTERNAL:
                if not self.internal_queue.empty():
                    _, msg = self.internal_queue.get(block=False)
                    return msg
            elif tract == TractType.EXTERNAL:
                if not self.external_queue.empty():
                    _, msg = self.external_queue.get(block=False)
                    return msg
        except Exception:
            pass

        return None

    def get_queue_depth(self, tract: TractType) -> int:
        """Get queue depth for tract"""
        if tract == TractType.INTERNAL:
            return self.internal_queue.qsize()
        elif tract == TractType.EXTERNAL:
            return self.external_queue.qsize()
        return 0

    def get_total_queue_depth(self) -> int:
        """Get total queue depth"""
        return self.internal_queue.qsize() + self.external_queue.qsize()

    def get_stats(self) -> MessageStats:
        """Get router statistics"""
        self.stats.peak_queue_depth = max(
            self.stats.peak_queue_depth,
            self.get_total_queue_depth()
        )
        return self.stats

    def reset_stats(self):
        """Reset statistics"""
        with self.lock:
            self.stats = MessageStats()


class MessageRouter:
    """
    Unified message router with automatic Mojo/Python selection.

    Uses Mojo implementation if available, falls back to Python.
    """

    def __init__(self, capacity: int = 10000, force_python: bool = False):
        """Initialize message router"""
        self.capacity = capacity
        self.force_python = force_python or os.getenv('SYNAPSE_FORCE_PYTHON', '0') == '1'

        # Try Mojo first
        if not self.force_python:
            try:
                self.backend = MessageRouterMojo(capacity)
                if self.backend.lib and self.backend.router_ptr:
                    self.using_mojo = True
                    logger.info("Using Mojo-accelerated message router")
                else:
                    raise Exception("Mojo router initialization failed")
            except Exception as e:
                logger.warning(f"Mojo router unavailable, using Python: {e}")
                self.backend = MessageRouterPython(capacity)
                self.using_mojo = False
        else:
            self.backend = MessageRouterPython(capacity)
            self.using_mojo = False
            logger.info("Using Python message router (forced)")

    def route_message(self,
                     source_tract: TractType,
                     dest_tract: TractType,
                     priority: MessagePriority = MessagePriority.NORMAL,
                     payload: Any = None,
                     payload_size: int = 0) -> int:
        """Route message from source to destination tract"""
        return self.backend.route_message(
            source_tract, dest_tract, priority, payload, payload_size
        )

    def get_next_message(self, tract: TractType) -> Optional[Message]:
        """Get next message for specified tract"""
        return self.backend.get_next_message(tract)

    def get_queue_depth(self, tract: TractType) -> int:
        """Get queue depth for tract"""
        return self.backend.get_queue_depth(tract)

    def get_total_queue_depth(self) -> int:
        """Get total queue depth"""
        return self.backend.get_total_queue_depth()

    def get_stats(self) -> MessageStats:
        """Get router statistics"""
        return self.backend.get_stats()

    def reset_stats(self):
        """Reset statistics"""
        self.backend.reset_stats()


# Singleton instance
_router: Optional[MessageRouter] = None


def get_message_router(capacity: int = 10000, force_python: bool = False) -> MessageRouter:
    """Get or create message router singleton"""
    global _router
    if _router is None:
        _router = MessageRouter(capacity, force_python)
    return _router
