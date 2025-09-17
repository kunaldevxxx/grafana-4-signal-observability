# Metrics Query Catalog

This document contains useful Prometheus queries for monitoring the sample application.

## Golden Signals (SRE)

### Request Rate
```promql
# Total request rate
sum(rate(http_requests_total[5m]))

# Request rate by endpoint
sum(rate(http_requests_total[5m])) by (endpoint)

# Request rate by status code
sum(rate(http_requests_total[5m])) by (status)
```

### Error Rate
```promql
# Overall error rate (percentage)
sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) * 100

# Error rate by endpoint
sum(rate(http_requests_total{status=~"5.."}[5m])) by (endpoint) / sum(rate(http_requests_total[5m])) by (endpoint) * 100

# 4xx error rate
sum(rate(http_requests_total{status=~"4.."}[5m])) / sum(rate(http_requests_total[5m])) * 100
```

### Latency
```promql
# P50 latency
histogram_quantile(0.50, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))

# P95 latency
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))

# P99 latency
histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))

# Average latency
sum(rate(http_request_duration_seconds_sum[5m])) / sum(rate(http_request_duration_seconds_count[5m]))
```

### Saturation
```promql
# Service availability
up{job="sample-app"}

# Request duration trend
increase(http_request_duration_seconds_sum[1h]) / increase(http_request_duration_seconds_count[1h])
```

## Business Metrics
```promql
# Business operations rate
sum(rate(business_operations_total[5m])) by (operation_type)

# Slow operations
sum(rate(business_operations_total{operation_type="slow_operation"}[5m]))

# External call success rate
sum(rate(business_operations_total{operation_type="external_call_success"}[5m])) / 
(sum(rate(business_operations_total{operation_type="external_call_success"}[5m])) + 
 sum(rate(business_operations_total{operation_type="external_call_failure"}[5m]))) * 100
```

## Infrastructure Metrics
```promql
# Memory usage (if available)
process_resident_memory_bytes{job="sample-app"}

# CPU usage (if available)
rate(process_cpu_seconds_total{job="sample-app"}[5m]) * 100

# File descriptors
process_open_fds{job="sample-app"}
```

## Recording Rules
The following recording rules are pre-computed for better performance:

```promql
# Use these instead of calculating on-the-fly
sample_app:http_requests:rate5m
sample_app:http_request_duration:p95_5m
sample_app:http_request_duration:p99_5m
sample_app:error_rate:5m
```

## Alerting Queries
```promql
# High error rate alert
rate(http_requests_total{status=~"5.."}[5m]) > 0.1

# High latency alert
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1

# Service down alert
up{job="sample-app"} == 0
```