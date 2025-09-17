# Setup and Usage Guide

This guide provides comprehensive instructions for setting up and using the 4-signal observability stack.

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- At least 4GB of available RAM
- Ports 3000, 8080, 9090, 3100, 3200, 4040 available

### 1. Clone and Start
```bash
git clone <repository-url>
cd grafana-4-signal-observability
docker-compose up -d
```

### 2. Access Services
- **Grafana**: http://localhost:3000 (admin/admin)
- **Sample App**: http://localhost:8080
- **Prometheus**: http://localhost:9090
- **Pyroscope**: http://localhost:4040

### 3. Generate Test Data
```bash
# Generate some load
curl http://localhost:8080/generate-load

# Test slow operations
curl http://localhost:8080/slow

# Test error scenarios
curl "http://localhost:8080/error?type=500"
```

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Sample App    │    │    Grafana      │    │   Prometheus    │
│   (Metrics,     │────│   (Dashboards)  │────│   (Metrics)     │
│    Traces,      │    │                 │    │                 │
│    Logs,        │    └─────────────────┘    └─────────────────┘
│    Profiles)    │              │                       │
└─────────────────┘              │                       │
         │                       │                       │
         │              ┌─────────────────┐    ┌─────────────────┐
         │              │      Loki       │    │     Tempo       │
         └──────────────│     (Logs)      │    │   (Traces)      │
                        │                 │    │                 │
                        └─────────────────┘    └─────────────────┘
                                 │                       │
                        ┌─────────────────┐    ┌─────────────────┐
                        │    Promtail     │    │   Pyroscope     │
                        │ (Log Shipper)   │    │  (Profiles)     │
                        └─────────────────┘    └─────────────────┘
```

## Service Configuration

### Sample Application

The sample application demonstrates all 4 observability signals:

#### Endpoints
- `GET /` - Home page with endpoint list
- `GET /slow` - Simulates slow operations (1-3s)
- `GET /error?type={500|404|timeout|random}` - Error scenarios
- `GET /external` - External API calls
- `GET /generate-load` - Load generation
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics

#### Instrumentation
```python
# OpenTelemetry traces
from opentelemetry import trace
tracer = trace.get_tracer(__name__)

# Prometheus metrics
from prometheus_client import Counter, Histogram
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests')

# Structured logging
import logging
logger = logging.getLogger(__name__)

# Pyroscope profiling
import pyroscope
pyroscope.configure(application_name="sample-app")
```

### Prometheus Configuration

#### Scrape Targets
```yaml
# prometheus/prometheus.yml
scrape_configs:
  - job_name: 'sample-app'
    static_configs:
      - targets: ['sample-app:8080']
    scrape_interval: 5s
```

#### Recording Rules
```yaml
# prometheus/rules/sample-app.yml
groups:
  - name: sample-app-recording
    rules:
      - record: sample_app:http_requests:rate5m
        expr: rate(http_requests_total[5m])
```

### Grafana Configuration

#### Datasources
All datasources are automatically configured:
- **Prometheus**: http://prometheus:9090
- **Loki**: http://loki:3100  
- **Tempo**: http://tempo:3200
- **Pyroscope**: http://pyroscope:4040

#### Dashboards
- Pre-configured 4-signal dashboard
- Automatic correlation between signals
- Ready-to-use panels for each signal type

## Using the Observability Stack

### 1. Metrics Analysis

#### Key Metrics to Monitor
```promql
# Golden Signals
- Request Rate: sum(rate(http_requests_total[5m]))
- Error Rate: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])
- Latency P95: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
- Saturation: up{job="sample-app"}
```

#### Dashboard Usage
1. Open Grafana at http://localhost:3000
2. Login with admin/admin
3. Navigate to "4-Signal Observability Dashboard"
4. Use time range picker to focus on specific periods
5. Click metrics to drill down

### 2. Logs Analysis

#### Log Sources
- Application logs from sample app
- Container logs via Promtail
- System logs (if available)

#### Useful Queries
```logql
# All application logs
{container_name=~".*sample-app.*"}

# Error logs only
{container_name=~".*sample-app.*"} |= "ERROR"

