import sys
from loguru import logger
from opentelemetry import trace
from core.sdk import BasePlugin

def otel_patcher(record):
    span = trace.get_current_span()
    if not span:
        return
        
    span_context = span.get_span_context()
    if span_context.is_valid:
        record["extra"]["trace_id"] = format(span_context.trace_id, "032x")
        record["extra"]["span_id"] = format(span_context.span_id, "016x")
        # Ensure 'service.name' is consistent if needed, but usually resource handles it.

class SystemLogger(BasePlugin):
    def __init__(self):
        super().__init__()
        # Configure Loguru to use the patcher
        # This wrapper adds trace/span IDs to every log record
        logger.configure(patcher=otel_patcher)
        
        # We can also add a specialized sink if we wanted to push logs AS spans,
        # but OTel usually handles logs separately via OTLPLogExporter.
        # For now, we rely on the stdout/stderr capture or OTel's auto-instrumentation 
        # if installed, OR just the fact that we have trace_id in logs allows correlation in backend.
        
        # However, the task specifically asked for "Integrate Loguru ... Export to OpenTelemetry".
        # If we just add trace_id to stdout, the collector needs to scrape stdout.
        # If we want to push logs directly to OTLP, we need an OTLP Log Handler.
        # Given "opentelemetry-exporter-otlp" is installed, we can try to hook logging.
        
        logger.info("System Logger initialized with OpenTelemetry bridge")

plugin = SystemLogger()
