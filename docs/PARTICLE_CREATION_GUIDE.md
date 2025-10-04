# Particle Creation Guide
## How to Create New Atomic Particles for the Synapse System

**Version**: Day 3-4
**Status**: Production Ready
**Architecture**: Dual-Tract with Fractal Pneuma

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Step-by-Step Creation Process](#step-by-step-creation-process)
4. [Code Template](#code-template)
5. [Testing Checklist](#testing-checklist)
6. [Registry Entry Requirements](#registry-entry-requirements)
7. [Common Patterns](#common-patterns)
8. [Anti-Patterns](#anti-patterns)
9. [Day 3-4 Features](#day-3-4-features)

---

## Overview

Atomic particles are the fundamental execution units in the Synapse system. They embody the **External Tract (`T_ext`)** - performing concrete actions on the environment (file system, network, database, etc.).

### Core Principles

1. **Single Responsibility**: Each particle does ONE thing well
2. **Fractal Pneuma**: Implements the Micro-Loop (Observe → Act → Evaluate → Memorize)
3. **State Persistence**: Maintains cycle count and custom metrics
4. **Circuit Breaker**: Automatic failure isolation (Day 3-4)
5. **Compression-Driven**: Fits into BWT/MTF/RLE/Huffman architecture

### When to Create a New Particle

Create a new particle when:
- A new atomic operation is needed (e.g., `api_caller`, `database_writer`)
- An existing particle is doing too much (violates Single Responsibility)
- You need specialized metrics or behavior for a specific operation

---

## Prerequisites

Before creating a particle, ensure:

1. **Base class available**: `lib/atomic_particle.py` is in your project
2. **Corpus Callosum running**: Message router is operational
3. **Registry exists**: `lib/registry.json` is present
4. **Python environment**: asyncio-compatible Python 3.8+

---

## Step-by-Step Creation Process

### Step 1: Define Your Particle's Purpose

**Question to ask**: "What single, atomic operation will this particle perform?"

**Examples**:
- ✅ `api_caller` - Makes HTTP API requests
- ✅ `json_parser` - Parses JSON data
- ❌ `data_processor` - Too vague (what kind of processing?)

### Step 2: Create the Particle File

**Location**: `lib/particles/your_particle_name.py`

**Naming convention**:
- Use snake_case for file names
- Use PascalCase for class names
- Suffix particle ID with descriptive name

```bash
touch lib/particles/your_particle_name.py
```

### Step 3: Implement the Particle Class

Use the [Code Template](#code-template) below as your starting point.

**Required methods**:
1. `__init__()` - Initialize custom metrics
2. `execute()` - Implement the atomic operation
3. Factory function - For easy instantiation

**Optional overrides**:
4. `evaluate()` - Only if you need custom scoring logic

### Step 4: Add Custom Metrics

Custom metrics track particle-specific data:

```python
def __init__(self, config, corpus_callosum, state_file):
    super().__init__(config, corpus_callosum, state_file)

    # Initialize custom metrics
    self._init_custom_metric('api_calls_made', 0)
    self._init_custom_metric('total_bytes_transferred', 0)
    self._init_custom_metric('average_response_time_ms', 0.0)
```

### Step 5: Implement the Execute Method

This is where your particle does its work:

```python
async def execute(self, context: ExecutionContext) -> Any:
    """Execute the atomic operation"""
    payload = context.payload

    # Extract parameters
    param1 = payload.get('param1')
    param2 = payload.get('param2', 'default')

    # Validate inputs
    if not param1:
        raise ValueError("param1 is required")

    # Perform the operation
    result = await self._do_the_thing(param1, param2)

    # Update custom metrics
    self.state.custom_metrics['operations_completed'] += 1

    return result
```

### Step 6: Add to Registry

Add your particle to `lib/registry.json`:

```json
{
  "agents": {
    "your_particle_id": {
      "id": "your_particle_id",
      "type": "atomic_particle",
      "tract": "EXTERNAL",
      "description": "Brief description of what this particle does",
      "frequency_rank": 10,
      "permissions": [
        "operation:specific_permission"
      ],
      "state_file": ".synapse/particles/your_particle_id_state.json",
      "particle_class": "YourParticleClass"
    }
  }
}
```

### Step 7: Write Tests

Create `tests/test_your_particle.py` following the [Testing Checklist](#testing-checklist).

### Step 8: Update Documentation

If your particle introduces new capabilities:
1. Update `file_creator_MVP.md` or equivalent
2. Document any new request types
3. Add examples to this guide

---

## Code Template

```python
"""
Your Particle Name
Description of what this particle does

This particle is part of the External Tract (T_ext) and implements
a single atomic operation: [describe operation].

Custom Metrics:
- metric_1: Description
- metric_2: Description
"""

import logging
from pathlib import Path
from typing import Any

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from atomic_particle import AtomicParticle, ExecutionContext, create_particle
from agent_consumer import AgentConfig
sys.path.insert(0, str(Path.home() / '.synapse-system' / '.synapse' / 'corpus_callosum'))
from reactive_message_router import TractType

logger = logging.getLogger(__name__)


class YourParticleClass(AtomicParticle):
    """
    Particle for [specific operation].

    Request payload:
    - param1 (required): Description
    - param2 (optional): Description
    - param3 (optional): Description

    Returns:
    - result_data: Description of return value
    """

    def __init__(self, config: AgentConfig, corpus_callosum, state_file: Path):
        super().__init__(config, corpus_callosum, state_file)

        # TODO: Initialize custom metrics
        self._init_custom_metric('metric_1', 0)
        self._init_custom_metric('metric_2', 0)
        self._init_custom_metric('metric_3', 0.0)

    async def execute(self, context: ExecutionContext) -> Any:
        """
        Execute the [operation name] operation.

        Args:
            context: Execution context with payload

        Returns:
            Result of the operation

        Raises:
            ValueError: If required parameters are missing
            RuntimeError: If operation fails
        """
        payload = context.payload

        # TODO: Extract and validate parameters
        param1 = payload.get('param1')
        param2 = payload.get('param2', 'default_value')

        if not param1:
            raise ValueError("param1 is required")

        # TODO: Perform the atomic operation
        try:
            result = await self._perform_operation(param1, param2)

            # TODO: Update custom metrics
            self.state.custom_metrics['metric_1'] += 1

            logger.info(
                f"[{self.config.agent_id}] Completed operation: "
                f"param1={param1}, result={result}"
            )

            return {
                "success": True,
                "result": result,
                "param1": param1
            }

        except Exception as e:
            logger.error(f"[{self.config.agent_id}] Operation failed: {e}")
            raise RuntimeError(f"Operation failed: {e}")

    async def _perform_operation(self, param1: str, param2: str) -> Any:
        """
        TODO: Implement the core operation logic here.

        This is a helper method to keep execute() clean.
        """
        # Your implementation here
        result = f"Processed {param1} with {param2}"
        return result


# Factory function
def create_your_particle(
    corpus_callosum,
    state_file: Path = None
) -> YourParticleClass:
    """
    Factory function for creating your particle instance.

    Args:
        corpus_callosum: Corpus Callosum instance
        state_file: Optional custom state file path

    Returns:
        Instantiated YourParticleClass
    """
    return create_particle(
        YourParticleClass,
        "your_particle_id",  # Must match registry entry
        corpus_callosum,
        state_file
    )
```

---

## Testing Checklist

### Unit Tests

Create `tests/test_your_particle.py`:

```python
import pytest
import asyncio
from pathlib import Path
import tempfile

from your_particle import create_your_particle
from reactive_message_router import ReactiveCorpusCallosum

@pytest.mark.asyncio
async def test_particle_basic_operation():
    """Test: Particle performs basic operation successfully"""
    # Setup
    corpus_callosum = ReactiveCorpusCallosum(enable_event_sourcing=False)
    await corpus_callosum.start()

    particle = create_your_particle(corpus_callosum)
    await particle.start()

    # Execute
    result = await corpus_callosum.route_message(
        source_tract=TractType.INTERNAL,
        dest_tract=TractType.EXTERNAL,
        payload={
            "param1": "test_value",
            "param2": "optional_value"
        }
    )

    # Assert
    assert result is not None

    # Cleanup
    await particle.stop()
    await corpus_callosum.stop()

@pytest.mark.asyncio
async def test_particle_error_handling():
    """Test: Particle handles missing parameters correctly"""
    # Test missing required param
    # Test invalid param types
    # Test operation failures
    pass

@pytest.mark.asyncio
async def test_particle_state_persistence():
    """Test: Particle persists state and custom metrics"""
    # Execute operation
    # Check state file exists
    # Verify custom metrics updated
    pass

@pytest.mark.asyncio
async def test_particle_circuit_breaker():
    """Test: Circuit breaker opens after failures (Day 3-4)"""
    # Trigger 5 consecutive failures
    # Verify circuit breaker opens
    # Verify requests rejected
    # Wait for recovery timeout
    # Verify circuit breaker half-opens
    pass
```

### Integration Tests

Add to `tests/test_file_creator_mvp.py`:

```python
@pytest.mark.asyncio
async def test_orchestrator_uses_new_particle(test_environment):
    """Test: Orchestrator can use the new particle"""
    # Add request type to orchestrator
    # Send request via corpus callosum
    # Verify particle executes
    # Verify correct result returned
    pass
```

### Test Coverage Goals

- ✅ **Unit tests**: 100% of execute() method
- ✅ **Error cases**: All ValueError/RuntimeError paths
- ✅ **State persistence**: Metrics update correctly
- ✅ **Circuit breaker**: All state transitions (Day 3-4)
- ✅ **Integration**: Works with orchestrator

---

## Registry Entry Requirements

Every particle **must** have a registry entry in `lib/registry.json`:

### Required Fields

```json
{
  "id": "unique_particle_id",           // Must be unique across all particles
  "type": "atomic_particle",            // Always "atomic_particle"
  "tract": "EXTERNAL",                  // Always "EXTERNAL" for particles
  "description": "What it does",        // Clear, concise description
  "frequency_rank": 10,                 // Initial rank (1=highest priority)
  "permissions": [                      // What it can access
    "resource:permission"
  ],
  "state_file": ".synapse/particles/particle_id_state.json",  // State file path
  "particle_class": "YourParticleClass" // Python class name
}
```

### Frequency Rank Guidelines

- **1**: Orchestrator only
- **2-5**: High-frequency operations (file_writer, api_caller)
- **6-10**: Medium-frequency (template_applier, json_parser)
- **11-20**: Low-frequency (specialized operations)
- **21+**: Rare/experimental particles

**Note**: With Day 3-4 MTF ranking, these will be automatically adjusted based on actual usage!

### Permission Naming Convention

Format: `resource:action`

Examples:
- `filesystem:read`
- `filesystem:write`
- `network:http`
- `database:query`
- `api:external`

---

## Common Patterns

### Pattern 1: File Operation Particle

```python
async def execute(self, context: ExecutionContext) -> Any:
    file_path = Path(context.payload.get('file_path'))

    # Ensure parent directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Perform operation
    file_path.write_text(content)

    # Update metrics
    self.state.custom_metrics['files_processed'] += 1
    self.state.custom_metrics['total_bytes'] += len(content)
```

### Pattern 2: API Call Particle

```python
async def execute(self, context: ExecutionContext) -> Any:
    import aiohttp

    url = context.payload.get('url')
    method = context.payload.get('method', 'GET')

    async with aiohttp.ClientSession() as session:
        async with session.request(method, url) as response:
            result = await response.json()

            # Update metrics
            self.state.custom_metrics['api_calls'] += 1
            self.state.custom_metrics['response_time_ms'] = response.elapsed.total_seconds() * 1000

            return result
```

### Pattern 3: Transform Particle

```python
async def execute(self, context: ExecutionContext) -> Any:
    input_data = context.payload.get('data')
    transform_type = context.payload.get('transform')

    # Apply transformation
    if transform_type == 'uppercase':
        result = input_data.upper()
    elif transform_type == 'lowercase':
        result = input_data.lower()
    else:
        raise ValueError(f"Unknown transform: {transform_type}")

    # Update metrics
    self.state.custom_metrics['transforms_applied'] += 1

    return result
```

### Pattern 4: Batch Operation Particle

```python
async def execute(self, context: ExecutionContext) -> Any:
    items = context.payload.get('items', [])
    results = []

    for item in items:
        result = await self._process_item(item)
        results.append(result)

    # Update metrics (note: O(1) for n items!)
    self.state.custom_metrics['batch_operations'] += 1
    self.state.custom_metrics['items_processed'] += len(items)

    return results
```

---

## Anti-Patterns

### ❌ Anti-Pattern 1: Doing Too Much

**Bad**:
```python
async def execute(self, context):
    # Read file
    content = Path('file.txt').read_text()

    # Transform it
    transformed = content.upper()

    # Write to database
    await db.write(transformed)

    # Send notification
    await api.notify()
```

**Why**: Violates Single Responsibility. This should be 4 particles.

**Good**: Create separate particles for read, transform, write, notify.

---

### ❌ Anti-Pattern 2: Storing State in Instance Variables

**Bad**:
```python
class MyParticle(AtomicParticle):
    def __init__(self, ...):
        super().__init__(...)
        self.data_cache = {}  # ❌ Will be lost on restart
```

**Why**: State is not persisted. Use `self.state.custom_metrics` instead.

**Good**:
```python
self._init_custom_metric('data_cache', {})
self.state.custom_metrics['data_cache']['key'] = value
```

---

### ❌ Anti-Pattern 3: Not Validating Inputs

**Bad**:
```python
async def execute(self, context):
    file_path = context.payload['file_path']  # ❌ Crashes if missing
    Path(file_path).write_text(content)
```

**Why**: Crashes instead of returning proper error.

**Good**:
```python
async def execute(self, context):
    file_path = context.payload.get('file_path')
    if not file_path:
        raise ValueError("file_path is required")
    Path(file_path).write_text(content)
```

---

### ❌ Anti-Pattern 4: Overriding evaluate() Without Reason

**Bad**:
```python
async def evaluate(self, result):
    return 1.0 if result.success else 0.0  # ❌ This is already the default
```

**Why**: Unnecessary code duplication.

**Good**: Only override `evaluate()` if you need custom scoring logic (e.g., based on performance, quality metrics, etc.).

---

## Day 3-4 Features

### Pattern Learning Integration

Your particle automatically contributes to pattern discovery. No extra code needed!

The orchestrator's pattern learner will:
- Detect when your particle is used in sequences
- Identify composition patterns involving your particle
- Suggest optimizations (e.g., batching multiple calls)

### MTF Ranking Integration

Your particle's frequency rank is automatically updated based on usage.

Initial rank in registry → Dynamic rank based on invocations

The MTF ranker tracks:
- Invocation count
- Execution time
- Success rate

After 5 minutes (configurable), ranks are recalculated.

### Circuit Breaker Usage

The circuit breaker is automatic, but you can configure it:

```python
class MyParticle(AtomicParticle):
    def __init__(self, config, corpus_callosum, state_file):
        super().__init__(
            config,
            corpus_callosum,
            state_file,
            failure_threshold=5,      # Open circuit after 5 failures
            recovery_timeout_s=60.0,  # Test recovery after 60 seconds
            half_open_max_requests=3  # Allow 3 requests in HALF_OPEN state
        )
```

**Circuit breaker states**:
- **CLOSED**: Normal operation, all requests pass through
- **OPEN**: Failing, requests immediately rejected with error
- **HALF_OPEN**: Testing recovery, limited requests allowed

**When it triggers**:
- `failure_threshold` consecutive failures → OPEN
- After `recovery_timeout_s` → HALF_OPEN
- Successful request in HALF_OPEN → CLOSED
- Failed request in HALF_OPEN → OPEN

---

## Complete Example: Creating an `api_caller` Particle

Let's walk through creating a real particle from scratch.

### Step 1: Define Purpose
**Purpose**: Make HTTP API calls to external services

### Step 2: Create File
```bash
touch lib/particles/api_caller.py
```

### Step 3: Implement

```python
"""
API Caller Particle
Makes HTTP API requests to external services

Custom Metrics:
- api_calls_made: Total number of API calls
- total_bytes_transferred: Total bytes sent/received
- average_response_time_ms: Average API response time
"""

import logging
import aiohttp
from pathlib import Path
from typing import Any

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from atomic_particle import AtomicParticle, ExecutionContext, create_particle

logger = logging.getLogger(__name__)


class ApiCaller(AtomicParticle):
    """
    Particle for making HTTP API calls.

    Request payload:
    - url (required): API endpoint URL
    - method (optional): HTTP method (default: GET)
    - headers (optional): Request headers dict
    - body (optional): Request body (for POST/PUT)

    Returns:
    - response_data: JSON response from API
    - status_code: HTTP status code
    """

    def __init__(self, config, corpus_callosum, state_file):
        super().__init__(config, corpus_callosum, state_file)

        self._init_custom_metric('api_calls_made', 0)
        self._init_custom_metric('total_bytes_transferred', 0)
        self._init_custom_metric('average_response_time_ms', 0.0)

    async def execute(self, context: ExecutionContext) -> Any:
        payload = context.payload

        # Extract parameters
        url = payload.get('url')
        method = payload.get('method', 'GET').upper()
        headers = payload.get('headers', {})
        body = payload.get('body')

        # Validate
        if not url:
            raise ValueError("url is required")

        if method not in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
            raise ValueError(f"Invalid HTTP method: {method}")

        # Make API call
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method,
                url,
                headers=headers,
                json=body if body else None
            ) as response:
                response_data = await response.json()
                status_code = response.status

                # Calculate bytes transferred
                request_size = len(str(body)) if body else 0
                response_size = len(str(response_data))
                total_bytes = request_size + response_size

                # Update metrics
                self.state.custom_metrics['api_calls_made'] += 1
                self.state.custom_metrics['total_bytes_transferred'] += total_bytes

                # Update average response time
                calls = self.state.custom_metrics['api_calls_made']
                current_avg = self.state.custom_metrics['average_response_time_ms']
                # Incremental average
                self.state.custom_metrics['average_response_time_ms'] = (
                    (current_avg * (calls - 1) + response.elapsed.total_seconds() * 1000) / calls
                )

                logger.info(
                    f"[{self.config.agent_id}] API call: {method} {url} → {status_code}"
                )

                return {
                    "success": True,
                    "response_data": response_data,
                    "status_code": status_code,
                    "bytes_transferred": total_bytes
                }


def create_api_caller(corpus_callosum, state_file=None):
    return create_particle(
        ApiCaller,
        "api_caller",
        corpus_callosum,
        state_file
    )
```

### Step 4: Add to Registry

```json
{
  "agents": {
    "api_caller": {
      "id": "api_caller",
      "type": "atomic_particle",
      "tract": "EXTERNAL",
      "description": "Makes HTTP API calls to external services",
      "frequency_rank": 4,
      "permissions": [
        "network:http",
        "api:external"
      ],
      "state_file": ".synapse/particles/api_caller_state.json",
      "particle_class": "ApiCaller"
    }
  }
}
```

### Step 5: Write Tests

```python
@pytest.mark.asyncio
async def test_api_caller_get_request():
    """Test: API caller makes GET request"""
    corpus_callosum = ReactiveCorpusCallosum(enable_event_sourcing=False)
    await corpus_callosum.start()

    api_caller = create_api_caller(corpus_callosum)
    await api_caller.start()

    result = await corpus_callosum.route_message(
        source_tract=TractType.INTERNAL,
        dest_tract=TractType.EXTERNAL,
        payload={
            "url": "https://api.example.com/data",
            "method": "GET"
        }
    )

    assert result['success'] == True
    assert result['status_code'] == 200

    await api_caller.stop()
    await corpus_callosum.stop()
```

### Step 6: Update Orchestrator

Add new request type to orchestrator:

```python
elif request_type == "api_call":
    plan.actions.append(PlannedAction(
        action_type=ActionType.API_CALL,
        target_particle="api_caller",
        payload={
            "url": params.get("url"),
            "method": params.get("method", "GET"),
            "headers": params.get("headers", {}),
            "body": params.get("body")
        }
    ))
```

### Step 7: Done!

Your `api_caller` particle is now:
- ✅ Part of the External Tract
- ✅ Implements Fractal Pneuma Micro-Loop
- ✅ Tracks custom metrics
- ✅ Has circuit breaker protection
- ✅ Automatically optimized by MTF ranking
- ✅ Contributes to pattern learning

---

## Summary Checklist

Before considering your particle complete:

- [ ] Implements `execute()` method
- [ ] Has clear, single responsibility
- [ ] Validates all inputs
- [ ] Initializes custom metrics
- [ ] Updates metrics on execution
- [ ] Has factory function
- [ ] Added to `lib/registry.json`
- [ ] Has unit tests (>80% coverage)
- [ ] Has integration test with orchestrator
- [ ] Circuit breaker tested (Day 3-4)
- [ ] Documentation updated
- [ ] Follows naming conventions
- [ ] No anti-patterns present

---

## Need Help?

Common issues and solutions:

**Q**: Particle not receiving messages
**A**: Check registry entry, ensure particle started, verify Corpus Callosum routing

**Q**: State not persisting
**A**: Ensure using `self.state.custom_metrics`, check file permissions, verify `_save_state()` called

**Q**: Circuit breaker always open
**A**: Check failure threshold, verify success/failure logic, review logs for actual errors

**Q**: Tests timing out
**A**: Increase timeout in `route_and_collect()`, check for deadlocks, verify async/await usage

---

**Next Steps**: Review existing particles (`lib/particles/*`) for more examples, or create your first particle using this guide!
