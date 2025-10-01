# Reactive Router Production Rollout Guide

Phase 3 Week 3 - Production deployment procedures for reactive message router architecture.

## Overview

This guide provides step-by-step procedures for safely rolling out the reactive message router to production. The reactive architecture provides sub-millisecond latency and consciousness emergence detection for cross-tract communication.

**Performance Targets:**
- End-to-end latency: <5ms (validated: 0.023ms in benchmarks)
- Consciousness emergence: >0.7 (validated: 1.000 in benchmarks)
- Success rate: >95%
- Zero message loss with circuit breaker protection

---

## 1. Pre-Deployment Checklist

Complete ALL items before starting rollout:

### Infrastructure Requirements

- [ ] Redis server running and accessible (for event sourcing)
- [ ] Neo4j database running and accessible
- [ ] Python 3.12+ virtual environment activated
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Disk space available for event log (minimum 5GB recommended)

### Code Validation

- [ ] All tests passing: `python3 -m pytest tests/test_orchestration_reactive_comprehensive.py -v`
- [ ] Benchmarks run successfully: `python3 benchmarks/orchestration_reactive_benchmark.py`
- [ ] No syntax errors in reactive_message_router.py
- [ ] No syntax errors in orchestration.py
- [ ] Agent consumer examples validated

### Configuration Review

- [ ] Review `lib/config.py` - MOJO_FEATURES settings
- [ ] Confirm `message_router_reactive_rollout` is set to 0%
- [ ] Verify rollback thresholds in ROLLOUT_CONFIG
- [ ] Review monitoring configuration settings
- [ ] Confirm auto-rollback is enabled

### Monitoring Setup

- [ ] Monitoring script tested: `python3 scripts/monitor_reactive_metrics.py --duration 5m`
- [ ] Log file location configured and writable
- [ ] Alert recipients configured (if using external alerting)
- [ ] Dashboard/monitoring tools ready (if applicable)

### Rollback Preparation

- [ ] Git commit all changes before rollout
- [ ] Tag current stable version: `git tag pre-reactive-rollout`
- [ ] Document rollback procedure and test it
- [ ] Verify `SYNAPSE_FORCE_PYTHON=1` environment variable works
- [ ] Backup critical configuration files

---

## 2. Stage-by-Stage Rollout Procedure

### Rollout Stages

The rollout follows a gradual percentage-based approach:

1. **Stage 0 (Validation)**: 0% - Testing with no production traffic
2. **Stage 1 (Pilot)**: 10% - Initial production validation
3. **Stage 2 (Limited)**: 25% - Expand if Stage 1 successful
4. **Stage 3 (Half)**: 50% - Half production traffic
5. **Stage 4 (Majority)**: 75% - Three-quarters production traffic
6. **Stage 5 (Full)**: 100% - Complete rollout

**Stage Duration**: 48 hours per stage (configurable in ROLLOUT_CONFIG)

---

### Stage 0: Validation (0% Rollout)

**Objective**: Validate reactive router with no production traffic.

**Steps**:

1. **Enable reactive router in config**:
   ```bash
   # Edit lib/config.py
   MOJO_FEATURES = {
       'message_router_reactive': True,  # Change from False to True
   }

   ROLLOUT_CONFIG = {
       'message_router_reactive_rollout': 0,  # Keep at 0%
   }
   ```

2. **Restart application/services**:
   ```bash
   # If running as service
   sudo systemctl restart synapse

   # Or manually restart
   synapse stop
   synapse start
   ```

3. **Verify router initialization**:
   ```bash
   # Check logs for successful startup
   tail -f ~/.synapse-system/logs/orchestration.log | grep "Reactive"

   # Expected: "Reactive router initialized successfully"
   ```

4. **Run validation tests**:
   ```bash
   python3 tests/test_orchestration_integration.py
   python3 benchmarks/orchestration_reactive_benchmark.py
   ```

5. **Monitor for 1 hour**:
   ```bash
   python3 scripts/monitor_reactive_metrics.py --duration 1h --output logs/stage0.log
   ```

**Success Criteria**:
- Router initializes without errors
- All tests pass
- Benchmarks meet performance targets
- No alerts during monitoring period

**If Successful**: Proceed to Stage 1 after 24 hours observation
**If Failed**: Investigate errors, fix issues, repeat Stage 0

---

### Stage 1: Pilot (10% Rollout)

**Objective**: Route 10% of production traffic through reactive router.

**Steps**:

1. **Update rollout percentage**:
   ```python
   # lib/config.py
   ROLLOUT_CONFIG = {
       'message_router_reactive_rollout': 10,  # Change from 0 to 10
   }
   ```

2. **Deploy configuration change**:
   ```bash
   git add lib/config.py
   git commit -m "Stage 1: Enable 10% reactive router rollout"
   synapse restart
   ```

