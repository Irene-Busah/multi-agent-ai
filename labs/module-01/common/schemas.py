"""Structured outputs for the reflection chain (section 3) and the forks (section 5)."""

def _schema(name, properties, required=None):
    return {"format": {"type": "json_schema", "name": name, "strict": True,
                       "schema": {"type": "object", "additionalProperties": False,
                                  "properties": properties, "required": required or list(properties)}}}


STEPS = _schema("assessment_plan", {
    "steps": {"type": "array", "items": {"type": "string"}, "description": "Ordered assessment steps"},
})

TRACE = _schema("reserve_trace", {
    "recommendation": {"type": "string", "description": "Coverage position and recommended action"},
    "reserve_eur": {"type": "number", "description": "Recommended reserve in EUR, property plus business interruption, after deductibles"},
    "reasoning_steps": {"type": "array", "items": {"type": "string"}},
    "confidence": {"type": "integer", "description": "1 to 10"},
    "revision_notes": {"type": "string", "description": "What changed since the previous draft, or 'initial draft'"},
})
