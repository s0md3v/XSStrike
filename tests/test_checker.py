import pytest
from unittest.mock import MagicMock, patch
from core.checker import XSSChecker
from core.config import ScanContext, XSSConfig

@pytest.fixture
def mock_context():
    config = XSSConfig(xsschecker="v3dm0s")
    context = ScanContext(
        config=config,
        target="http://example.com/test",
        paramData={"q": "v3dm0s"},
        headers={"User-Agent": "XSStrike"}
    )
    return context

@patch('core.checker.requester')
def test_xss_checker_efficiency(mock_req, mock_context):
    checker = XSSChecker(mock_context)
    
    # Mock response containing the reflected string
    # check_string = 'st4r7s' + payload + '3nd'
    # For payload '<svg>', check_string = 'st4r7s<svg>3nd'
    mock_response = MagicMock()
    mock_response.text = "<html><body>st4r7s<svg>3nd</body></html>"
    mock_req.return_value = mock_response
    
    efficiencies = checker.check("<svg>", [0]) # position 0 (placeholder)
    
    assert len(efficiencies) > 0
    assert efficiencies[0] == 100 # Perfect reflection

@patch('core.checker.requester')
def test_xss_checker_partial_efficiency(mock_req, mock_context):
    checker = XSSChecker(mock_context)
    
    mock_response = MagicMock()
    # Reflected partially or filtered (e.g., stripped <>)
    mock_response.text = "<html><body>st4r7ssvg3nd</body></html>"
    mock_req.return_value = mock_response
    
    efficiencies = checker.check("<svg>", [0])
    
    assert len(efficiencies) > 0
    assert 0 < efficiencies[0] < 100
