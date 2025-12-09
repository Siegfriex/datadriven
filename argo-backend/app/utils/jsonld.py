from typing import Any, Dict, List

def to_jsonld(
    data: Any, 
    context: str = "https://schema.org/", 
    type_name: str | None = None,
    id_uri: str | None = None
) -> Dict[str, Any]:
    """
    Wraps a dictionary or model dump in JSON-LD structure.
    Auto-injects 'argo:' namespace for custom fields.
    """
    if isinstance(data, list):
        return {
            "@context": context,
            "@type": "Collection",
            "member": [to_jsonld(item, context) for item in data]
        }
    
    result = data.copy() if isinstance(data, dict) else data.model_dump(by_alias=True)
    
    # JSON-LD Standard Fields
    if "@context" not in result:
        result["@context"] = context
    if type_name and "@type" not in result:
        result["@type"] = type_name
    if id_uri and "@id" not in result:
        result["@id"] = id_uri

    # Fields to exclude from auto-namespacing
    EXCLUDED_FIELDS = {
        # Schema.org Standard
        "@context", "@type", "@id", "identifier", "name", "alternateName", 
        "birthDate", "url", "description",
        # Frontend Compatibility / Legacy / Relations
        "birth_year", "artist_id",
        "collaborations", "institutions", "exhibitions", "collaborators",
        "artworks", # Future
        # Coordinates (Frontend interface match)
        "x", "y", "z", "radius", "computed_at", "algorithm",
        # Explicit Scores/Analysis (handled as objects)
        "scores", "coordinates_3d", "structuralist_analysis"
    }

    argo_fields = {}
    for key, value in list(result.items()):
        if key in EXCLUDED_FIELDS or key.startswith("argo:") or key.startswith("@"):
            continue
            
        # Move custom field to argo: namespace
        argo_fields[f"argo:{key}"] = value
        del result[key]
    
    result.update(argo_fields)
        
    return result
