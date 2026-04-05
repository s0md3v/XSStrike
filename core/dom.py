import re
from typing import List, Dict, Any, Set
from core.config import ScanContext
from core.log import setup_logger

logger = setup_logger()

class DOMScanner:
    def __init__(self, context: ScanContext):
        self.context = context
        # Sources: Places where user-controlled data enters the script
        self.sources = r'\b(?:document\.(URL|documentURI|URLUnencoded|baseURI|cookie|referrer)|location\.(href|search|hash|pathname)|window\.name|history\.(pushState|replaceState)(local|session)Storage)\b'
        # Sinks: Dangerous functions that can execute code
        self.sinks = r'\b(?:eval|evaluate|execCommand|assign|navigate|getResponseHeaderopen|showModalDialog|Function|set(Timeout|Interval|Immediate)|execScript|crypto.generateCRMFRequest|ScriptElement\.(src|text|textContent|innerText)|.*?\.onEventName|document\.(write|writeln)|.*?\.innerHTML|Range\.createContextualFragment|(document|window)\.location)\b'

    def scan(self, response_text: str) -> List[str]:
        """
        Analyzes the HTML response for potential DOM XSS vulnerabilities by identifying sources and sinks.
        Returns a list of highlighted lines with potential vulnerabilities.
        """
        highlighted = []
        # Extract scripts
        scripts = re.findall(r'(?i)(?s)<script[^>]*>(.*?)</script>', response_text)
        
        sink_found = False
        source_found = False
        
        for script in scripts:
            lines = script.split('\n')
            all_controlled_vars: Set[str] = set()
            
            for i, line in enumerate(lines, 1):
                original_line = line
                # 1. Track variables assigned from sources or other controlled variables
                if 'var ' in line or 'let ' in line or 'const ' in line:
                    for var in all_controlled_vars:
                        if var in line:
                            match = re.search(r'[a-zA-Z$_][a-zA-Z0-9$_]+', line.split('=')[0])
                            if match:
                                all_controlled_vars.add(match.group().replace('$', '\\$'))

                # 2. Identify Sources
                source_matches = list(re.finditer(self.sources, line))
                if source_matches:
                    source_found = True
                    for match in source_matches:
                        # Colorize for console if needed, but here we track
                        source_str = line[match.start():match.end()]
                        # If a variable is assigned from a source, track it
                        var_match = re.search(r'(?:var|let|const)\s+([a-zA-Z$_][a-zA-Z0-9$_]+)\s*=', line)
                        if var_match:
                            all_controlled_vars.add(var_match.group(1).replace('$', '\\$'))
                        line = line.replace(source_str, f"[bold yellow]{source_str}[/bold yellow]")

                # 3. Track controlled variables usage
                for var in all_controlled_vars:
                    if re.search(r'\b%s\b' % var, line):
                        source_found = True
                        line = re.sub(r'\b%s\b' % var, f"[yellow]{var}[/yellow]", line)

                # 4. Identify Sinks
                sink_matches = list(re.finditer(self.sinks, line))
                if sink_matches:
                    for match in sink_matches:
                        sink_str = line[match.start():match.end()]
                        line = line.replace(sink_str, f"[bold red]{sink_str}[/bold red]")
                        # If a controlled variable is passed to a sink, it's a high potential DOM XSS
                        for var in all_controlled_vars:
                            if re.search(r'\b%s\b' % var, original_line):
                                sink_found = True

                if line != original_line:
                    highlighted.append(f"{i}: {line.strip()}")

        if sink_found and source_found:
            logger.vuln("[bold red]Potential DOM XSS detected![/bold red] Source data reaches a dangerous sink.")
        
        return highlighted

# Legacy alias
dom = lambda response: DOMScanner(ScanContext()).scan(response)
