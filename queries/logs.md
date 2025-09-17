# Logs Query Catalog

This document contains useful LogQL queries for searching and analyzing logs.

## Basic Log Queries

### Application Logs
```logql
# All application logs
{container_name=~".*sample-app.*"}

# Logs from specific service
{service_name="sample-app"}

# Logs in time range
{container_name=~".*sample-app.*"} |= "2023-"
```

## Log Level Filtering
```logql
# Error logs only
{container_name=~".*sample-app.*"} |= "ERROR"

# Warning and error logs
{container_name=~".*sample-app.*"} |~ "ERROR|WARNING"

# Info logs
{container_name=~".*sample-app.*"} |= "INFO"

# Debug logs
{container_name=~".*sample-app.*"} |= "DEBUG"
```

## Structured Log Parsing
```logql
# Parse JSON logs
{container_name=~".*sample-app.*"} | json

# Extract specific fields
{container_name=~".*sample-app.*"} | json | line_format "{{.message}}"

# Filter by extracted fields
{container_name=~".*sample-app.*"} | json | level="ERROR"
```

## Pattern Matching
```logql
# HTTP request logs
{container_name=~".*sample-app.*"} |~ "GET|POST|PUT|DELETE"

# Error patterns
{container_name=~".*sample-app.*"} |~ "exception|error|fail"

# Slow operation logs
{container_name=~".*sample-app.*"} |= "slow operation"

# External API calls
{container_name=~".*sample-app.*"} |= "external API"
```

## Log Metrics
```logql
# Count of log lines per minute
count_over_time({container_name=~".*sample-app.*"}[1m])

# Error log rate
rate({container_name=~".*sample-app.*"} |= "ERROR" [5m])

# Bytes per second
bytes_rate({container_name=~".*sample-app.*"}[1m])

# Bytes over time
bytes_over_time({container_name=~".*sample-app.*"}[1m])
```

## Advanced Queries

### Log Aggregations
```logql
# Top error messages
topk(10, count by (message) ({container_name=~".*sample-app.*"} |= "ERROR" | json))

# Request duration from logs
{container_name=~".*sample-app.*"} |= "duration" | regexp "duration=(?P<duration>[\\d\\.]+)" | unwrap duration | avg_over_time(1m)

# Count by endpoint
count by (endpoint) ({container_name=~".*sample-app.*"} | json | endpoint != "")
```

### Correlation Queries
```logql
# Logs for specific trace ID
{container_name=~".*sample-app.*"} |= "trace_id=abc123"

# Logs around error time
{container_name=~".*sample-app.*"} |= "ERROR" 

# Request and response correlation
{container_name=~".*sample-app.*"} |~ "request_id=\\w+" | regexp "request_id=(?P<req_id>\\w+)"
```

## Performance Monitoring
```logql
# Slow queries (if logged)
{container_name=~".*sample-app.*"} |~ "duration" | regexp "duration=(?P<duration>[\\d\\.]+)" | unwrap duration | duration > 1

# Memory allocation logs
{container_name=~".*sample-app.*"} |= "memory" | regexp "memory=(?P<memory>[\\d]+)" | unwrap memory

# Database query logs
{container_name=~".*sample-app.*"} |= "query" | json | query_time > 100
```

## Troubleshooting Queries
```logql
# Stack traces
{container_name=~".*sample-app.*"} |= "Traceback"

# Connection errors
{container_name=~".*sample-app.*"} |~ "connection.*error|timeout|refused"

# Authentication failures
{container_name=~".*sample-app.*"} |~ "auth.*fail|unauthorized|forbidden"

# Rate limiting
{container_name=~".*sample-app.*"} |= "rate limit"
```

## Log Context
```logql
# Get context around errors (before and after)
{container_name=~".*sample-app.*"} |= "ERROR" | line_format "{{.timestamp}} {{.level}} {{.message}}"

# Show surrounding log lines
{container_name=~".*sample-app.*"} and {container_name=~".*sample-app.*"} |= "ERROR"
```