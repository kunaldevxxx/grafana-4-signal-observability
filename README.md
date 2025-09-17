# Grafana 4-Signal Observability

A comprehensive, production-ready reference implementation demonstrating the four pillars of observability: **Metrics**, **Logs**, **Traces**, and **Profiles** using Grafana ecosystem tools.

## 🎯 Repository Objectives

This repository provides a reproducible reference for:

✅ **Infrastructure Provisioning**: Docker Compose setup for complete observability stack  
✅ **Instrumented Sample App**: Python Flask application with full OpenTelemetry instrumentation  
✅ **Grafana Provisioning**: Pre-configured datasources and comprehensive dashboards  
✅ **Recording & Alerting Rules**: Production-ready Prometheus rules  
✅ **Query Catalogs**: Extensive examples for metrics, logs, traces, and profiles  
✅ **Troubleshooting & Optimization**: Complete guides for production operations  

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- 4GB+ available RAM
- Ports 3000, 8080, 9090, 3100, 3200, 4040 available

### Start the Stack
```bash
git clone https://github.com/kunaldevxxx/grafana-4-signal-observability.git
cd grafana-4-signal-observability
docker-compose up -d
```

### Access Services
| Service | URL | Credentials |
|---------|-----|-------------|
| **Grafana** | http://localhost:3000 | admin/admin |
| **Sample App** | http://localhost:8080 | - |
| **Prometheus** | http://localhost:9090 | - |
| **Pyroscope** | http://localhost:4040 | - |

### Generate Test Data
```bash
# Generate application load
curl http://localhost:8080/generate-load

# Test slow operations  
curl http://localhost:8080/slow

# Test error scenarios
curl "http://localhost:8080/error?type=500"

# External API calls
curl http://localhost:8080/external
```

## 📊 The Four Signals

### 1. Metrics (Prometheus)
- **Golden Signals**: Request rate, error rate, latency, saturation
- **Business Metrics**: Custom operations tracking
- **Infrastructure Metrics**: Resource utilization
- **Recording Rules**: Pre-computed aggregations for performance

### 2. Logs (Loki + Promtail)
- **Structured Logging**: JSON-formatted application logs
- **Container Logs**: Automatic collection via Promtail
- **Log Correlation**: Trace ID injection for correlation
- **Log Metrics**: Derived metrics from log patterns

### 3. Traces (Tempo)
- **Distributed Tracing**: Full request lifecycle tracking
- **Service Maps**: Automatic service dependency discovery
- **Span Correlation**: Linked to logs and metrics
- **Performance Analysis**: Latency breakdown and bottleneck identification

### 4. Profiles (Pyroscope)
- **Continuous Profiling**: Always-on performance monitoring
- **CPU Profiling**: Function-level performance analysis
- **Memory Profiling**: Allocation tracking and leak detection
- **Flame Graphs**: Visual performance analysis

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Sample App    │    │    Grafana      │    │   Prometheus    │
│   (Flask +      │────│   (Dashboards   │────│   (Metrics      │
│    OpenTelemetry│    │    + Alerts)    │    │    + Rules)     │
│    + Pyroscope) │    └─────────────────┘    └─────────────────┘
└─────────────────┘              │                       │
         │                       │                       │
         │              ┌─────────────────┐    ┌─────────────────┐
         │              │      Loki       │    │     Tempo       │
         └──────────────│    (Logs +      │    │   (Traces +     │
                        │    Queries)     │    │   TraceQL)      │
                        └─────────────────┘    └─────────────────┘
                                 │                       │
                        ┌─────────────────┐    ┌─────────────────┐
                        │    Promtail     │    │   Pyroscope     │
                        │ (Log Collection)│    │ (Profiles +     │
                        │                 │    │  Flame Graphs)  │
                        └─────────────────┘    └─────────────────┘
