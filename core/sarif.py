import json
from datetime import datetime
from typing import List, Dict, Any

class SarifExporter:
    def __init__(self, tool_name: str = "XSStrike", version: str = "3.1.7"):
        self.tool_name = tool_name
        self.version = version
        self.results: List[Dict[str, Any]] = []

    def add_finding(self, url: str, parameter: str, payload: str, description: str = "XSS Vulnerability found"):
        """Adds a finding to the SARIF report."""
        result = {
            "ruleId": "XSS-001",
            "message": {
                "text": f"{description} in parameter '{parameter}' at {url}"
            },
            "locations": [
                {
                    "physicalLocation": {
                        "address": {
                            "fullyQualifiedName": url
                        }
                    }
                }
            ],
            "properties": {
                "parameter": parameter,
                "payload": payload
            }
        }
        self.results.append(result)

    def generate_sarif(self) -> str:
        """Generates the final SARIF JSON string."""
        sarif_log = {
            "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
            "version": "2.1.0",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": self.tool_name,
                            "version": self.version,
                            "rules": [
                                {
                                    "id": "XSS-001",
                                    "name": "Cross-Site Scripting",
                                    "shortDescription": {
                                        "text": "Potential Cross-Site Scripting (XSS) vulnerability detected."
                                    }
                                }
                            ]
                        }
                    },
                    "results": self.results
                }
            ]
        }
        return json.dumps(sarif_log, indent=2)

    def save_to_file(self, filename: str):
        with open(filename, "w") as f:
            f.write(self.generate_sarif())
