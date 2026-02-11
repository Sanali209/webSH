import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from core.settings import settings
from loguru import logger

def setup_tracing():
    resource = Resource(attributes={
        "service.name": settings.APP_NAME,
        "service.version": settings.APP_VERSION,
    })

    provider = TracerProvider(resource=resource)
    
    # Configure OTLP Exporter
    # Note: OTLPSpanExporter defaults to localhost:4317 (gRPC) or checks OTEL_EXPORTER_OTLP_ENDPOINT
    # We explicitly pass the endpoint if needed, but the library handles env vars well.
    # However, settings.OTEL_EXPORTER_OTLP_ENDPOINT might be http/protobuf
    processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT))
    provider.add_span_processor(processor)

    # Real-time Broadcast Processor
    from opentelemetry.sdk.trace import SpanProcessor
    from core.debug import broadcaster
    import asyncio
    import time
    
    class BroadcasterSpanProcessor(SpanProcessor):
        def on_end(self, span):
            # Convert span to dict for UI
            span_data = {
                "trace_id": format(span.get_span_context().trace_id, "032x"),
                "span_id": format(span.get_span_context().span_id, "016x"),
                "name": span.name,
                "start_time": span.start_time,
                "end_time": span.end_time,
                "parent_id": format(span.parent.span_id, "016x") if span.parent else None,
                "status": span.status.status_code.name,
                "attributes": dict(span.attributes) if span.attributes else {}
            }
            
            # Fire and forget update
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(broadcaster.broadcast({
                    "type": "span",
                    "data": span_data
                }))
            except RuntimeError:
                pass

    provider.add_span_processor(BroadcasterSpanProcessor())

    # Sets the global default tracer provider
    trace.set_tracer_provider(provider)
    
    logger.info(f"Tracing initialized. Exporting to {settings.OTEL_EXPORTER_OTLP_ENDPOINT}")
    return provider