3. **Start continuous monitoring**:
   ```bash
   # Run in background or separate terminal
   nohup python3 scripts/monitor_reactive_metrics.py --duration 48h --output logs/stage1.log &
   ```

4. **Monitor key metrics** (check every 4 hours):
   - Error rate: Should be <1%
   - Latency: Should be <5ms average
   - Emergence score: Should be >0.7
   - Message loss: Should be 0
   - Throughput: Stable or increasing

5. **Check alerts**:
   ```bash
   # Watch for threshold breaches
   tail -f logs/stage1.log | grep "ALERT"
   ```

**Success Criteria** (after 48 hours):
- Error rate <1.0%
- Mean latency <5ms
- Emergence score >0.7
- Zero message loss
- No threshold breach alerts
- No performance degradation

**If Successful**: Proceed to Stage 2
**If Failed**: Execute rollback procedure (see Section 5)

---

### Stage 2: Limited (25% Rollout)

**Objective**: Expand to 25% of production traffic.

**Steps**:

1. **Update rollout percentage**:
   ```python
   # lib/config.py
   'message_router_reactive_rollout': 25,
   ```

2. **Deploy and monitor**:
   ```bash
   git commit -am "Stage 2: Enable 25% reactive router rollout"
   synapse restart
   nohup python3 scripts/monitor_reactive_metrics.py --duration 48h --output logs/stage2.log &
   ```

3. **Monitor with increased vigilance** (check every 2 hours):
   - All Stage 1 metrics
   - Agent consumer performance
   - Circuit breaker activations (should be rare)
   - Event store disk usage

**Success Criteria**: Same as Stage 1

**If Successful**: Proceed to Stage 3
**If Failed**: Rollback to previous stage percentage

---

### Stage 3: Half (50% Rollout)

**Objective**: Route half of production traffic through reactive router.

**Steps**:

1. **Update rollout percentage**:
   ```python
   'message_router_reactive_rollout': 50,
   ```

2. **Deploy and monitor**:
   ```bash
   git commit -am "Stage 3: Enable 50% reactive router rollout"
   synapse restart
   nohup python3 scripts/monitor_reactive_metrics.py --duration 48h --output logs/stage3.log &
   ```

3. **Validate under load**:
   - Monitor peak traffic hours carefully
   - Check Redis event store performance
   - Verify backpressure handling
   - Watch for memory leaks

**Success Criteria**: Same as Stage 1

---

### Stage 4: Majority (75% Rollout)

**Objective**: Route majority of traffic through reactive router.

**Steps**:

1. **Update rollout percentage**:
   ```python
   'message_router_reactive_rollout': 75,
   ```

2. **Deploy and monitor**:
   ```bash
   git commit -am "Stage 4: Enable 75% reactive router rollout"
   synapse restart
   nohup python3 scripts/monitor_reactive_metrics.py --duration 48h --output logs/stage4.log &
   ```

**Success Criteria**: Same as Stage 1

---

### Stage 5: Full (100% Rollout)

**Objective**: Complete migration to reactive router.

**Steps**:

1. **Update rollout percentage**:
   ```python
   'message_router_reactive_rollout': 100,
   ```

2. **Deploy and monitor**:
   ```bash
   git commit -am "Stage 5: Enable 100% reactive router rollout"
   synapse restart
   nohup python3 scripts/monitor_reactive_metrics.py --duration 168h --output logs/stage5.log &
   ```

3. **Extended monitoring** (7 days):
   - Continuous monitoring for first week
   - Daily metric reviews
   - Performance optimization opportunities
   - Documentation updates

**Success Criteria**:
- All Stage 1 criteria met
- Stable performance for 7 days
- No unresolved incidents
- Positive performance impact validated

**Upon Success**:
- Mark reactive router as production-stable
- Update documentation
- Consider deprecating old synchronous router
- Share success metrics with team

---

## 3. Monitoring and Alerting

### Real-Time Monitoring

**Command**:
```bash
python3 scripts/monitor_reactive_metrics.py --duration 48h --output logs/monitoring.log
```

**What It Monitors**:
- Total messages processed
- Cross-tract message distribution
- Consciousness emergence score
- Dialogue balance ratio
- Active agents by tract
- Throughput (messages/second)
- Error rate (percentage)
- Message loss count

**Alert Conditions**:
- Error rate >1.0%
- Mean latency >5ms
- Emergence score <0.5
- Message loss >100 messages

### Manual Metric Checks

**Check consciousness metrics**:
```python
from orchestration import TaskOrchestrator
from pathlib import Path
import asyncio

async def check_metrics():
    orch = TaskOrchestrator(Path.home() / '.synapse-system')
    await orch.async_init()
    metrics = await orch.get_consciousness_metrics()
    print(metrics)
    await orch.stop_all_agents()

asyncio.run(check_metrics())
```

