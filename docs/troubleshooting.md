# Troubleshooting Guide

This guide provides step-by-step troubleshooting procedures for common observability scenarios.

## Common Issues and Solutions

### 1. High Response Times

#### Symptoms
- P95 latency > 1 second
- User complaints about slow responses
- Increased timeout errors

#### Investigation Steps

1. **Check Metrics**
   ```promql
   # Check overall latency trend
   histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
   
   # Identify slow endpoints
   histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) by (endpoint)
   ```

2. **Analyze Traces**
   ```traceql
   # Find slow traces
   {duration > 1s && service.name="sample-app"}
   
   # Identify bottleneck spans
   {service.name="sample-app"} >> {duration > 500ms}
   ```

3. **Check Logs**
   ```logql
   # Look for performance warnings
   {container_name=~".*sample-app.*"} |= "slow" or "timeout"
   
   # Check for errors during slow periods
   {container_name=~".*sample-app.*"} |= "ERROR" 
   ```

4. **Profile Analysis**
   ```
   # Check CPU usage during slow periods
   sample-app{} | during(slow_response_timespan)
   
   # Identify CPU hotspots
   sample-app{} | top(10)
   ```

#### Common Causes and Solutions

- **Database queries**: Optimize queries, add indexes
- **External API calls**: Implement caching, circuit breakers
- **CPU-intensive operations**: Optimize algorithms, add caching
- **Memory pressure**: Increase memory, optimize data structures

### 2. High Error Rates

#### Symptoms
- Error rate > 5%
- Increased 5xx responses
- User-reported failures

#### Investigation Steps

1. **Check Error Metrics**
   ```promql
   # Overall error rate
   rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) * 100
   
   # Error rate by endpoint
   rate(http_requests_total{status=~"5.."}[5m]) by (endpoint) / rate(http_requests_total[5m]) by (endpoint) * 100
   ```

2. **Analyze Error Traces**
   ```traceql
   # Find error traces
   {status=error && service.name="sample-app"}
   
   # Group by error type
   {status=error} | group_by(error.type)
   ```

3. **Check Error Logs**
   ```logql
   # Recent error logs
   {container_name=~".*sample-app.*"} |= "ERROR" 
   
   # Parse error patterns
   {container_name=~".*sample-app.*"} |= "ERROR" | json | error_type != ""
   ```

4. **Profile During Errors**
   ```
   # Profile during error spikes
   sample-app{} | during(error_spike_timespan)
   ```

#### Common Solutions

- **Dependency failures**: Implement circuit breakers, retries
- **Resource exhaustion**: Scale horizontally, optimize resource usage
- **Configuration issues**: Review and validate configurations
- **Code bugs**: Use traces to identify failing code paths

### 3. Service Unavailability

#### Symptoms
- Service health checks failing
- Complete request failures
- Container/pod restarts

#### Investigation Steps

1. **Check Service Status**
   ```promql
   # Service availability
   up{job="sample-app"}
   
   # Container restart rate
   rate(container_restart_total[5m])
   ```

2. **Check Infrastructure Logs**
   ```logql
   # Container logs
   {container_name=~".*sample-app.*"} |= "exit" or "killed" or "restart"
   
   # System logs
   {job="syslog"} |= "sample-app"
   ```

3. **Resource Analysis**
   ```promql
   # Memory usage
   container_memory_usage_bytes{container="sample-app"}
   
   # CPU usage
   rate(container_cpu_usage_seconds_total{container="sample-app"}[5m])
   ```

#### Common Solutions

- **Resource limits**: Increase memory/CPU limits
- **Health check issues**: Fix health check endpoints
- **Dependency failures**: Check downstream services
- **Configuration errors**: Validate environment variables

### 4. Memory Leaks

#### Symptoms
- Gradually increasing memory usage
- Out of memory errors
- Container restarts due to memory limits

#### Investigation Steps

1. **Memory Metrics**
   ```promql
   # Memory usage trend
   container_memory_usage_bytes{container="sample-app"}
   
   # Memory growth rate
   increase(container_memory_usage_bytes{container="sample-app"}[1h])
   ```

2. **Memory Profiles**
   ```
   # Heap allocation growth
   sample-app:inuse_space:bytes:inuse:bytes{} | growth_rate()
   
   # Top memory allocators
   sample-app:alloc_space:bytes:space:bytes{} | top(10)
   ```

3. **Application Logs**
   ```logql
   # Memory-related logs
   {container_name=~".*sample-app.*"} |= "memory" or "heap" or "gc"
   ```

#### Solutions

- **Fix memory leaks**: Use profiles to identify leaking functions
- **Optimize data structures**: Reduce memory footprint
- **Implement proper cleanup**: Ensure resources are released
- **Tune garbage collection**: Optimize GC settings

