from typing import Type, Dict, Any, Optional
from pydantic import BaseModel, SecretStr
from pydantic.fields import FieldInfo
import inspect

def settings_to_json_schema(model: Optional[Type[BaseModel]]) -> Dict[str, Any]:
    """
    Generates a JSON schema for a Pydantic model, optimized for UI form generation.
    Removes redundant titles and injects ui:widget hints.
    """
    if not model:
        return {}

    schema = model.model_json_schema()

    # Process properties to add ui:widget hint
    properties = schema.get("properties", {})

    for field_name, field_info in model.model_fields.items():
        if field_name not in properties:
            continue

        prop_schema = properties[field_name]

        # Check for SecretStr
        # Note: field_info.annotation might be complex (e.g. Optional[SecretStr])
        # A simple check is to look at the type or use pydantic's metadata
        is_secret = False
        if field_info.annotation == SecretStr:
            is_secret = True
        elif hasattr(field_info.annotation, "__origin__") and field_info.annotation.__origin__ is SecretStr: # type: ignore
             is_secret = True
        # Handle Optional[SecretStr]
        elif hasattr(field_info.annotation, "__args__"):
             for arg in field_info.annotation.__args__: # type: ignore
                 if arg == SecretStr:
                     is_secret = True
                     break

        if is_secret:
             prop_schema["ui:widget"] = "password"
             prop_schema["format"] = "password"

        # Check for extra JSON schema info passed via Field(json_schema_extra={...})
        if field_info.json_schema_extra:
             extra = field_info.json_schema_extra
             if isinstance(extra, dict):
                 for key, value in extra.items():
                     if key.startswith("ui:"):
                         prop_schema[key] = value

        # Clean up title if it matches the field name (auto-generated)
        # Pydantic generates titles like "Api Key" for "api_key"
        generated_title = field_name.replace("_", " ").title()
        if prop_schema.get("title") == generated_title:
            del prop_schema["title"]

    # Remove top-level title if it matches the model name (often generic)
    if "title" in schema:
        # We might want to keep it if it's meaningful, but often it's "Settings" or "Config"
        # The task suggests removing it if it interferes.
        # Let's remove it to keep the schema clean for the UI which might use its own header.
        del schema["title"]

    return schema