# Slow operation logs
{container_name=~".*sample-app.*"} |= "slow operation"
```

#### Log Analysis Workflow
1. Start with broad query: `{container_name=~".*sample-app.*"}`
2. Filter by level: `|= "ERROR"`
3. Parse structured logs: `| json`
4. Extract metrics: `| count_over_time([5m])`

### 3. Traces Analysis

#### Trace Discovery
```traceql
# All application traces
{service.name="sample-app"}

# Slow traces
{duration > 1s}

# Error traces
{status=error}
```

#### Trace Analysis Workflow
1. Search traces by service: `{service.name="sample-app"}`
2. Filter by duration or status
3. Examine span hierarchy and timing
4. Correlate with logs using trace IDs
5. Jump to related metrics

### 4. Profiles Analysis

#### Profile Types Available
- **CPU**: Identify performance bottlenecks
- **Memory**: Track allocations and leaks
- **Custom**: Application-specific profiles

#### Profile Analysis Workflow
1. Access Pyroscope at http://localhost:4040
2. Select application: "sample-app"
3. Choose profile type and time range
4. Analyze flame graph
5. Compare different time periods

## Advanced Usage

### 1. Correlation Across Signals

#### Trace to Logs
1. Find problematic trace in Tempo
2. Copy trace ID
3. Search logs: `{container_name=~".*sample-app.*"} |= "trace_id_here"`

#### Metrics to Traces
1. Identify high latency period in metrics
2. Search traces for that time range: `{duration > 1s && start >= time_range}`
3. Analyze slow traces

#### Logs to Profiles
1. Find performance warnings in logs
2. Switch to Pyroscope for the same time range
3. Identify CPU/memory hotspots

### 2. Alerting Setup

#### Prometheus Alerts
```yaml
# Custom alerts in prometheus/rules/
groups:
  - name: custom-alerts
    rules:
      - alert: CustomHighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        annotations:
          summary: "Custom latency threshold exceeded"
```

#### Grafana Alerts
1. Go to Alerting > Alert Rules
2. Create new rule based on any query
3. Configure notification channels
4. Test alert conditions

### 3. Custom Instrumentation

#### Adding Custom Metrics
```python
# In your application code
from prometheus_client import Counter, Histogram

BUSINESS_OPERATIONS = Counter(
    'business_operations_total',
    'Business operations',
    ['operation_type', 'result']
)

# Usage
BUSINESS_OPERATIONS.labels(
    operation_type='user_signup',
    result='success'
).inc()
```

#### Adding Custom Traces
```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("custom_operation") as span:
    span.set_attribute("custom.attribute", "value")
    # Your business logic here
```

#### Custom Log Fields
```python
import logging

logger = logging.getLogger(__name__)

# Structured logging
logger.info("Business event", extra={
    "event_type": "user_action",
    "user_id": 12345,
    "action": "purchase",
    "amount": 99.99
})
```

## Production Considerations

### 1. Security
- Change default passwords
- Configure authentication
- Set up TLS/SSL certificates
- Network security and firewall rules

### 2. Performance
- Adjust retention policies
- Configure appropriate scrape intervals
- Optimize query performance
- Monitor resource usage

### 3. High Availability
- Run multiple instances of each service
- Configure persistent storage
- Set up backup strategies
- Plan for disaster recovery

### 4. Scaling
- Horizontal scaling for stateless services
- Sharding for large datasets
- Load balancing configuration
- Resource planning and monitoring

## Troubleshooting

### Common Issues

#### Services Not Starting
```bash
# Check service status
docker-compose ps

# Check logs
docker-compose logs sample-app
docker-compose logs grafana
```

#### No Data in Grafana
1. Verify datasource connections
2. Check if sample app is generating data
3. Validate time ranges
4. Review query syntax

#### High Resource Usage
```bash
# Monitor resource usage
docker stats

# Adjust resource limits in docker-compose.yml
services:
  sample-app:
    deploy:
      resources:
        limits:
          memory: 512M
```

### Getting Help
1. Check service logs: `docker-compose logs [service]`
2. Verify network connectivity
3. Review configuration files
4. Consult query catalogs in `/queries/` directory
5. Reference troubleshooting guide in `/docs/troubleshooting.md`