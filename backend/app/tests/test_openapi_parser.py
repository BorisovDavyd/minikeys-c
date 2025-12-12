from app.parsers.openapi_parser import OpenAPIParser
from sample_inputs.openapi_sample import SAMPLE_YAML


def test_list_paths():
    parser = OpenAPIParser(SAMPLE_YAML)
    paths = parser.list_paths()
    assert "/vms" in paths
    assert "/disks/{id}" in paths


def test_operations_count():
    parser = OpenAPIParser(SAMPLE_YAML)
    ops = parser.operations()
    assert any(op["operationId"] == "create_vm" for op in ops)
    assert len(ops) >= 10
