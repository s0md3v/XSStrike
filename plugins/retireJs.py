import re
import json
import hashlib
from typing import List, Dict, Any, Optional, Set
from core.requester import Requester
from core.utils import deJSON, js_extractor, handle_anchor
from core.config import ScanContext
from core.log import setup_logger

logger = setup_logger()

class RetireJsScanner:
    def __init__(self, context: ScanContext):
        self.context = context
        self.requester = Requester(context)
        self.definitions = context.definitions

    def scan_response(self, url: str, response_text: str):
        """Extracts scripts from response and checks them for outdated/vulnerable JS libraries."""
        scripts = js_extractor(response_text)
        for script in scripts:
            if script not in self.context.checkedScripts:
                self.context.checkedScripts.add(script)
                full_uri = handle_anchor(url, script)
                try:
                    js_response = self.requester.request(full_uri).text
                    result = self._main_scanner(full_uri, js_response)
                    if result:
                        self._log_vulnerability(result, full_uri)
                except Exception as e:
                    logger.debug(f"Failed to fetch script {full_uri}: {e}")

    def _main_scanner(self, uri: str, content: str) -> Optional[Dict[str, Any]]:
        if not self.definitions:
            return None
            
        uri_results = self._scan_uri(uri, self.definitions)
        content_results = self._scan_file_content(content, self.definitions)
        
        all_results = uri_results + content_results
        if not all_results:
            return None
            
        # Consolidation logic
        base_result = {
            'component': all_results[0]['component'],
            'version': all_results[0]['version'],
            'vulnerabilities': []
        }
        
        unique_vulns = set()
        for r in all_results:
            for v in r.get('vulnerabilities', []):
                unique_vulns.add(json.dumps(v, sort_keys=True))
                
        for v_str in unique_vulns:
            base_result['vulnerabilities'].append(json.loads(v_str))
            
        return base_result

    def _log_vulnerability(self, result: Dict[str, Any], uri: str):
        logger.red_line()
        logger.good(f"Vulnerable component: [bold red]{result['component']} v{result['version']}[/bold red]")
        logger.info(f"Component location: {uri}")
        vulns = result['vulnerabilities']
        logger.info(f"Total vulnerabilities: {len(vulns)}")
        for v in vulns:
            summary = v.get('identifiers', {}).get('summary', 'No summary')
            severity = v.get('severity', 'Unknown')
            cve = v.get('identifiers', {}).get('CVE', ['N/A'])[0]
            logger.info(f"  - Summary: {summary}")
            logger.info(f"    Severity: {severity} | CVE: {cve}")
        logger.red_line()

    def _scan(self, data: str, extractor: str, definitions: Dict, matcher=None) -> List[Dict]:
        matcher = matcher or self._simple_match
        detected = []
        for component, details in definitions.items():
            extractors = details.get("extractors", {}).get(extractor)
            if not extractors:
                continue
            for i in extractors:
                match = matcher(i, data)
                if match:
                    detected.append({"version": match, "component": component, "detection": extractor})
        return detected

    def _simple_match(self, regex: str, data: str) -> Optional[str]:
        regex = deJSON(regex)
        match = re.search(regex, data)
        return match.group(1) if match else None

    def _scan_uri(self, uri: str, definitions: Dict) -> List[Dict]:
        results = self._scan(uri, 'uri', definitions)
        return self._check(results, definitions)

    def _scan_file_content(self, content: str, definitions: Dict) -> List[Dict]:
        results = self._scan(content, 'filecontent', definitions)
        if not results:
            # Try hash match
            file_hash = hashlib.sha1(content.encode('utf-8')).hexdigest()
            for component, details in definitions.items():
                hashes = details.get("extractors", {}).get("hashes", {})
                if file_hash in hashes:
                    results.append({"version": hashes[file_hash], "component": component, "detection": 'hash'})
        return self._check(results, definitions)

    def _check(self, results: List[Dict], definitions: Dict) -> List[Dict]:
        for r in results:
            component = r['component']
            version = r['version']
            vulns = definitions.get(component, {}).get("vulnerabilities", [])
            for v in vulns:
                below = v.get("below")
                at_or_above = v.get("atOrAbove")
                if not self._is_at_or_above(version, below):
                    if at_or_above and not self._is_at_or_above(version, at_or_above):
                        continue
                    r.setdefault("vulnerabilities", []).append(v)
        return results

    def _is_at_or_above(self, v1: str, v2: str) -> bool:
        if not v1 or not v2: return True
        p1 = [int(x) if x.isdigit() else x for x in re.split(r'[.-]', v1)]
        p2 = [int(x) if x.isdigit() else x for x in re.split(r'[.-]', v2)]
        for a, b in zip(p1, p2):
            if type(a) != type(b): return isinstance(a, int)
            if a > b: return True
            if a < b: return False
        return len(p1) >= len(p2)

# Legacy support
def retireJs(url, response):
    from core.config import ScanContext, globalVariables
    context = ScanContext(definitions=globalVariables.get('definitions', {}))
    scanner = RetireJsScanner(context)
    scanner.scan_response(url, response)
