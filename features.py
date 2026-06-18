"""
features.py
============
Ten small, self-contained demonstrations of the `frictionless` package
(https://pypi.org/project/frictionless/, the "DEVT" - Describe, Extract,
Validate, Transform - framework).

Every function below calls real frictionless top-level functions/classes:
describe, extract, validate, Resource, Schema, Detector, Checklist, Pipeline,
steps, checks.

Requires: pip install frictionless
"""
import os

from frictionless import (
    Checklist,
    Detector,
    Field,
    Resource,
    Schema,
    checks,
    describe,
    extract,
    steps,
    validate,
    system, transform
)


# 1. DESCRIBE -------------------------------------------------------------
def describe_file(path):
    """Feature 1: describe() - infer a schema (field names + types) from
    a tabular file, without reading/validating all the data."""
    resource = describe(path)
    return resource


# 2. EXTRACT ----------------------------------------------------------------
def extract_rows(path):
    """Feature 2: extract() - read and normalize all rows from a file,
    casting cells to the types inferred (or provided) by the schema.

    In frictionless v5+, extract() always returns a dict keyed by resource
    name, e.g. {'invalid': [Row(...), Row(...), ...]}.
    This unwraps that single-resource result into just the list of rows.
    """
    result = extract(path)
    if isinstance(result, dict):
        # single-file source -> {resource_name: [rows]}; take the only value
        rows = next(iter(result.values()))
    else:
        rows = result
    return [row for row in rows]


# 3. VALIDATE (basic) -------------------------------------------------------
def validate_file(path):
    """Feature 3: validate() - run frictionless default checks against a
    file and return a Report. report.valid is True/False."""
    with system.use_context(trusted=True):
        report = validate(path)
    return report


# 4. VALIDATE WITH CUSTOM CHECKS --------------------------------------------
def validate_with_sequential_check(path, field_name="id"):
    """Feature 4: validate() with a Checklist - in v5, custom checks are
    wrapped in a Checklist object."""
    checklist = Checklist(checks=[checks.sequential_value(field_name=field_name)])
    with system.use_context(trusted=True):
        report = validate(path, checklist=checklist)
    return report


# 5. BUILD A SCHEMA MANUALLY -------------------------------------------------
def build_schema(field_specs):
    """Feature 5: Schema - construct a Table Schema by hand from field
    definitions instead of inferring it. field_specs is a list of
    (name, type_str) tuples, e.g. [("id", "integer"), ("name", "string")].
    """
    built_fields = []
    for name, type_str in field_specs:
        built_fields.append(Field(name=name))

    schema = Schema(fields=built_fields)
    return schema


# 6. DETECTOR (custom inference behavior) ------------------------------------
def describe_with_detector(path, field_names=None, field_type=None, sample_size=100):
    """Feature 6: Detector - control how describe()/Resource() infer
    metadata: override field names, force every field to one type, or
    change how many rows are sampled for inference."""
    detector_kwargs = {"sample_size": sample_size}
    if field_names:
        detector_kwargs["field_names"] = field_names
    if field_type:
        detector_kwargs["field_type"] = field_type

    detector = Detector(**detector_kwargs)
    resource = describe(path, detector=detector)
    return resource


# 7. REPORT.FLATTEN (simplify validation errors) -----------------------------
def flatten_report(report, properties=None):
    """Feature 7: Report.flatten() - turn a validation Report into a flat
    list of [property, property, ...] rows, one per error."""
    if properties is None:
        properties = ["rowNumber", "fieldNumber", "type", "note"]
    return report.flatten(properties)


# 8. RESOURCE EXPLORATION (metadata + stats) ---------------------------------
def explore_resource(path):
    """Feature 8: Resource - open a resource and inspect its metadata
    (format, encoding, schema) and stats (rows, bytes, hash) after a
    read. Returns the opened resource object."""
    resource = Resource(path=path)
    resource.infer(stats=True)
    return resource


# 9. TRANSFORM (clean/reshape a resource) ------------------------------------
def transform_keep_fields(path, field_names):
    """Feature 9: Resource.transform() + Pipeline - keep only the given
    columns, dropping the rest, producing a cleaned target resource."""
    safe_path = os.path.relpath(path)
    target = transform(
        source=safe_path,
        steps=[steps.field_filter(names=field_names)]
    )
    return target


def transform_filter_rows(path, formula):
    """Feature 9b: Resource.transform() + Pipeline - keep only rows for
    which `formula` (a simpleeval expression over field names) is true."""
    safe_path = os.path.relpath(path)
    resource = Resource(path = str(safe_path))
    resource.infer()
    target = transform(
        source=resource,
        steps=[
            steps.table_normalize(),
            steps.row_filter(formula=formula)
        ]
    )
    return target


# 10. SAVE SCHEMA TO DISK -----------------------------------------------------
def save_schema(schema, out_path):
    """Feature 10: Schema.to_json()/to_yaml() - persist a schema (built by
    hand or inferred via describe) to a descriptor file on disk."""
    if out_path.endswith((".yaml", ".yml")):
        schema.to_yaml(out_path)
    else:
        schema.to_json(out_path)
    return out_path