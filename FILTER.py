def parse_cuckoo_json(input_path):
    import json

    # Load raw JSON data
    with open(input_path, 'r') as file:
        data = json.load(file)

    # Filter relevant sections
    filtered_data = {
        "info": {
            "score": data["info"].get("score"),
            "duration": data["info"].get("duration"),
            "started": data["info"].get("started"),
            "ended": data["info"].get("ended")
        },
        "signatures": [
            {
                "name": sig.get("name"),
                "description": sig.get("description"),
                "severity": sig.get("severity"),
                "marks": sig.get("marks", [])
            }
            for sig in data.get("signatures", [])
            if sig.get("severity") >= 2  # Filter signatures with higher severity
        ],
        "target": {
            "file_name": data["target"]["file"].get("name"),
            "file_type": data["target"]["file"].get("type"),
            "sha256": data["target"]["file"].get("sha256"),
            "size": data["target"]["file"].get("size")
        },
        "network": {
            "udp": data["network"].get("udp", []),
            "http": data["network"].get("http", []),
            "dns": data["network"].get("dns", []),
            "icmp": data["network"].get("icmp", [])
        },
        "behavior": {
            "generic": [
                {
                    "process_name": proc.get("process_name"),
                    "pid": proc.get("pid"),
                    "summary": proc.get("summary")
                }
                for proc in data["behavior"].get("generic", [])
            ],
            "apistats": data["behavior"].get("apistats", {})
        }
    }

    # Remove empty fields to clean the JSON
    filtered_data = {key: value for key, value in filtered_data.items() if value}

    return filtered_data
