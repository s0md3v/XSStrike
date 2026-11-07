"""Focused delimiter-preservation tests for ``core.utils.getParams``.

Added 2026-11-07 for the two maxsplit fixes in ``core/utils.py``:
``url.split('?', 1)[1]`` (text after a second ``?`` is no longer dropped) and
``part.split('=', 1)`` (a value may contain further ``=`` signs).

The second fix is in the parser shared by GET queries and ordinary form-data,
so form-data values containing ``=`` are corrected by the same change.  That
effect is tested and disclosed here; it is not a promise that every POST body
is byte-identical to the pre-fix output for inputs that contain the defect.

XSStrike is licensed under the GNU GPLv3 (see LICENSE).

Isolation: importing this module has no side effects and installs no
process-wide network patch.  A test that drives the real consumer requests the
function-scoped ``offline`` fixture, which replaces
``requests.adapters.HTTPAdapter.send`` with an offline 200 responder for that
one test (recording the prepared request); ``runtime`` initialises
``core.config.globalVariables`` the way ``xsstrike.py`` does at runtime.
``pytest``'s ``monkeypatch`` restores both exactly when the test ends.  Socket
and DNS containment belongs to the external research harness, not to this
file, and no test depends on another test having run first.
"""
import json
import os
import sys
from urllib.parse import parse_qs

import pytest
import requests
from requests.adapters import HTTPAdapter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
# ``import core`` must work for ``pytest`` as well as ``python -m pytest``.
# The path is only touched when the checkout root is not already importable,
# so a normal ``python -m pytest`` run from the checkout changes nothing.
_KNOWN = {os.path.normcase(os.path.abspath(entry or os.getcwd())) for entry in sys.path}
if os.path.normcase(SRC) not in _KNOWN:
    sys.path.insert(0, SRC)

import core.config
import core.requester
import core.utils

GET = True
POST = False


def _offline_response(request):
    """A requests.Response that looks like an ordinary 200 HTML page."""
    response = requests.Response()
    response.status_code = 200
    response.url = request.url
    response.request = request
    response.reason = 'OK'
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    response._content = b'<html><body>offline fixture</body></html>'
    response.encoding = 'utf-8'
    return response


@pytest.fixture
def runtime(monkeypatch):
    """Genuine runtime initialisation for one test.

    ``xsstrike.py`` assigns ``vars(args)`` here, and ``--json`` / ``--path``
    are ``store_true`` flags, so both are ``False`` on an ordinary run.
    ``monkeypatch`` puts every touched key back exactly, including deleting a
    key that did not exist before, so the dict is identical after the test.
    """
    monkeypatch.setitem(core.config.globalVariables, 'jsonData', False)
    monkeypatch.setitem(core.config.globalVariables, 'path', False)


@pytest.fixture
def offline(runtime, monkeypatch):
    """Per-test transport seam; returns the intercepted prepared requests."""
    sent = []

    def send(adapter, request, **kwargs):
        body = request.body
        if isinstance(body, bytes):
            body = body.decode('utf-8', 'replace')
        sent.append({'method': request.method, 'url': request.url, 'body': body})
        return _offline_response(request)

    monkeypatch.setattr(HTTPAdapter, 'send', send)
    return sent


def _consume(offline, target, params=None, method=GET):
    """Drive the real consumer and return (prepared_url, prepared_body)."""
    base = core.utils.getUrl(target, method)
    before = len(offline)
    response = core.requester.requester(base, params, {}, method, 0, 10)
    assert len(offline) - before == 1, 'expected exactly one intercepted transport call'
    assert response.status_code == 200
    return offline[-1]['url'], offline[-1]['body']


def _query_of(url):
    """Parse the query of a prepared URL the way an HTTP server would."""
    return parse_qs(url.split('?', 1)[1], keep_blank_values=True)


# --------------------------------------------------------------------------
# The two admitted fixes, through the real consumer.
# --------------------------------------------------------------------------
def test_question_mark_inside_value_keeps_later_parameters(offline):
    target = 'https://example.invalid/search?q=alpha&next=/login?return=1&flag=a+b'
    params = core.utils.getParams(target, None, GET)
    assert params == {'q': 'alpha', 'next': '/login?return=1', 'flag': 'a+b'}

    url, body = _consume(offline, target, params)
    assert body is None
    query = _query_of(url)
    assert query['q'] == ['alpha']
    assert query['next'] == ['/login?return=1']
    assert query['flag'] == ['a+b']


