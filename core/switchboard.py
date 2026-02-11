from typing import Any, Dict, Optional
from loguru import logger
from pydantic import TypeAdapter, ValidationError
from core.schemas import CapabilityEnvelope
from core.registry import registry

class Switchboard:
    def __init__(self, max_trace_depth: int = 10):
        self.max_trace_depth = max_trace_depth
        # Cache for TypeAdapters to improve performance
        self._adapter_cache: Dict[str, TypeAdapter] = {}

    def _get_adapter(self, domain_query: str) -> Optional[TypeAdapter]:
        if domain_query in self._adapter_cache:
            return self._adapter_cache[domain_query]
        
        schema = registry.get_schema(domain_query)
        if schema:
            adapter = TypeAdapter(schema)
            self._adapter_cache[domain_query] = adapter
            return adapter
        return None

    async def dispatch(self, envelope: CapabilityEnvelope) -> Any:
        # 1. Audit & Trace check
        if len(envelope.context.trace_stack) >= self.max_trace_depth:
            logger.error(f"Circular dependency or too deep trace stack: {envelope.correlation_id}")
            raise RuntimeError("Max trace depth exceeded")

        # 2. Add current node to trace stack
        envelope.context.trace_stack.append("kernel.switchboard")

        # 3. Resolve provider
        handler = registry.resolve(envelope.domain)
        if not handler:
            logger.warning(f"No provider found for domain: {envelope.domain}")
            return {"error": f"Capability not found: {envelope.domain}", "correlation_id": envelope.correlation_id}

        # 4. Schema Guard (High-speed validation)
        params = envelope.params
        adapter = self._get_adapter(envelope.domain)
        if adapter:
            try:
                # High-speed validation of params against the schema
                params = adapter.validate_python(envelope.params)
            except ValidationError as ve:
                logger.warning(f"Schema validation failed for {envelope.domain}: {ve.json()}")
                return {
                    "status": "error",
                    "type": "schema_validation_error",
                    "details": ve.errors(),
                    "correlation_id": envelope.correlation_id
                }

        # 5. Execute
        try:
            logger.info(f"Dispatching {envelope.domain} [CID: {envelope.correlation_id}]")
            # Handlers are assumed to be async in this architecture
            result = await handler(params, envelope.context)
            return {
                "status": "success",
                "data": result,
                "correlation_id": envelope.correlation_id
            }
        except Exception as e:
            logger.exception(f"Error executing capability {envelope.domain}: {e}")
            return {
                "status": "error",
                "message": str(e),
                "correlation_id": envelope.correlation_id
            }

switchboard = Switchboard()
