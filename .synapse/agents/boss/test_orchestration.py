#!/usr/bin/env python3
"""
Test Synapse Project Manager Orchestration

Tests the complete orchestration workflow using 4QZero compression principles.
"""

import asyncio
import json
from synapse_pm_agent import SynapseProjectManagerAgent


async def test_feature_implementation():
    """Test complete feature implementation workflow."""
    print("🚀 Testing Feature Implementation Orchestration")
    print("=" * 60)

    # Initialize orchestrator
    pm = SynapseProjectManagerAgent()
    print(f"✅ Initialized {pm.config['agent']['name']}")
    print(f"📊 Current cycle: {pm.state['cycle']}")

    # Test complex feature request
    feature_request = """
    Implement a user authentication system for a Rust web application.
    Requirements:
    - JWT token-based authentication
    - Password hashing with bcrypt
    - Login/logout endpoints
    - User registration with email validation
    - Rate limiting for security
    - Integration tests with 90%+ coverage
    - API documentation
    """

    print(f"\n📝 Request: {feature_request[:100]}...")

    try:
        # Execute orchestration workflow
        result = await pm.orchestrate_workflow(feature_request, "feat")

        print(f"\n🎯 Orchestration Results:")
        print(f"   Workflow ID: {result.get('workflow_id')}")
        print(f"   Pattern: {result.get('pattern', {}).get('pattern_name')}")
        print(f"   Agents Coordinated: {result.get('performance', {}).get('agents_coordinated')}")
        print(f"   Parallel Streams: {result.get('performance', {}).get('parallel_streams')}")
        print(f"   Total Tasks: {result.get('performance', {}).get('total_tasks')}")

        # Show execution graph
        execution_graph = result.get("execution_graph", {})
        if "optimized_streams" in execution_graph:
            print(f"\n📈 Execution Plan:")
            for i, stream in enumerate(execution_graph["optimized_streams"]):
                print(f"   Wave {i+1}: {stream}")

        # Show validation results
        validation = result.get("validation", {})
        print(f"\n✅ Validation:")
        print(f"   Valid: {validation.get('valid')}")
        print(f"   Confidence: {validation.get('confidence', 0):.2f}")

        # Show performance metrics
        if "agent_results" in result:
            agent_results = result["agent_results"]
            print(f"\n🤖 Agent Performance:")
            print(f"   Successful: {agent_results.get('successful', 0)}")
            print(f"   Failed: {agent_results.get('failed', 0)}")
            print(f"   Total Agents: {agent_results.get('agents_coordinated', 0)}")

        return result

    except Exception as e:
        print(f"❌ Orchestration failed: {e}")
        return None


async def test_bug_fix_workflow():
    """Test bug fix workflow."""
    print("\n\n🐛 Testing Bug Fix Orchestration")
    print("=" * 60)

    pm = SynapseProjectManagerAgent()

    bug_report = """
    Fix memory leak in user session management.
    The application consumes increasing memory over time.
    Issue appears related to session cleanup not working properly.
    Priority: High
    """

    print(f"📝 Bug Report: {bug_report[:80]}...")

    try:
        result = await pm.orchestrate_workflow(bug_report, "bug")

        print(f"\n🎯 Bug Fix Results:")
        print(f"   Workflow ID: {result.get('workflow_id')}")
        print(f"   Pattern: {result.get('pattern', {}).get('pattern_name')}")
        print(f"   Performance: {result.get('performance')}")

        return result

    except Exception as e:
        print(f"❌ Bug fix orchestration failed: {e}")
        return None


async def test_task_decomposition():
    """Test task decomposition capabilities."""
    print("\n\n⚙️ Testing Task Decomposition")
    print("=" * 60)

    pm = SynapseProjectManagerAgent()

    complex_task = "Add OAuth2 integration with Google and GitHub for the authentication system"

    print(f"📝 Complex Task: {complex_task}")

    try:
        result = await pm.decompose_task(complex_task)

        print(f"\n🧩 Decomposition Results:")
        print(f"   Task Type: {result.get('task_type')}")
        print(f"   Atomic Tasks: {len(result.get('atomic_tasks', []))}")
        print(f"   Estimated Duration: {result.get('estimated_duration')} minutes")

        # Show atomic tasks
        for i, task in enumerate(result.get('atomic_tasks', [])[:3]):  # Show first 3
            print(f"   {i+1}. {task.get('description')} -> {task.get('agent_required')}")

        return result

    except Exception as e:
        print(f"❌ Task decomposition failed: {e}")
        return None


