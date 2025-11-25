from src.protocol_layer.protocols.capsule_uri import parse_capsule_uri


def test_parse_basic_uri():
    uri = "capsule://fusion/mhd64/v4.1"
    parsed = parse_capsule_uri(uri)
    assert parsed.authority == "fusion"
    assert parsed.domain == "mhd64"
    assert parsed.subdomains == []
    assert parsed.operation == "v4.1"
    assert parsed.version is None


def test_parse_with_params_and_subdomains():
    uri = "capsule://org-x/materials/stress-analysis/v2?material=titanium&temp=1500K"
    parsed = parse_capsule_uri(uri)
    assert parsed.authority == "org-x"
    assert parsed.domain == "materials"
    assert parsed.subdomains == []
    assert parsed.operation == "stress-analysis"
    assert parsed.version == "v2"
    assert parsed.params["material"] == "titanium"
    assert parsed.params["temp"] == "1500K"


def test_parse_with_subdomains_and_version():
    uri = "capsule://fusion/plasma/coil/optimize/v3"
    parsed = parse_capsule_uri(uri)
    assert parsed.authority == "fusion"
    assert parsed.domain == "plasma"
    assert parsed.subdomains == ["coil"]
    assert parsed.operation == "optimize"
    assert parsed.version == "v3"
