# Traces Query Catalog

This document contains useful TraceQL queries for searching and analyzing distributed traces.

## Basic Trace Queries

### Service-Based Queries
```traceql
# All traces for sample-app service
{service.name="sample-app"}

# Traces for specific operation
{service.name="sample-app" && name="slow_operation"}

# Traces for HTTP requests
{service.name="sample-app" && span.kind="server"}
```

## Duration-Based Queries
```traceql
# Slow traces (over 1 second)
{duration > 1s}

# Very slow traces (over 5 seconds)
{duration > 5s}

# Fast traces (under 100ms)
{duration < 100ms}

# Traces in duration range
{duration >= 500ms && duration <= 2s}
```

## Status and Error Queries
```traceql
# Error traces
{status = error}

# Successful traces
{status = ok}

# Traces with specific error messages
{span.status_message =~ ".*timeout.*"}
```

## Attribute-Based Queries
```traceql
# HTTP method filtering
{http.method="POST"}

# Status code filtering
{http.status_code >= 400}

# Specific endpoints
{http.route="/slow"}

# User agent filtering
{http.user_agent =~ ".*Chrome.*"}
```

## Complex Queries

### Multi-Service Traces
```traceql
# Traces spanning multiple services
{service.name="sample-app"} && {service.name="external-service"}

# Traces with database calls
{service.name="sample-app"} && {db.system="postgresql"}

# Traces with external API calls
{service.name="sample-app"} && {http.url =~ ".*external.*"}
```

### Performance Analysis
```traceql
# Traces with slow database queries
{db.operation="SELECT" && duration > 1s}

# Traces with many spans (complex operations)
{traceDuration > 2s && spanCount > 10}

# Traces with external timeouts
{http.status_code = 408 || span.status_message =~ ".*timeout.*"}
```

### Business Logic Queries
```traceql
# Business operation traces
{operation.type="slow_operation"}

# Customer-specific traces (if customer ID is tagged)
{customer.id="12345"}

# Feature flag traces
{feature.flag="new-feature" && feature.enabled=true}
```

## Aggregation and Analysis

### Root Span Analysis
```traceql
# Only root spans
{span.kind="server" && parent.span_id=""}

# Root spans with errors
{span.kind="server" && parent.span_id="" && status=error}
```

### Resource Analysis
```traceql
# High memory usage traces
{resource.memory.usage > 1000000}

# Specific version traces
{service.version="1.0.0"}

# Environment-specific traces
{deployment.environment="production"}
```

## Correlation Queries

### Log Correlation
```traceql
# Traces that should have corresponding logs
{service.name="sample-app" && log.level="ERROR"}

# Traces with specific log correlation IDs
{correlation.id="abc-123"}
```

### Metric Correlation
```traceql
# Traces during high error rate periods
{service.name="sample-app" && time >= "2023-01-01T10:00:00Z" && time <= "2023-01-01T11:00:00Z"}

# Traces with custom metric attributes
{custom.metric.value > 100}
```

## Troubleshooting Queries

### Error Investigation
```traceql
# Recent error traces
{status=error && duration >= now-1h}

# Specific error types
{error.type="TimeoutError"}

# Error traces by endpoint
{status=error && http.route="/external"}
```

### Performance Investigation
```traceql
# Slowest traces in last hour
{duration > 2s && start >= now-1h}

# Traces with unusual patterns
{spanCount > 20 || depth > 5}

# Memory leak investigation
{resource.memory.usage > previous.resource.memory.usage * 2}
```

### Dependency Analysis
```traceql
# External service dependencies
{service.name="sample-app"} >> {service.name !~ "sample-app"}

# Database dependency analysis
{service.name="sample-app"} >> {db.system=~".*"}

# Cache hit/miss analysis
{cache.hit=true} vs {cache.hit=false}
```

## Advanced Features

### Structural Queries
```traceql
# Traces with specific span hierarchy
{service.name="sample-app"} >> {operation.name="database_query"} >> {operation.name="cache_lookup"}

# Parallel span analysis
{service.name="sample-app"} && parallel({operation.name="task1"}, {operation.name="task2"})
```

### Statistical Queries
```traceql
# Percentile analysis
{service.name="sample-app" && duration > percentile(duration, 95)}

# Rate analysis
{service.name="sample-app" && rate(status=error) > 0.05}
```

## Span-Specific Queries
```traceql
# Specific span operations
{name="slow_operation"}

# Span attributes
{span.custom_attribute="value"}

# Span events
{span.event.name="exception"}

# Resource attributes
{resource.service.name="sample-app"}
```

## Time-Based Queries
```traceql
# Recent traces
{start >= now-15m}

# Specific time window
{start >= "2023-01-01T00:00:00Z" && start <= "2023-01-01T23:59:59Z"}

# Duration within time range
{duration >= 1s && start >= now-1h}
```