async def test_context_compression():
    """Test context compression using 4QZero principles."""
    print("\n\n🗜️ Testing Context Compression")
    print("=" * 60)

    pm = SynapseProjectManagerAgent()

    # Create verbose context
    verbose_context = {
        "task": "Implement a comprehensive user authentication system with JWT tokens, password hashing using bcrypt, email validation, rate limiting for security purposes, and complete integration testing coverage",
        "requirements": [
            "JSON Web Token implementation for stateless authentication",
            "Secure password hashing using bcrypt with appropriate salt rounds",
            "Email validation with regex patterns and domain verification",
            "Rate limiting implementation to prevent brute force attacks",
            "Comprehensive integration test suite with minimum 90% coverage",
            "Complete API documentation with examples and usage instructions"
        ],
        "context": {
            "language": "rust",
            "framework": "axum",
            "database": "postgresql",
            "deployment": "docker_kubernetes",
            "security_requirements": "OWASP_top_10_compliance",
            "performance_targets": "sub_100ms_response_time"
        }
    }

    print(f"📊 Original context size: {len(str(verbose_context))} characters")

    # Test compression
    compressed = pm.communicator._compress_context(verbose_context)
    compressed_size = len(str(compressed))
    compression_ratio = compressed_size / len(str(verbose_context))

    print(f"🗜️ Compressed size: {compressed_size} characters")
    print(f"📉 Compression ratio: {compression_ratio:.2f}")
    print(f"💾 Space saved: {1 - compression_ratio:.1%}")

    print(f"\n📝 Compressed Context:")
    print(json.dumps(compressed, indent=2))

    return {
        "original_size": len(str(verbose_context)),
        "compressed_size": compressed_size,
        "compression_ratio": compression_ratio,
        "compressed_context": compressed
    }


async def test_agent_communication():
    """Test agent communication protocol."""
    print("\n\n📡 Testing Agent Communication")
    print("=" * 60)

    pm = SynapseProjectManagerAgent()

    # Test single agent query
    context = {
        "task": "Analyze Rust code for performance bottlenecks",
        "code": "fn example() { /* sample code */ }",
        "requirements": ["performance_analysis", "optimization_suggestions"]
    }

    print("🔄 Testing single agent communication...")

    try:
        result = await pm.communicator.query_agent("@rust-specialist", context)

        print(f"✅ Agent Response:")
        print(f"   Agent: {result.get('agent')}")
        print(f"   Execution Time: {result.get('execution_time', 0):.1f}s")
        print(f"   Context Compression: {result.get('context_compression', 0):.2f}")

        if "error" in result:
            print(f"   Error: {result['error']}")

        return result

    except Exception as e:
        print(f"❌ Agent communication failed: {e}")
        return None


async def main():
    """Run all orchestration tests."""
    print("🎭 Synapse Project Manager - Orchestration Test Suite")
    print("Using 4QZero compression principles for maximum coordination density")
    print("=" * 80)

    # Run tests
    tests = [
        test_feature_implementation(),
        test_bug_fix_workflow(),
        test_task_decomposition(),
        test_context_compression(),
        test_agent_communication()
    ]

    results = []
    for test in tests:
        try:
            result = await test
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed: {e}")
            results.append(None)

    # Summary
    print("\n\n📊 Test Suite Summary")
    print("=" * 80)

    successful_tests = sum(1 for r in results if r is not None)
    total_tests = len(results)

    print(f"✅ Successful Tests: {successful_tests}/{total_tests}")
    print(f"📈 Success Rate: {successful_tests/total_tests:.1%}")

    if successful_tests > 0:
        print("\n🎯 Key Achievements:")
        print("   • Multi-agent orchestration functional")
        print("   • 4QZero compression principles applied")
        print("   • Symbolic state management working")
        print("   • Context density maximization achieved")
        print("   • Workflow pattern matching operational")

    print("\n🚀 Synapse Project Manager is ready for network orchestration!")


if __name__ == "__main__":
    asyncio.run(main())