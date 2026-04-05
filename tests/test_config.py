import pytest
from core.config import XSSConfig, ScanContext

def test_config_defaults():
    config = XSSConfig()
    assert config.delay == 0
    assert config.threadCount == 10
    assert config.timeout == 10
    assert "http" in config.proxies

def test_scan_context_initialization():
    config = XSSConfig(delay=2, timeout=20)
    context = ScanContext(config=config, target="http://example.com")
    assert context.target == "http://example.com"
    assert context.config.delay == 2
    assert context.config.timeout == 20
    assert isinstance(context.headers, dict)
    assert isinstance(context.checkedScripts, set)

def test_scan_context_pydantic_validation():
    with pytest.raises(ValueError):
        # Invalid delay type
        XSSConfig(delay="invalid")
