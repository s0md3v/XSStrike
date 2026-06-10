"""Tests for XSStrike - Advanced XSS Scanner."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from core.colors import green, red, yellow, end
from core.config import xsschecker, specialAttributes
from core.encoders import base64
from core.generator import generator
from core.dom import dom
from core.utils import (
    converter, extractHeaders, getParams,
    getVar, reader, replaceValue, stripper,
    closest, fillHoles, randomUpper,
)
from core.htmlParser import htmlParser
from core.wafDetector import wafDetector
from core.zetanize import zetanize
from core.fuzzer import fuzzer
from core.filterChecker import filterChecker


class TestConfig:
    """Test configuration constants."""

    def test_xsschecker(self):
        assert isinstance(xsschecker, str)
        assert len(xsschecker) > 0

    def test_special_attributes(self):
        assert isinstance(specialAttributes, list)
        assert len(specialAttributes) > 0


class TestEncoders:
    """Test encoder functions."""

    def test_base64_encode(self):
        result = base64("<script>alert(1)</script>")
        assert result is not None
        assert isinstance(result, str)

    def test_base64_decode(self):
        encoded = base64("hello")
        assert isinstance(encoded, str)


class TestModules:
    """Test that core modules are callable."""

    def test_generator_callable(self):
        assert callable(generator)

    def test_dom_callable(self):
        assert callable(dom)

    def test_html_parser_callable(self):
        assert callable(htmlParser)

    def test_waf_detector_callable(self):
        assert callable(wafDetector)

    def test_zetanize_callable(self):
        assert callable(zetanize)

    def test_fuzzer_callable(self):
        assert callable(fuzzer)

    def test_filter_checker_callable(self):
        assert callable(filterChecker)


class TestUtils:
    """Test utility functions."""

    def test_converter_json(self):
        result = converter('{"a": 1}')
        assert result == {"a": 1}

    def test_converter_roundtrip(self):
        data = {"key": "value"}
        result = converter(converter(data))
        assert result == data

    def test_stripper_right(self):
        result = stripper("hello/", "/")
        assert result == "hello"

    def test_stripper_right_no_match(self):
        result = stripper("hello", "/")
        assert result == "hello"

    def test_extract_headers(self):
        result = extractHeaders("User-Agent: test\\nAccept: */*")
        assert isinstance(result, dict)
        assert "User-Agent" in result or "Accept" in result

    def test_get_params_query(self):
        result = getParams("http://example.com?q=test&id=1", "", "GET")
        assert isinstance(result, dict)

    def test_get_params_none(self):
        result = getParams("http://example.com", "", "GET")
        assert result is None

    def test_random_upper(self):
        result = randomUpper("test")
        assert isinstance(result, str)
        assert len(result) == 4

    def test_random_upper_empty(self):
        result = randomUpper("")
        assert result == ""


class TestReplaceValue:
    """Test replaceValue function."""

    def test_replace_dict_value(self):
        d = {"a": "old", "b": "keep"}
        result = replaceValue(d, "old", "new")
        assert result["a"] == "new"
        assert result["b"] == "keep"

    def test_replace_no_match(self):
        d = {"a": "x", "b": "y"}
        result = replaceValue(d, "z", "new")
        assert result["a"] == "x"
        assert result["b"] == "y"


class TestClosest:
    """Test closest function."""

    def test_closest_value(self):
        result = closest(5, {"a": 3, "b": 7, "c": 10})
        assert isinstance(result, dict)
        assert 7 in result.values() or 3 in result.values()


class TestFillHoles:
    """Test fillHoles function."""

    def test_fill_numeric(self):
        result = fillHoles("12", [1, 0])
        assert isinstance(result, list)
