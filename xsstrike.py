#!/usr/bin/env python3

import sys
import signal
import json
import typer
from typing import Optional
from rich.console import Console
from rich.panel import Panel

# Local imports
from core.config import XSSConfig, ScanContext, default_headers, default_payloads
from core.utils import extractHeaders, extract_cookies, reader, find_db_file
import core.log
console = Console()
app = typer.Typer(help="XSStrike Advanced XSS Scanner (Modernized)")

def show_banner():
    banner_text = """
    XSStrike v3.1.7 (Modernized)
    Advanced XSS Detection Suite
    """
    console.print(Panel(banner_text, style="bold red", subtitle="Refactored with Pydantic & Typer"))

@app.command()
def main(
    url: Optional[str] = typer.Option(None, "-u", "--url", help="Target URL"),
    data: Optional[str] = typer.Option(None, "--data", help="POST data"),
    fuzzer: bool = typer.Option(False, "--fuzzer", help="Fuzzer mode"),
    update: bool = typer.Option(False, "--update", help="Update XSStrike"),
    timeout: int = typer.Option(10, "--timeout", help="Timeout in seconds"),
    threads: int = typer.Option(10, "-t", "--threads", help="Number of threads"),
    delay: int = typer.Option(0, "-d", "--delay", help="Delay between requests"),
    crawl: bool = typer.Option(False, "--crawl", help="Crawl mode"),
    level: int = typer.Option(2, "-l", "--level", help="Crawl depth"),
    headers: Optional[str] = typer.Option(None, "--headers", help="Custom headers"),
    cookies: Optional[str] = typer.Option(None, "--cookies", help="Custom session cookies"),
    seeds: Optional[str] = typer.Option(None, "--seeds", help="Seeds file"),
    payload_file: Optional[str] = typer.Option(None, "-f", "--file", help="Custom payloads file"),
    skip_dom: bool = typer.Option(False, "--skip-dom", help="Skip DOM checking"),
    blind: bool = typer.Option(False, "--blind", help="Blind XSS mode"),
    json_data: bool = typer.Option(False, "--json", help="POST data is JSON"),
    path: bool = typer.Option(False, "--path", help="Inject in path"),
    console_log_level: str = typer.Option("INFO", "--console-log-level"),
):
    show_banner()
    
    # Initialize Configuration
    config = XSSConfig(
        delay=delay,
        threadCount=threads,
        timeout=timeout
    )
    
    if cookies:
        config.cookies = extract_cookies(cookies)
    
    # Initialize Scan Context
    context = ScanContext(config=config)
    context.target = url
    context.headers = default_headers.copy()
    
    if headers:
        context.headers.update(extractHeaders(headers))
        
    # Load definitions
    definitions_file = find_db_file('definitions.json')
    if definitions_file:
        with open(definitions_file, 'r') as f:
            context.definitions = json.load(f)

    # Payload Logic
    context.payloads = default_payloads
    if payload_file:
        context.payloads = list(filter(None, reader(payload_file)))

    if not url and not seeds:
        console.print("[yellow]No target specified.[/yellow] Use --help for usage.")
        raise typer.Exit(code=1)

    # Log setup
    core.log.console_log_level = console_log_level
    logger = core.log.setup_logger()
    
    # 1. WAF Detection
    from core.wafDetector import WAFDetector
    waf_detector = WAFDetector(context)
    waf_name = waf_detector.detect()
    
    # 2. Main Execution Flow
    if fuzzer:
        from modes.fuzzer import XSSFuzzer
        fuzzer_engine = XSSFuzzer(context)
        fuzzer_engine.fuzz()
        
    elif crawl:
        from modes.crawl import XSScrawler
        crawler_engine = XSScrawler(context)
        crawler_engine.run(level=level)
        
    else:
        # Standard Scan using the modernized Scanner class
        from modes.scan import Scanner
        scanner = Scanner(context)
        scanner.scan(skip_dom=skip_dom, skip_confirm=False)

    # --- FINAL SUMMARY ---
    if context.findings:
        from rich.table import Table
        table = Table(title="XSStrike Scan Summary", show_header=True, header_style="bold magenta")
        table.add_column("Type", style="dim")
        table.add_column("Target URL", no_wrap=False)
        table.add_column("Payload", style="cyan")
        table.add_column("Status", justify="center")

        for f in context.findings:
            status = "[bold green]CONFIRMED[/bold green]" if f.confirmed else "[yellow]POTENTIAL[/yellow]"
            table.add_row(f.type, f.url, f.payload, status)
        
        console.print("\n")
        console.print(table)
        console.print(f"\n[bold green]Scan finished. Total vulnerabilities confirmed: {len([f for f in context.findings if f.confirmed])}[/bold green]")
    else:
        console.print("\n[bold yellow]Scan finished. No vulnerabilities found.[/bold yellow]")

def handle_sigint(sig, frame):
    console.print("\n[bold yellow]Aborted by user.[/bold yellow]")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_sigint)
    app()
