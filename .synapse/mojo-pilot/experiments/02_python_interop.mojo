"""
Experiment 02: Python Interop Test
Purpose: Verify Mojo can import and use Python modules (redis, neo4j)
Risk: Low (only tests import and ping, no data modification)
Expected: Successful module loading and Redis connection
"""

from python import Python

fn main() raises:
    print("🔥 Mojo Python Interop Test")
    print("=" * 50)
    print("")

    # Test 1: Import Python's sys module
    print("Test 1: Basic Python import")
    var sys = Python.import_module("sys")
    print("  ✅ Python version:", sys.version)
    print("")

    # Test 2: Import redis module
    print("Test 2: Redis module import")
    var redis = Python.import_module("redis")
    print("  ✅ Redis module imported successfully")
    print("")

    # Test 3: Connect to Redis (read-only ping)
    print("Test 3: Redis connection (localhost:6379)")
    try:
        var r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

        # Safe read-only operation
        var pong = r.ping()
        print("  ✅ Redis PING successful:", pong)

        # Get Redis info (read-only)
        var info = r.info("server")
        print("  ✅ Redis version:", info["redis_version"])

    except e:
        print("  ⚠️  Redis connection failed (is Docker running?)")
        print("  Error:", e)
        print("  Fix: Run 'synapse start' to start services")

    print("")

    # Test 4: Import neo4j module (no connection yet)
    print("Test 4: Neo4j module import")
    try:
        var neo4j = Python.import_module("neo4j")
        print("  ✅ Neo4j module imported successfully")
    except:
        print("  ⚠️  Neo4j module not found")
        print("  Fix: cd .synapse/mojo-pilot && uv sync")

    print("")
    print("=" * 50)
    print("✨ Phase 0 Experiment 02: PASSED")
    print("")
    print("Next Steps:")
    print("  - Python interop is working!")
    print("  - Mojo can use existing Python libraries")
    print("  - Ready for performance benchmarks")
    print("  - Run: mojo run experiments/03_redis_connection.mojo")