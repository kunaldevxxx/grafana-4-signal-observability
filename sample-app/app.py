import os
import time
import random
import logging
import requests
from flask import Flask, request, jsonify
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import pyroscope

# OpenTelemetry imports
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Pyroscope profiling
pyroscope.configure(
    application_name="sample-app",
    server_address="http://pyroscope:4040",
    tags={"version": "1.0.0", "environment": "development"}
)

# Initialize OpenTelemetry
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Configure OTLP exporters
otlp_exporter = OTLPSpanExporter(
    endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://tempo:4317"),
    insecure=True
)

span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Configure metrics
metric_reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://tempo:4317"),
        insecure=True
    ),
    export_interval_millis=5000,
)
metrics.set_meter_provider(MeterProvider(metric_readers=[metric_reader]))
meter = metrics.get_meter(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')
BUSINESS_METRIC = Counter('business_operations_total', 'Business operations', ['operation_type'])

# OpenTelemetry metrics
otel_request_counter = meter.create_counter(
    name="http_requests_total",
    description="Total number of HTTP requests",
    unit="1"
)

otel_request_duration = meter.create_histogram(
    name="http_request_duration",
    description="Duration of HTTP requests",
    unit="s"
)

# Initialize Flask app
app = Flask(__name__)

# Instrument Flask and requests
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()
LoggingInstrumentor().instrument()

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    # Prometheus metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.endpoint or 'unknown',
        status=response.status_code
    ).inc()
    
    if hasattr(request, 'start_time'):
        duration = time.time() - request.start_time
        REQUEST_LATENCY.observe(duration)
        
        # OpenTelemetry metrics
        otel_request_counter.add(1, {
            "method": request.method,
            "endpoint": request.endpoint or 'unknown',
            "status": str(response.status_code)
        })
        
        otel_request_duration.record(duration, {
            "method": request.method,
            "endpoint": request.endpoint or 'unknown'
        })
    
    return response

@app.route('/')
def home():
    logger.info("Home endpoint accessed")
    return jsonify({
        "message": "Welcome to the 4-Signal Observability Demo",
        "endpoints": {
            "/": "This endpoint",
            "/slow": "Simulates slow operation",
            "/error": "Simulates error scenarios",
            "/external": "Makes external API call",
            "/metrics": "Prometheus metrics",
            "/health": "Health check"
        }
    })

@app.route('/slow')
def slow_operation():
    """Simulate a slow operation for demonstrating traces and metrics"""
    with tracer.start_as_current_span("slow_operation") as span:
        # Add some attributes to the span
        span.set_attribute("operation.type", "slow")
        span.set_attribute("operation.complexity", "high")
        
        logger.info("Starting slow operation")
        
        # Simulate some processing time
        sleep_time = random.uniform(1, 3)
        span.set_attribute("sleep.duration", sleep_time)
        time.sleep(sleep_time)
        
        # Simulate some CPU-intensive work
        with tracer.start_as_current_span("cpu_intensive_work"):
            result = 0
            for i in range(100000):
                result += i * random.random()
        
        BUSINESS_METRIC.labels(operation_type="slow_operation").inc()
        logger.info(f"Slow operation completed in {sleep_time:.2f} seconds")
        
        return jsonify({
            "message": "Slow operation completed",
            "duration": sleep_time,
            "result": result
        })

@app.route('/error')
def error_scenario():
    """Simulate different error scenarios"""
    error_type = request.args.get('type', 'random')
    
    with tracer.start_as_current_span("error_operation") as span:
        span.set_attribute("error.type", error_type)
        
        if error_type == 'random':
            error_type = random.choice(['500', '404', 'timeout', 'success'])
        
        logger.warning(f"Simulating error type: {error_type}")
        
        if error_type == '500':
            span.set_attribute("error", True)
            span.set_attribute("error.message", "Internal server error simulation")
            logger.error("Simulated 500 error")
            return jsonify({"error": "Internal server error"}), 500
        elif error_type == '404':
            span.set_attribute("error", True)
            span.set_attribute("error.message", "Resource not found simulation")
            logger.error("Simulated 404 error")
            return jsonify({"error": "Resource not found"}), 404
        elif error_type == 'timeout':
            span.set_attribute("operation.timeout", True)
            logger.warning("Simulating timeout")
            time.sleep(10)  # This will likely timeout
            return jsonify({"message": "This shouldn't be reached"})
        else:
            BUSINESS_METRIC.labels(operation_type="error_handled").inc()
            logger.info("Error scenario handled successfully")
            return jsonify({"message": "No error occurred"})

@app.route('/external')
def external_call():
    """Make an external API call to demonstrate distributed tracing"""
    with tracer.start_as_current_span("external_api_call") as span:
        span.set_attribute("external.service", "httpbin.org")
        
        try:
            logger.info("Making external API call")
            response = requests.get("https://httpbin.org/delay/1", timeout=5)
            span.set_attribute("http.status_code", response.status_code)
            span.set_attribute("external.success", True)
            
            BUSINESS_METRIC.labels(operation_type="external_call_success").inc()
            logger.info("External API call successful")
            
            return jsonify({
                "message": "External call successful",
                "status_code": response.status_code,
                "data": response.json()
            })
        except requests.exceptions.RequestException as e:
            span.set_attribute("error", True)
            span.set_attribute("error.message", str(e))
            BUSINESS_METRIC.labels(operation_type="external_call_failure").inc()
            logger.error(f"External API call failed: {e}")
            
            return jsonify({
                "error": "External call failed",
                "details": str(e)
            }), 500

@app.route('/metrics')
def metrics():
    """Expose Prometheus metrics"""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/health')
def health():
    """Health check endpoint"""
    logger.info("Health check requested")
    return jsonify({
        "status": "healthy",
        "timestamp": time.time(),
        "service": "sample-app",
        "version": "1.0.0"
    })

@app.route('/generate-load')
def generate_load():
    """Generate some load for testing purposes"""
    with tracer.start_as_current_span("load_generation") as span:
        operations = random.randint(10, 50)
        span.set_attribute("load.operations", operations)
        
        logger.info(f"Generating load with {operations} operations")
        
        results = []
        for i in range(operations):
            with tracer.start_as_current_span(f"operation_{i}"):
                # Simulate various operations
                operation_type = random.choice(['fast', 'medium', 'slow'])
                
                if operation_type == 'fast':
                    time.sleep(random.uniform(0.01, 0.1))
                elif operation_type == 'medium':
                    time.sleep(random.uniform(0.1, 0.5))
                else:
                    time.sleep(random.uniform(0.5, 1.0))
                
                results.append({
                    "operation": i,
                    "type": operation_type
                })
                
                BUSINESS_METRIC.labels(operation_type=f"load_{operation_type}").inc()
        
        logger.info(f"Load generation completed: {operations} operations")
        return jsonify({
            "message": "Load generation completed",
            "operations": operations,
            "results": results
        })

if __name__ == '__main__':
    logger.info("Starting sample application with 4-signal observability")
    app.run(host='0.0.0.0', port=8080, debug=False)