CATS_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "color": {
            "type": "string",
            "enum": [
                "black",
                "white",
                "black & white",
                "red",
                "red & white",
                "red & black & white",
            ],
        },
        "tail_length": {
            "type": "integer",
            "minimum": 0,
        },
        "whiskers_length": {
            "type": "integer",
            "minimum": 0,
        },
    },
    "required": ["name", "color", "tail_length", "whiskers_length"],
}
