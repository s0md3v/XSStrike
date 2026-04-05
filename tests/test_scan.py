import pytest
from unittest.mock import MagicMock, patch
from modes.scan import Scanner
from core.config import ScanContext, XSSConfig

@pytest.fixture
def vulnerable_context():
    config = XSSConfig(xsschecker="v3dm0s", delay=0, timeout=1)
    context = ScanContext(
        config=config,
        target="http://vulnerable.com/search",
        paramData={"q": "v3dm0s"},
        headers={"User-Agent": "XSStrike"}
    )
    return context

@patch('modes.scan.requester')
@patch('core.checker.requester')
def test_full_scan_flow(mock_checker_req, mock_scan_req, vulnerable_context):
    # 1. Mock initial scan response (with reflection)
    initial_res = MagicMock()
    initial_res.text = '<html><body>Search for: v3dm0s</body></html>'
    mock_scan_req.return_value = initial_res
    
    # 2. Mock checker response (for payload)
    # Let's say '<svg>' works
    checker_res = MagicMock()
    checker_res.text = '<html><body>Search for: st4r7s<svg>3nd</body></html>'
    mock_checker_req.return_value = checker_res
    
    scanner = Scanner(vulnerable_context)
    
    # We don't want it to actually print everything to console during tests, 
    # but we want to check if it completes without error and finds something.
    # In a more advanced test, we could capture logs.
    scanner.scan(skip_confirm=True)
    
    assert mock_scan_req.called
    assert mock_checker_req.called
