<h1 align="center">
  <br>
  <a href="https://github.com/s0md3v/XSStrike"><img src="https://image.ibb.co/cpuYoA/xsstrike-logo.png" alt="XSStrike"></a>
  <br>
  XSStrike v3.1.7 (Modernized)
  <br>
</h1>

<h4 align="center">Advanced XSS Detection Suite with Zero False Positives</h4>

XSStrike has been completely refactored to meet modern software engineering standards and advanced offensive security needs. It is no longer just a fuzzer, but a comprehensive XSS detection platform.

## 🚀 Key Features

*   **Zero False Positives**: Integrated with **Playwright (Chromium)** for dynamic validation. Every potential vulnerability is executed in a real browser to confirm if it's exploitable.
*   **Stored XSS Engine**: Advanced crawler that extracts real form fields, injects unique tracking payloads, and re-visits pages to confirm persistence and execution.
*   **DOM XSS Scanner**: Analyzes JavaScript data flow to identify when user-controlled sources reach dangerous execution sinks.
*   **Modern CLI**: Built with **Typer** and **Rich** for a beautiful, intuitive, and highly readable terminal interface.
*   **Pydantic Integration**: All configurations and contexts are strictly typed and validated at runtime.
*   **Authenticated Scans**: Full support for session cookies to scan behind login walls.
*   **DevSecOps Ready**: Exports results in standard **SARIF** format for integration with GitHub Security, GitLab, and CI/CD pipelines.
*   **WAF Detection**: Intelligent detection of over 30 different Web Application Firewalls.

## 🛠 Installation

Using `uv` (recommended):
```bash
# Install dependencies
uv pip install -e ".[dev]"

# Install Playwright browsers
uv run playwright install chromium
```

Using `pip`:
```bash
pip install -r requirements.txt
playwright install chromium
```

## 📖 Usage

### Standard Scan (Reflected + DOM)
```bash
uv run xsstrike.py -u "https://example.com/search?q=query"
```

### Full Crawler (Reflected + Stored + DOM)
```bash
uv run xsstrike.py -u "https://example.com" --crawl --level 3
```

### Authenticated Scan (Using Cookies)
```bash
uv run xsstrike.py -u "https://example.com/admin" --cookies "session=abc; auth=123" --crawl
```

### Fuzzer Mode (Filter Analysis)
```bash
uv run xsstrike.py -u "https://example.com/api" --data "input=test" --fuzzer
```

## 📊 Output Example
After every scan, XSStrike provides a visual summary table:
*   **CONFIRMED**: The browser actually executed the payload (Confirmed vulnerability).
*   **POTENTIAL**: The payload was reflected/stored in HTML but execution was blocked (Filtered or CSP).

## 🐳 Docker
```bash
docker build -t xsstrike .
docker run xsstrike -u "http://example.com"
```

## ⚖️ License
This project is licensed under the GPL-3.0 License.