## Performance Optimization

### 1. Metrics Optimization

#### Reduce Cardinality
```promql
# Before: High cardinality
http_requests_total{user_id="12345", session_id="abcdef", request_id="xyz"}

# After: Controlled cardinality
http_requests_total{endpoint="/api/users", method="GET", status="200"}
```

#### Use Recording Rules
```yaml
# prometheus/rules/optimized.yml
groups:
  - name: optimized-queries
    rules:
      - record: api:request_rate:5m
        expr: sum(rate(http_requests_total[5m])) by (endpoint)
      
      - record: api:error_rate:5m
        expr: sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))
```

### 2. Logs Optimization

#### Structured Logging
```python
# Good: Structured logs
logger.info("Request processed", extra={
    "endpoint": "/api/users",
    "duration": 0.25,
    "status": 200,
    "user_id": 12345
})

# Avoid: Unstructured logs
logger.info(f"Processed request to /api/users in 0.25s with status 200 for user 12345")
```

#### Log Sampling
```python
# Sample logs for high-volume endpoints
if should_sample_log(endpoint, rate=0.1):  # 10% sampling
    logger.info("Request details", extra=details)
```

### 3. Traces Optimization

#### Smart Sampling
```yaml
# tempo.yaml - Probabilistic sampling
sampling:
  probabilistic:
    rate: 0.1  # 10% of traces
  
  # Higher sampling for errors
  error_sampling:
    rate: 1.0  # 100% of error traces
```

#### Span Optimization
```python
# Minimize span overhead
with tracer.start_as_current_span("critical_operation", kind=SpanKind.INTERNAL):
    # Only add essential attributes
    span.set_attribute("operation.type", "database_query")
    result = database.query()
```

### 4. Profiles Optimization

#### Selective Profiling
```python
# Profile only during specific conditions
if should_profile(load_level="high", error_rate="> 5%"):
    pyroscope.tag_wrapper({"scenario": "high_load"})(function)()
```

## Monitoring Best Practices

### 1. Alert Design

#### Good Alerts
```yaml
# Alert on symptoms, not causes
- alert: HighErrorRate
  expr: api:error_rate:5m > 0.05
  for: 2m
  
- alert: HighLatency
  expr: api:latency:p95:5m > 1
  for: 5m
```

#### Avoid Alert Fatigue
- Set appropriate thresholds based on SLOs
- Use `for` duration to avoid flapping
- Group related alerts
- Implement alert runbooks

### 2. Dashboard Design

#### Key Principles
- Start with overview, drill down to details
- Use consistent time ranges across panels
- Include both rate and error metrics
- Show trends and percentiles, not just averages

#### Example Dashboard Structure
```
├── Overview Row (SLI metrics)
├── Traffic Row (request rates, top endpoints)
├── Errors Row (error rates, types, traces)
├── Latency Row (percentiles, distributions)
└── Saturation Row (resource usage, capacity)
```

### 3. Data Retention

#### Optimization Strategy
```yaml
# Short-term high resolution
prometheus:
  retention: 15d
  resolution: 15s

# Long-term lower resolution  
thanos:
  retention: 1y
  downsampling:
    - resolution: 5m
      retention: 90d
    - resolution: 1h
      retention: 1y
```

## Incident Response

### 1. Incident Workflow

1. **Detection**: Automated alerts or user reports
2. **Triage**: Assess severity and impact
3. **Investigation**: Use observability data to find root cause
4. **Mitigation**: Apply immediate fixes
5. **Resolution**: Implement permanent solution
6. **Post-mortem**: Learn and improve

### 2. Investigation Runbook

#### Step 1: Overview
```promql
# Check service health
up{job="sample-app"}

# Check error rate
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])

# Check latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

#### Step 2: Deep Dive
```traceql
# Find problematic traces
{status=error && duration > 5s}

# Correlate with logs
{service.name="sample-app"} && {span.status=error}
```

#### Step 3: Root Cause
```
# Profile during incident
sample-app{} | during(incident_timespan)

# Compare with baseline
sample-app{} | diff(baseline_profile)
```

### 3. Communication

#### Status Updates
- Use metrics dashboards for objective status
- Include error rates, latency, and availability
- Provide ETAs based on observability data
- Share investigation findings from traces/logs

## Capacity Planning

### 1. Growth Prediction
```promql
# Request growth rate
predict_linear(
    api:request_rate:5m[7d], 
    86400 * 30  # 30 days
)

# Resource utilization trend
predict_linear(
    container_memory_usage_bytes[7d],
    86400 * 30
)
```

### 2. Load Testing Validation
- Monitor all 4 signals during load tests
- Compare performance profiles under different loads
- Validate alert thresholds with realistic traffic
- Document breaking points and mitigation strategies