def test_equals_sign_inside_value_is_preserved(offline):
    target = 'https://example.invalid/search?q=alpha&token=AbC==&sig=a=b=c'
    params = core.utils.getParams(target, None, GET)
    assert params == {'q': 'alpha', 'token': 'AbC==', 'sig': 'a=b=c'}

    url, body = _consume(offline, target, params)
    assert body is None
    query = _query_of(url)
    assert query['token'] == ['AbC==']
    assert query['sig'] == ['a=b=c']


def test_combined_question_mark_and_equals_in_value(offline):
    target = 'https://example.invalid/p?a=1&b=x?y=z==&c=3'
    params = core.utils.getParams(target, None, GET)
    assert params == {'a': '1', 'b': 'x?y=z==', 'c': '3'}

    url, _body = _consume(offline, target, params)
    query = _query_of(url)
    assert query['b'] == ['x?y=z==']
    assert query['c'] == ['3']


# --------------------------------------------------------------------------
# Existing semantics that must not change (regressions).
# --------------------------------------------------------------------------
def test_empty_duplicate_and_missing_equals_entries(offline):
    target = 'https://example.invalid/search?a=&b=1&b=2&c'
    params = core.utils.getParams(target, None, GET)
    assert params['a'] == ''
    assert params['b'] == '2'          # last wins, unchanged
    assert params['c'] == ''           # missing '=' still yields ''

    url, _body = _consume(offline, target, params)
    query = _query_of(url)
    assert query['a'] == ['']
    assert query['b'] == ['2']
    assert query['c'] == ['']


def test_plain_get_query_round_trip(offline):
    target = 'https://example.invalid/search?a=1&b=2'
    params = core.utils.getParams(target, None, GET)
    assert params == {'a': '1', 'b': '2'}

    url, _body = _consume(offline, target, params)
    assert _query_of(url) == {'a': ['1'], 'b': ['2']}


def test_geturl_and_path_handling_unchanged():
    target = 'https://example.invalid/deep/path?x=1'
    assert core.utils.getUrl(target, GET) == 'https://example.invalid/deep/path'
    assert core.utils.getUrl(target, POST) == target
    assert core.utils.getParams(target, None, GET) == {'x': '1'}


def test_no_query_returns_none():
    assert core.utils.getParams('https://example.invalid/login', None, GET) is None


def test_ordinary_form_data_keeps_extra_equals(offline):
    # Shared-parser effect, disclosed: a form-data value containing '=' is no
    # longer truncated by the same change that fixes the GET query path.
    body = 'user=alice&token=AbC==&note=a=b'
    params = core.utils.getParams('https://example.invalid/post', body, POST)
    assert params == {'user': 'alice', 'token': 'AbC==', 'note': 'a=b'}

    url, prepared_body = _consume(offline, 'https://example.invalid/post', params, POST)
    assert '?' not in url
    assert parse_qs(prepared_body, keep_blank_values=True) == {
        'user': ['alice'], 'token': ['AbC=='], 'note': ['a=b'],
    }


def test_ordinary_form_data_without_defect_unchanged(offline):
    body = 'a=1&b=2'
    params = core.utils.getParams('https://example.invalid/post', body, POST)
    assert params == {'a': '1', 'b': '2'}

    _url, prepared_body = _consume(offline, 'https://example.invalid/post', params, POST)
    assert parse_qs(prepared_body, keep_blank_values=True) == {'a': ['1'], 'b': ['2']}


def test_json_body_control_unchanged(runtime):
    payload = json.dumps({'a': '1', 'b': 'two'})
    params = core.utils.getParams('https://example.invalid/api', payload, POST)
    assert params == {'a': '1', 'b': 'two'}


# --------------------------------------------------------------------------
# Boundaries this patch deliberately does not change (documented, tolerant).
# --------------------------------------------------------------------------
def test_decoding_boundary_documented_not_locked():
    # Values stay raw text today (the consumer re-encodes the dict, so
    # '%E4' is sent as '%25E4').  A later decoding fix is allowed to change
    # this, so the assertion accepts either the raw or the decoded text and
    # only requires that nothing was truncated.
    target = 'https://example.invalid/search?q=%E4%B8%AD%E6%96%87&flag=a+b'
    params = core.utils.getParams(target, None, GET)
    assert params['q'] in ('%E4%B8%AD%E6%96%87', '\u4e2d\u6587')
    assert params['flag'] in ('a+b', 'a b')


def test_fragment_boundary_documented_not_locked():
    # Today the fragment text is absorbed into the value ('1#frag').  A later
    # fragment fix may strip or encode it; only the parameter name and the
    # leading value must survive.
    params = core.utils.getParams('https://example.invalid/search?a=1#frag', None, GET)
    assert params['a'] in ('1#frag', '1')
    assert params['a'].startswith('1')