```

## 📚 Documentation

### Setup and Usage
- **[Setup Guide](docs/setup.md)**: Comprehensive setup and configuration
- **[Troubleshooting Guide](docs/troubleshooting.md)**: Production troubleshooting procedures

### Query Catalogs
- **[Metrics Queries](queries/metrics.md)**: PromQL examples for monitoring
- **[Logs Queries](queries/logs.md)**: LogQL examples for log analysis  
- **[Traces Queries](queries/traces.md)**: TraceQL examples for distributed tracing
- **[Profiles Queries](queries/profiles.md)**: Profiling queries and analysis techniques

## 🔧 Sample Application Features

The included Flask application demonstrates comprehensive observability instrumentation:

### Instrumentation
- **OpenTelemetry**: Automatic and manual tracing
- **Prometheus**: Custom metrics with proper labels
- **Structured Logging**: JSON logs with correlation IDs
- **Pyroscope**: Continuous profiling integration

### Endpoints
```bash
GET  /                 # Home page with API documentation
GET  /slow             # Simulates slow operations (1-3s)
GET  /error?type=500   # Error scenarios (500, 404, timeout)
GET  /external         # External API calls for distributed tracing
GET  /generate-load    # Load generation for testing
GET  /health           # Health check endpoint
GET  /metrics          # Prometheus metrics endpoint
```

### Key Features
- **Automatic Instrumentation**: HTTP requests, external calls
- **Custom Spans**: Business logic tracing
- **Error Handling**: Proper error status and attributes
- **Performance Simulation**: Configurable delays and load
- **Resource Monitoring**: CPU, memory, and custom metrics

## 📈 Pre-built Dashboards

### 4-Signal Observability Dashboard
- **Metrics Overview**: Golden signals and business metrics
- **Real-time Traces**: Interactive trace search and analysis
- **Log Analysis**: Structured log search with correlation
- **Profile Visualization**: Flame graphs and performance analysis
- **Alert Integration**: Visual alert status and history

### Dashboard Features
- **Cross-signal Correlation**: Jump between metrics, logs, traces, and profiles
- **Time Synchronization**: Consistent time ranges across all panels
- **Drill-down Capabilities**: From high-level metrics to detailed traces
- **Custom Variables**: Dynamic filtering and grouping

## 🚨 Alerting and Rules

### Prometheus Recording Rules
```yaml
# High-performance pre-computed metrics
- record: sample_app:http_requests:rate5m
- record: sample_app:http_request_duration:p95_5m  
- record: sample_app:error_rate:5m
```

### Alert Rules
```yaml
# Production-ready alerts
- alert: HighErrorRate        # Error rate > 10%
- alert: HighLatency         # P95 latency > 1s
- alert: ServiceDown         # Service unavailable
```

## 🔍 Query Examples

### Metrics (PromQL)
```promql
# Request rate
sum(rate(http_requests_total[5m]))

# Error rate
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) * 100

# P95 latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

### Logs (LogQL)
```logql
# Application errors
{container_name=~".*sample-app.*"} |= "ERROR"

# Slow operations
{container_name=~".*sample-app.*"} |= "slow operation"

# Request rate from logs
rate({container_name=~".*sample-app.*"} |= "INFO" [5m])
```

### Traces (TraceQL)
```traceql
# Slow traces
{duration > 1s && service.name="sample-app"}

# Error traces
{status=error && service.name="sample-app"}

# External service calls
{service.name="sample-app"} >> {service.name!="sample-app"}
```

### Profiles
```
# CPU hotspots
sample-app{} | top(10)

# Memory allocation patterns  
sample-app:alloc_space:bytes:space:bytes{} | rate()

# Performance comparison
sample-app{} | diff(baseline_profile)
```

## 🛠️ Production Considerations

### Security
- Change default passwords
- Configure authentication (LDAP, OAuth)
- Enable TLS/SSL
- Network security and firewall rules

### Performance
- Adjust retention policies based on requirements
- Configure appropriate scrape intervals
- Optimize query performance with recording rules
- Monitor resource usage and capacity

### High Availability
- Multi-instance deployments
- Persistent storage configuration
- Backup and disaster recovery
- Load balancing setup

### Scaling
- Horizontal scaling patterns
- Data sharding strategies
- Resource planning and monitoring
- Cost optimization techniques

## 📁 Repository Structure

```
├── docker-compose.yml           # Complete stack definition
├── sample-app/                  # Instrumented Flask application
│   ├── app.py                   # Main application with 4-signal instrumentation
│   ├── Dockerfile               # Container configuration
│   └── requirements.txt         # Python dependencies
├── prometheus/                  # Metrics collection and rules
│   ├── prometheus.yml           # Prometheus configuration
│   └── rules/                   # Recording and alerting rules
├── loki/                        # Log aggregation
│   └── loki-config.yaml         # Loki configuration
├── promtail/                    # Log collection
│   └── promtail-config.yaml     # Promtail configuration  
├── tempo/                       # Distributed tracing
│   └── tempo.yaml               # Tempo configuration
├── grafana/                     # Visualization and dashboards
│   ├── provisioning/            # Automated setup
│   │   ├── datasources/         # Pre-configured data sources
│   │   └── dashboards/          # Dashboard provisioning
│   └── dashboards/              # Dashboard definitions
├── queries/                     # Query catalogs and examples
│   ├── metrics.md               # PromQL query examples
│   ├── logs.md                  # LogQL query examples
│   ├── traces.md                # TraceQL query examples
│   └── profiles.md              # Profiling query examples
├── docs/                        # Documentation
│   ├── setup.md                 # Setup and configuration guide
│   └── troubleshooting.md       # Troubleshooting procedures
└── README.md                    # This file
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Areas for Contribution
- Additional instrumentation examples
- More complex sample applications
- Kubernetes manifests
- Additional dashboard examples
- Performance optimizations
- Documentation improvements

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Grafana Labs for the excellent observability tools
- OpenTelemetry community for standardized instrumentation
- Prometheus community for robust metrics collection
- The broader observability community for best practices and patterns

---

**🎯 Ready to dive into comprehensive observability?**

1. `docker-compose up -d`
2. Visit http://localhost:3000
3. Explore the 4-Signal Observability Dashboard
4. Generate some load and watch the magic happen!

For detailed setup instructions, see [docs/setup.md](docs/setup.md)