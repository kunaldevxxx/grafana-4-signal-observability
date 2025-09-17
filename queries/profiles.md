# Profiles Query Catalog

This document contains useful queries and techniques for analyzing application profiles with Pyroscope.

## Basic Profile Queries

### CPU Profiling
```
# Basic CPU profile
sample-app{}

# CPU profile for specific time range
sample-app{}[5m]

# CPU profile with filters
sample-app{job="sample-app"}
```

### Memory Profiling
```
# Heap allocations
sample-app:alloc_objects:count:space:bytes{}

# In-use memory
sample-app:inuse_objects:count:inuse:bytes{}

# Memory allocations over time
sample-app:alloc_space:bytes:space:bytes{}
```

## Filtering and Aggregation

### Service Filtering
```
# Specific service instance
sample-app{instance="sample-app-1"}

# Multiple instances
sample-app{instance=~"sample-app-.*"}

# Version-specific profiling
sample-app{version="1.0.0"}
```

### Function-Level Analysis
```
# Focus on specific functions
sample-app{} | grep("slow_operation")

# Exclude system functions
sample-app{} | grep -v("^runtime\.")

# Focus on application code only
sample-app{} | grep("app\.")
```

## Performance Analysis

### CPU Hotspots
```
# Top CPU consuming functions
sample-app{} | top(10)

# CPU usage by package
sample-app{} | group_by("package")

# Relative CPU usage
sample-app{} | diff(baseline_profile)
```

### Memory Analysis
```
# Memory allocation hotspots
sample-app:alloc_space:bytes:space:bytes{} | top(10)

# Memory leak detection
sample-app:inuse_space:bytes:inuse:bytes{} | diff(previous_snapshot)

# Allocation patterns
sample-app:alloc_objects:count:space:bytes{} | rate()
```

## Comparative Analysis

### Before/After Comparison
```
# Compare with baseline
sample-app{} | diff(sample-app{}[1h])

# Compare different versions
sample-app{version="1.0.0"} vs sample-app{version="1.1.0"}

# Compare different environments
sample-app{env="dev"} vs sample-app{env="prod"}
```

### Load Testing Analysis
```
# Profile during load test
sample-app{}[load_test_duration]

# Compare low vs high load
sample-app{} | split_by(load_level)

# Performance degradation analysis
sample-app{} | trend_analysis()
```

## Troubleshooting Scenarios

### High CPU Usage
```
# Find CPU hotspots
sample-app{} | filter(cpu_usage > 80%) | top(5)

# Identify inefficient loops
sample-app{} | grep("for|while") | duration_analysis()

# Recursive function analysis
sample-app{} | call_graph() | depth > 10
```

### Memory Issues
```
# Memory leak investigation
sample-app:inuse_space:bytes:inuse:bytes{} | growth_rate() > 1MB/min

# Large object allocations
sample-app:alloc_space:bytes:space:bytes{} | filter(size > 1MB)

# Garbage collection pressure
sample-app{} | gc_analysis() | frequency > normal
```

### Performance Regression
```
# Regression detection
sample-app{} | regression_analysis(baseline_date)

# Slow endpoint identification
sample-app{} | filter(endpoint="/slow") | performance_delta()

# Function performance degradation
sample-app{} | function_perf_delta() | degradation > 20%
```

## Advanced Profiling Techniques

### Differential Profiling
```
# Compare profiles from different time periods
diff(sample-app{}[10m], sample-app{}[10m offset 1h])

# Feature flag impact analysis
diff(
  sample-app{feature_flag="enabled"}[5m], 
  sample-app{feature_flag="disabled"}[5m]
)
```

### Continuous Profiling Analysis
```
# Trend analysis over time
sample-app{} | time_series() | moving_average(window=10m)

# Periodic performance patterns
sample-app{} | pattern_detection() | daily_cycle()

# Performance anomaly detection
sample-app{} | anomaly_detection() | threshold=2_std_dev
```

### Multi-Dimensional Analysis
```
# Profile by user type
sample-app{} | group_by(user_type) | compare()

# Geographic performance analysis
sample-app{} | group_by(region) | latency_analysis()

# Device-specific profiling
sample-app{} | group_by(device_type) | resource_usage()
```

## Profile Types and Use Cases

### CPU Profiles
- **Use Case**: Identify CPU bottlenecks, hot functions
- **Query Pattern**: `sample-app{profile_type="cpu"}`
- **Analysis**: Look for functions consuming >10% CPU

### Heap Profiles
- **Use Case**: Memory allocation analysis, leak detection
- **Query Pattern**: `sample-app{profile_type="heap"}`
- **Analysis**: Track allocation growth over time

### Goroutine Profiles (Go apps)
- **Use Case**: Concurrency analysis, deadlock detection
- **Query Pattern**: `sample-app{profile_type="goroutine"}`
- **Analysis**: Monitor goroutine count trends

### Mutex Profiles
- **Use Case**: Lock contention analysis
- **Query Pattern**: `sample-app{profile_type="mutex"}`
- **Analysis**: Identify synchronization bottlenecks

## Integration with Other Signals

### Trace Correlation
```
# Correlate slow traces with CPU profiles
sample-app{trace_id="abc123"} | during(slow_trace_timespan)

# Profile during high trace latency
sample-app{} | filter(trace_p95_latency > 1s)
```

### Metrics Correlation
```
# Profile during high error rate
sample-app{} | during(error_rate_spike)

# Resource usage correlation
sample-app{} | correlate_with(memory_usage_metric)
```

### Log Correlation
```
# Profile during logged errors
sample-app{} | during(error_log_timespan)

# Performance during warning periods
sample-app{} | correlate_with(warning_log_frequency)
```

## Best Practices

### Query Optimization
- Use time ranges to limit data: `sample-app{}[5m]`
- Filter early: `sample-app{service="web"}`
- Use appropriate aggregation levels
- Leverage tags for efficient filtering

### Analysis Workflow
1. Start with overview: `sample-app{}`
2. Identify hotspots: `| top(10)`
3. Drill down: `| grep("suspect_function")`
4. Compare: `| diff(baseline)`
5. Correlate: `| during(incident_timespan)`

### Performance Monitoring
- Set up continuous profiling
- Define performance baselines
- Monitor key functions regularly
- Alert on performance regressions