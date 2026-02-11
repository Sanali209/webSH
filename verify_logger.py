import sys
from loguru import logger
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

# Setup OTel
provider = TracerProvider()
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("test.logger")

# Config Patcher (Same as plugin)
def otel_patcher(record):
    span = trace.get_current_span()
    if not span:
        return
        
    span_context = span.get_span_context()
    if span_context.is_valid:
        record["extra"]["trace_id"] = format(span_context.trace_id, "032x")
        record["extra"]["span_id"] = format(span_context.span_id, "016x")

logger.configure(patcher=otel_patcher)
# Add a sink that prints the extra dict
logger.add(sys.stderr, format="{time} | {level} | {message} | {extra}")

if __name__ == "__main__":
    logger.info("Log outside span")
    
    with tracer.start_as_current_span("test-span") as span:
        logger.info("Log inside span")
        span_ctx = span.get_span_context()
        print(f"Expected Trace ID: {format(span_ctx.trace_id, '032x')}")