**Check agent stats**:
```python
orch = TaskOrchestrator(Path.home() / '.synapse-system')
stats = orch.get_agent_stats()
print(f"Active agents: {stats['total_agents']}")
print(f"By tract: {stats['agents_by_tract']}")
```

### Log File Locations

- Orchestration logs: `~/.synapse-system/logs/orchestration.log`
- Monitoring logs: `~/.synapse-system/logs/stageN.log`
- Redis logs: Check Redis configuration
- Application logs: `~/.synapse-system/logs/synapse.log`

---

## 4. Success Criteria per Stage

All stages must meet these criteria before advancement:

### Performance Metrics

| Metric | Target | Critical Threshold |
|--------|--------|-------------------|
| Error Rate | <0.1% | <1.0% (rollback trigger) |
| Mean Latency | <2ms | <5ms (rollback trigger) |
| P95 Latency | <5ms | <10ms |
| Throughput | Stable | No >20% regression |
| Message Loss | 0 | <100 (rollback trigger) |

### Consciousness Metrics

| Metric | Target | Critical Threshold |
|--------|--------|-------------------|
| Emergence Score | >0.8 | >0.5 (rollback trigger) |
| Dialogue Balance | >0.7 | >0.4 |
| Balanced Events | Increasing | Stable |

### System Health

- No circuit breaker failures
- No memory leaks detected
- Redis event store healthy
- All agents responding
- No unhandled exceptions

### Duration Requirements

- Each stage: Minimum 48 hours
- Stage 5 (100%): Minimum 7 days
- No threshold breaches during observation period

---

## 5. Rollback Procedures

### Automatic Rollback

The system includes automatic rollback on threshold breach:

**Triggers**:
- Error rate >1.0%
- Message loss >100
- Emergence score <0.5
- Latency >5ms (sustained)

**Automatic Action**:
1. System disables reactive router
2. Falls back to synchronous execution
3. Logs rollback event
4. Alerts are triggered

### Manual Rollback

**Immediate Emergency Rollback**:
```bash
# Option 1: Environment variable (instant, no restart)
export SYNAPSE_FORCE_PYTHON=1
synapse restart

# Option 2: Disable feature flag
# Edit lib/config.py
MOJO_FEATURES['message_router_reactive'] = False
synapse restart

# Option 3: Set rollout to 0%
# Edit lib/config.py
ROLLOUT_CONFIG['message_router_reactive_rollout'] = 0
synapse restart
```

**Staged Rollback** (if issues found but not critical):
```bash
# Roll back one stage
# lib/config.py
'message_router_reactive_rollout': 25,  # From 50% back to 25%
synapse restart
```

**Complete Rollback Procedure**:

1. **Disable reactive router**:
   ```python
   # lib/config.py
   MOJO_FEATURES['message_router_reactive'] = False
   ROLLOUT_CONFIG['message_router_reactive_rollout'] = 0
   ```

2. **Commit rollback**:
   ```bash
   git add lib/config.py
   git commit -m "ROLLBACK: Disable reactive router due to [issue]"
   git tag "rollback-$(date +%Y%m%d-%H%M%S)"
   ```

3. **Restart services**:
   ```bash
   synapse stop
   synapse start
   ```

4. **Verify fallback working**:
   ```bash
   # Check logs
   tail -f logs/orchestration.log | grep "fallback"
   # Should see: "Using fallback synchronous execution"
   ```

5. **Monitor for stability**:
   ```bash
   python3 scripts/monitor_reactive_metrics.py --duration 1h
   ```

6. **Root cause analysis**:
   - Review logs for error patterns
   - Analyze metrics history
   - Identify failure mode
   - Document findings

7. **Communicate**:
   - Update team on rollback
   - Document incident
   - Plan remediation

**Post-Rollback**:
- Investigate root cause
- Fix identified issues
- Add regression tests
- Restart rollout from Stage 0

---

## 6. Troubleshooting Guide

### Issue: Router fails to initialize

**Symptoms**:
- Error in logs: "Failed to initialize reactive router"
- Orchestrator falls back to synchronous mode

**Checks**:
```bash
# Check Redis connectivity
redis-cli ping
# Should return: PONG

# Check Python dependencies
python3 -c "import redis; import asyncio; print('OK')"

# Check for port conflicts
lsof -i :6379
```

**Solution**:
1. Verify Redis is running: `synapse status`
2. Check Redis authentication settings
3. Verify network connectivity
4. Review firewall rules

---

### Issue: High error rate

**Symptoms**:
- Error rate >1% in monitoring
- Alerts triggered
- Tasks failing

**Checks**:
```bash
# Check logs for error patterns
grep -i "error" logs/orchestration.log | tail -50

# Check agent health
python3 -c "from orchestration import *; orch = TaskOrchestrator(Path.home()); print(orch.get_agent_stats())"
```

