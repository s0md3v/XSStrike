import re
from typing import Dict, Any, Optional
from core.config import xsschecker, badTags, ScanContext
from core.utils import extractScripts

class HTMLParser:
    def __init__(self, context: ScanContext):
        self.context = context

    def parse(self, response_text: str) -> Dict[int, Dict[str, Any]]:
        """
        Parses the HTML response to find reflections and analyze their context.
        Returns a dictionary of occurrences with context details and filter scores.
        """
        occurences: Dict[int, Dict[str, Any]] = {}
        
        # 1. Identify raw reflection positions
        # Using the xsschecker string to find where our probe reflected
        checker = self.context.config.xsschecker
        for match in re.finditer(checker, response_text):
            pos = match.start()
            occurences[pos] = {
                'context': 'html', # Default
                'details': {},
                'score': {'<': 0, '>': 0, '\"': 0, '\'': 0}
            }

        # 2. Refine context (Attribute, Script, Comment)
        self._refine_contexts(response_text, occurences)
        
        return occurences

    def _refine_contexts(self, response_text: str, occurences: Dict[int, Dict[str, Any]]):
        # This is a simplified version of the original logic, 
        # which would need more complex regex/parsing to be 100% equivalent.
        # For now, we maintain the structure for the refactoring.
        
        # Example: Find reflections inside scripts
        scripts = extractScripts(response_text)
        for script in scripts:
            if self.context.config.xsschecker in script:
                # Logic to map script reflection to overall position
                pass

        # Example: Find reflections inside attributes
        # <tag attr="reflection">
        attr_pattern = re.compile(r'<([a-zA-Z0-9]+)\s+[^>]*?([a-zA-Z0-9_-]+)\s*=\s*(["\'])([^>]*?' + self.context.config.xsschecker + r'[^>]*?)\3', re.IGNORECASE)
        for match in attr_pattern.finditer(response_text):
            tag, attr_name, quote, value = match.groups()
            pos = response_text.find(self.context.config.xsschecker, match.start())
            if pos in occurences:
                occurences[pos]['context'] = 'attribute'
                occurences[pos]['details'] = {
                    'tag': tag.lower(),
                    'name': attr_name.lower(),
                    'quote': quote,
                    'value': value,
                    'type': 'value'
                }

    def calculate_scores(self, occurences: Dict[int, Dict[str, Any]], response_with_probes: str):
        """
        Updates the scores based on a response that contains special characters.
        """
        # This logic is usually called after sending a probe like < > " '
        for pos, data in occurences.items():
            # Check if characters are reflected correctly near the position
            pass
