import re
import json
import hashlib
from urllib.parse import urlparse

from xsstrike.core.colors import green, end
from xsstrike.core.requester import requester
from xsstrike.core.utils import deJSON, js_extractor, handle_anchor, getVar, updateVar
from xsstrike.core.log import setup_logger

logger = setup_logger(__name__)


def is_defined(o):
    return o is not None


def scan(data, extractor, definitions, matcher=None):
    matcher = matcher or _simple_match
    detected = []
    for component in definitions:
        extractors = definitions[component].get(
            "extractors", None).get(
            extractor, None)
        if (not is_defined(extractors)):
            continue
        for i in extractors:
            match = matcher(i, data)
            if (match):
                detected.append({"version": match,
                                 "component": component,
                                 "detection": extractor})
    return detected


def _simple_match(regex, data):
    regex = deJSON(regex)
    match = re.search(regex, data)
    return match.group(1) if match else None


def _replacement_match(regex, data):
    try:
        regex = deJSON(regex)
        group_parts_of_regex = r'^\/(.*[^\\])\/([^\/]+)\/$'
        ar = re.search(group_parts_of_regex, regex)
        search_for_regex = "(" + ar.group(1) + ")"
        match = re.search(search_for_regex, data)
        ver = None
        if (match):
            ver = re.sub(ar.group(1), ar.group(2), match.group(0))
            return ver

        return None
    except:
        return None


def _scanhash(hash, definitions):
    for component in definitions:
        hashes = definitions[component].get("extractors", None).get("hashes", None)
        if (not is_defined(hashes)):
            continue
        for i in hashes:
            if (i == hash):
                return [{"version": hashes[i],
                         "component": component,
                         "detection": 'hash'}]

    return []


def check(results, definitions):
    for r in results:
        result = r

        if (not is_defined(definitions[result.get("component", None)])):
            continue
        vulns = definitions[
            result.get(
                "component",
                None)].get(
            "vulnerabilities",
            None)
        for i in range(len(vulns)):
            if (not _is_at_or_above(result.get("version", None),
                                vulns[i].get("below", None))):
                if (is_defined(vulns[i].get("atOrAbove", None)) and not _is_at_or_above(
                        result.get("version", None), vulns[i].get("atOrAbove", None))):
                    continue

                vulnerability = {"info": vulns[i].get("info", None)}
                if (vulns[i].get("severity", None)):
                    vulnerability["severity"] = vulns[i].get("severity", None)

                if (vulns[i].get("identifiers", None)):
                    vulnerability["identifiers"] = vulns[
                        i].get("identifiers", None)

                result["vulnerabilities"] = result.get(
                    "vulnerabilities", None) or []
                result["vulnerabilities"].append(vulnerability)

    return results


def unique(ar):
    return list(set(ar))


def _is_at_or_above(version1, version2):
    # print "[",version1,",", version2,"]"
    v1 = re.split(r'[.-]', version1)
    v2 = re.split(r'[.-]', version2)

    l = len(v1) if len(v1) > len(v2) else len(v2)
    for i in range(l):
        v1_c = _to_comparable(v1[i] if len(v1) > i else None)
        v2_c = _to_comparable(v2[i] if len(v2) > i else None)
        # print v1_c, "vs", v2_c
        if (not isinstance(v1_c, type(v2_c))):
            return isinstance(v1_c, int)
        if (v1_c > v2_c):
            return True
        if (v1_c < v2_c):
            return False

    return True


def _to_comparable(n):
    if (not is_defined(n)):
        return 0
    if (re.search(r'^[0-9]+$', n)):
        return int(str(n), 10)

    return n


def _replace_version(jsRepoJsonAsText):
    return re.sub(r'[.0-9]*', '[0-9][0-9.a-z_\-]+', jsRepoJsonAsText)


def is_vulnerable(results):
    for r in results:
        if ('vulnerabilities' in r):
            # print r
            return True

    return False


def scan_uri(uri, definitions):
    result = scan(uri, 'uri', definitions)
    return check(result, definitions)


def scan_filename(fileName, definitions):
    result = scan(fileName, 'filename', definitions)
    return check(result, definitions)


def scan_file_content(content, definitions):
    result = scan(content, 'filecontent', definitions)
    if (len(result) == 0):
        result = scan(content, 'filecontentreplace', definitions, _replacement_match)

    if (len(result) == 0):
        result = _scanhash(
            hashlib.sha1(
                content.encode('utf8')).hexdigest(),
            definitions)

    return check(result, definitions)


def main_scanner(uri, response):
    definitions = getVar('definitions')
    uri_scan_result = scan_uri(uri, definitions)
    filecontent = response
    filecontent_scan_result = scan_file_content(filecontent, definitions)
    uri_scan_result.extend(filecontent_scan_result)
    result = {}
    if uri_scan_result:
        result['component'] = uri_scan_result[0]['component']
        result['version'] = uri_scan_result[0]['version']
        result['vulnerabilities'] = []
        vulnerabilities = set()
        for i in uri_scan_result:
            k = set()
            try:
                for j in i['vulnerabilities']:
                    vulnerabilities.add(str(j))
            except KeyError:
                pass
        for vulnerability in vulnerabilities:
            result['vulnerabilities'].append(json.loads(vulnerability.replace('\'', '"')))
        return result

def retireJs(url, response):
    scripts = js_extractor(response)
    for script in scripts:
        if script not in getVar('checkedScripts'):
            updateVar('checkedScripts', script, 'add')
            uri = handle_anchor(url, script)
            response = requester(uri, '', getVar('headers'), True, getVar('delay'), getVar('timeout')).text
            result = main_scanner(uri, response)
            if result:
                logger.red_line()
                logger.good('Vulnerable component: ' + result['component'] + ' v' + result['version'])
                logger.info('Component location: %s' % uri)
                details = result['vulnerabilities']
                logger.info('Total vulnerabilities: %i' % len(details))
                for detail in details:
                    logger.info('%sSummary:%s %s' % (green, end, detail['identifiers']['summary']))
                    logger.info('Severity: %s' % detail['severity'])
                    logger.info('CVE: %s' % detail['identifiers']['CVE'][0])
                logger.red_line()