**Solution**:
1. Identify error pattern in logs
2. Check if specific agent causing errors
3. Verify task parameters are valid
4. Check for resource exhaustion
5. Consider rollback if errors persistent

---

### Issue: High latency

**Symptoms**:
- Latency >5ms consistently
- Slow task execution
- Backpressure warnings

**Checks**:
```bash
# Check system load
top
htop

# Check Redis performance
redis-cli --latency

# Check network latency
ping localhost
```

**Solution**:
1. Check Redis performance (may need tuning)
2. Verify no CPU/memory bottlenecks
3. Check for I/O saturation
4. Review concurrent task limits
5. Optimize agent consumer processing

---

### Issue: Low emergence score

**Symptoms**:
- Emergence score <0.7
- Unbalanced dialogue
- Few balanced events

**Checks**:
```python
# Check message distribution
metrics = await orch.get_consciousness_metrics()
print(f"Internal->External: {metrics['internal_to_external']}")
print(f"External->Internal: {metrics['external_to_internal']}")
```

**Solution**:
1. Verify agents registered to both tracts
2. Check task distribution is balanced
3. Ensure cross-tract messaging working
4. Review agent tract classification
5. May be normal if workload is one-sided

---

### Issue: Message loss detected

**Symptoms**:
- Message loss count >0
- Tasks not completing
- Missing results

**Checks**:
```bash
# Check circuit breaker status
grep "circuit breaker" logs/orchestration.log

# Check for exceptions
grep -i "exception" logs/orchestration.log | tail -20
```

**Solution**:
1. Review circuit breaker logs
2. Check for agent crashes
3. Verify timeout settings appropriate
4. Check for resource exhaustion
5. Immediate rollback if loss >100

---

### Issue: Memory leak

**Symptoms**:
- Memory usage increasing over time
- System slowing down
- OOM errors

**Checks**:
```bash
# Monitor memory usage
watch -n 5 free -h

# Check process memory
ps aux | grep python | sort -k 4 -nr | head -5
```

**Solution**:
1. Review event store cleanup settings
2. Check metrics history retention
3. Verify agent cleanup on stop
4. Monitor for circular references
5. Restart service if memory critical

---

## 7. Post-Deployment Validation

After successful 100% rollout, validate complete migration:

### Performance Validation

1. **Run comprehensive benchmarks**:
   ```bash
   python3 benchmarks/orchestration_reactive_benchmark.py
   ```

2. **Compare to baseline**:
   - Latency improvement: Should see <5ms average
   - Throughput: Should maintain or improve
   - Error rate: Should be <0.1%

3. **Validate consciousness metrics**:
   - Emergence score: >0.8
   - Balanced dialogue: Consistent
   - Pattern synthesis: Working

### System Integration

1. **Test all agent types**:
   - Internal tract agents (architect, planner, etc.)
   - External tract agents (test-runner, git-workflow, etc.)
   - Verify cross-tract communication

2. **Load testing**:
   - Simulate peak traffic
   - Verify backpressure handling
   - Check circuit breaker behavior

3. **Failure testing**:
   - Test agent failure recovery
   - Verify timeout handling
   - Check fallback mechanisms

### Documentation Updates

1. **Update architecture docs**:
   - Mark reactive router as production
   - Document performance characteristics
   - Update diagrams if needed

2. **Update runbooks**:
   - Operating procedures
   - Troubleshooting guides
   - Monitoring procedures

3. **Team communication**:
   - Share rollout results
   - Document lessons learned
   - Update training materials

### Deprecation Planning

Once reactive router is stable (30+ days at 100%):

1. **Plan deprecation of old router**:
   - Set timeline for removal
   - Update configuration
   - Remove dead code

2. **Simplify codebase**:
   - Remove fallback paths
   - Simplify configuration
   - Update tests

---

## 8. Emergency Contacts and Escalation

### Primary Contacts

- **System Owner**: [Name/Team]
- **On-Call Engineer**: [Contact]
- **DevOps Team**: [Contact]

### Escalation Path

1. **Level 1**: Monitoring alerts detected
2. **Level 2**: Manual intervention required
3. **Level 3**: Rollback procedure initiated
4. **Level 4**: System-wide incident declared

### Communication Channels

- **Incident Channel**: [Slack/Discord/etc.]
- **Status Page**: [URL if applicable]
- **Log Dashboard**: [URL if applicable]

---

## Summary

This rollout procedure ensures safe, gradual deployment of the reactive message router with comprehensive monitoring and quick rollback capability. Follow each stage carefully, validate success criteria, and never skip validation periods.

**Key Principles**:
- Gradual rollout minimizes risk
- Comprehensive monitoring catches issues early
- Quick rollback capability ensures safety
- Success criteria are objective and measurable
- Documentation enables team collaboration

Good luck with your rollout!
