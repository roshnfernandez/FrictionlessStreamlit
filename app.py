"""
app.py
======
Streamlit demo of 10 features of the `frictionless` package
(https://pypi.org/project/frictionless/), the DEVT (Describe, Extract,
Validate, Transform) data framework.

Run with:
    pip install -r requirements.txt
    streamlit run app.py

Ships with two built-in sample CSVs (sample_data/countries_valid.csv and
sample_data/countries_invalid.csv) so it works out of the box with no
upload required.
"""
import os
import tempfile

import streamlit as st

import features as f

st.set_page_config(page_title="frictionless demo", page_icon="🧹", layout="wide")

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
VALID_CSV = os.path.join(SAMPLE_DIR, "countries_valid.csv")
INVALID_CSV = os.path.join(SAMPLE_DIR, "countries_invalid.csv")


def file_picker(key):
    """Shared widget: choose between the two bundled sample CSVs."""
    choice = st.radio(
        "Sample file",
        ["countries_valid.csv (clean)", "countries_invalid.csv (messy)"],
        key=key,
        horizontal=True,
    )
    return VALID_CSV if choice == "countries_valid.csv (clean)" else INVALID_CSV


def show_raw_csv(path):
    with open(path) as fh:
        st.code(fh.read(), language="text")


st.title("🧹 `frictionless` package — 10 features demo")
st.caption(
    "Every action below calls a real `frictionless` function: `describe`, "
    "`extract`, `validate`, `transform`, `Resource`, `Schema`, `Detector`, "
    "or `Report.flatten()`."
)

with st.expander("What is `frictionless`?", expanded=False):
    st.markdown(
        "[`frictionless`](https://pypi.org/project/frictionless/) "
        "(`pip install frictionless`) is a data management framework "
        "built around four ideas, sometimes called **DEVT**:\n\n"
        "- **Describe** — infer/edit metadata (schema, field types) for a table\n"
        "- **Extract** — read & normalize tabular data from CSV, Excel, JSON, SQL, etc.\n"
        "- **Validate** — check a table against its schema and report problems\n"
        "- **Transform** — clean and reshape data via composable `steps`\n\n"
        "The 10 tabs below show 10 different ways of using these four capabilities."
    )
    st.caption(
        "⚠️ This app requires the real `frictionless` package — "
        "`pip install -r requirements.txt` before running."
    )

tabs = st.tabs([
    "1. Describe",
    "2. Extract",
    "3. Validate",
    "4. Custom check",
    "5. Build schema",
    "6. Detector",
    "7. Flatten report",
    "8. Resource stats",
    "9. Transform",
    "10. Save schema",
])

# 1. DESCRIBE ---------------------------------------------------------------
with tabs[0]:
    st.subheader("Feature 1 — `describe()`: infer a schema")
    st.code('from frictionless import describe\nresource = describe(path)', language="python")
    path = VALID_CSV
    show_raw_csv(path)
    if st.button("Describe", key="btn_describe"):
        resource = f.describe_file(path)
        st.write("Inferred schema (field name → type):")
        st.json({fld.name: fld.type for fld in resource.schema.fields})

# 2. EXTRACT ------------------------------------------------------------------
with tabs[1]:
    st.subheader("Feature 2 — `extract()`: read normalized rows")
    st.code('from frictionless import extract\nrows = extract(path)', language="python")
    path2 = VALID_CSV
    if st.button("Extract rows", key="btn_extract"):
        rows = f.extract_rows(path2)
        st.write(f"{len(rows)} row(s) extracted, cells cast to inferred types:")
        st.table([dict(row) for row in rows])

# 3. VALIDATE -------------------------------------------------------------
with tabs[2]:
    st.subheader("Feature 3 — `validate()`: run default checks")
    st.code('from frictionless import validate\nreport = validate(path)', language="python")
    path3 = file_picker("validate_file")
    if st.button("Validate", key="btn_validate"):
        report = f.validate_file(path3)
        if report.valid:
            st.success("✅ report.valid = True — no errors found.")
        else:
            st.error("❌ report.valid = False — errors found:")
            rows = f.flatten_report(report, ["rowNumber", "fieldNumber", "type", "note"])
            st.table([
                {"row": r[0], "field": r[1], "type": r[2], "note": r[3]}
                for r in rows
            ])

# 4. VALIDATE WITH CUSTOM CHECK ---------------------------------------------
with tabs[3]:
    st.subheader("Feature 4 — `validate()` with a custom check")
    st.caption("`checks.sequential_value` confirms a column counts up without gaps.")
    st.code(
        'from frictionless import validate, checks\n'
        'report = validate(path, checks=[checks.sequential_value(field_name="id")])',
        language="python",
    )
    path4 = file_picker("custom_check_file")
    field_for_check = st.text_input("Field to check for sequential values", value="id", key="seq_field")
    if st.button("Validate with sequential_value check", key="btn_custom_check"):
        report = f.validate_with_sequential_check(path4, field_for_check)
        if report.valid:
            st.success(f"✅ '{field_for_check}' is sequential and the file is otherwise valid.")
        else:
            rows = f.flatten_report(report, ["rowNumber", "fieldNumber", "type", "note"])
            st.table([
                {"row": r[0], "field": r[1], "type": r[2], "note": r[3]}
                for r in rows
            ])

# 5. BUILD SCHEMA MANUALLY ---------------------------------------------------
with tabs[4]:
    st.subheader("Feature 5 — `Schema`: build a schema by hand")
    st.code(
        'from frictionless import Schema, fields\n'
        'schema = Schema(fields=[fields.IntegerField(name="id"), '
        'fields.StringField(name="name")])',
        language="python",
    )
    st.caption("Define fields below, one per line, as `name:type` (type ∈ integer, string, number, boolean, date).")
    spec_text = st.text_area(
        "Field specs",
        value="id:integer\nname:string\npopulation:number",
        key="schema_spec",
    )
    if st.button("Build schema", key="btn_build_schema"):
        specs = []
        for line in spec_text.strip().splitlines():
            if ":" in line:
                name, type_str = line.split(":", 1)
                specs.append((name.strip(), type_str.strip()))
        schema = f.build_schema(specs)
        st.session_state["built_schema"] = schema  # used later by tab 10
        st.json(schema.to_dict())

# 6. DETECTOR -----------------------------------------------------------------
with tabs[5]:
    st.subheader("Feature 6 — `Detector`: control inference behavior")
    st.code(
        'from frictionless import Detector, describe\n'
        'detector = Detector(field_type="string")  # force every field to one type\n'
        'resource = describe(path, detector=detector)',
        language="python",
    )
    path6 = VALID_CSV
    force_type = st.selectbox(
        "Force every field to this type (or leave default to auto-infer)",
        ["(auto-infer)", "string", "integer", "number", "any"],
        key="detector_type",
    )
    if st.button("Describe with Detector", key="btn_detector"):
        field_type = None if force_type == "(auto-infer)" else force_type
        resource = f.describe_with_detector(path6, field_type=field_type)
        st.json({fld.name: fld.type for fld in resource.schema.fields})

# 7. FLATTEN REPORT -----------------------------------------------------------
with tabs[6]:
    st.subheader("Feature 7 — `report.flatten()`: simplify validation errors")
    st.caption(
        "Validation reports can be deeply nested (grouped by task/file). "
        "`flatten()` turns them into one flat row per error."
    )
    st.code(
        'report = validate(path)\n'
        'report.flatten(["rowNumber", "fieldNumber", "code", "message"])',
        language="python",
    )
    path7 = file_picker("flatten_file")
    if st.button("Validate + flatten", key="btn_flatten"):
        report = f.validate_file(path7)
        flat = f.flatten_report(report, ["rowNumber", "fieldNumber", "code", "message"])
        if not flat:
            st.success("No errors to flatten — file is valid.")
        else:
            st.write(f"{len(flat)} error(s), flattened to a simple list:")
            for row in flat:
                st.write(f"`{row}`")

# 8. RESOURCE STATS -------------------------------------------------------
with tabs[7]:
    st.subheader("Feature 8 — `Resource`: explore metadata & stats")
    st.code(
        'from frictionless import Resource\n'
        'resource = Resource(path)\n'
        'resource.infer(stats=True)\n'
        'print(resource.stats)  # hash, bytes, fields, rows',
        language="python",
    )
    path8 = VALID_CSV
    if st.button("Explore resource", key="btn_resource"):
        resource = f.explore_resource(path8)
        c1, c2 = st.columns(2)
        with c1:
            st.write("**Metadata**")
            st.json({
                "name": resource.name,
                "format": resource.format,
                "encoding": resource.encoding,
                "scheme": resource.scheme,
            })
        with c2:
            st.write("**Stats**")
            stats = resource.stats
            # resource.stats behaves like a dict-ish metadata object in
            # frictionless; read defensively in case it's attribute-only
            # or mapping-only depending on installed version.
            def _get(obj, key, default=None):
                if hasattr(obj, key):
                    return getattr(obj, key)
                try:
                    return obj[key]
                except (KeyError, TypeError):
                    return default

            st.json({
                "rows": _get(stats, "rows"),
                "fields": _get(stats, "fields"),
                "bytes": _get(stats, "bytes"),
                "hash": _get(stats, "hash"),
            })

# 9. TRANSFORM ------------------------------------------------------------
with tabs[8]:
    st.subheader("Feature 9 — `transform()`: clean / reshape data")
    st.caption("Two common steps: keep only some columns, or filter rows by a formula.")

    st.markdown("**9a. Keep only selected columns** (`steps.field_filter`)")
    st.code(
        'from frictionless import transform, steps\n'
        'target = transform(path, steps=[steps.field_filter(names=["id", "name"])])',
        language="python",
    )
    path9 = VALID_CSV
    cols = st.text_input("Columns to keep (comma-separated)", value="id,name", key="keep_cols")
    if st.button("Transform: keep columns", key="btn_transform_fields"):
        names = [c.strip() for c in cols.split(",") if c.strip()]
        target = f.transform_keep_fields(path9, names)
        st.table([dict(row) for row in target.read_rows()])

    st.divider()
    st.markdown("**9b. Filter rows by a formula** (`steps.row_filter`)")
    st.code(
        'target = transform(path, steps=[\n'
        '    steps.table_normalize(),\n'
        '    steps.row_filter(formula="population > 50000000"),\n'
        '])',
        language="python",
    )
    path9b = VALID_CSV
    formula = st.text_input("Row filter formula", value="population > 50000000", key="row_formula")
    if st.button("Transform: filter rows", key="btn_transform_rows"):
        target = f.transform_filter_rows(path9b, formula)
        st.table([dict(row) for row in target.read_rows()])

# 10. SAVE SCHEMA -------------------------------------------------------------
with tabs[9]:
    st.subheader("Feature 10 — `Schema.to_json()` / `.to_yaml()`: save metadata")
    st.code('schema.to_json("schema.json")\nschema.to_yaml("schema.yaml")', language="python")
    st.caption(
        "Uses the schema built in tab 5 if available, otherwise describes "
        "the chosen sample file first."
    )
    path10 = VALID_CSV
    fmt = st.radio("Save as", ["JSON", "YAML"], key="save_fmt", horizontal=True)
    if st.button("Save schema", key="btn_save_schema"):
        schema = st.session_state.get("built_schema")
        if schema is None:
            resource = f.describe_file(path10)
            schema = resource.schema
            st.info("No schema built in tab 5 yet — describing the sample file instead.")
        suffix = ".json" if fmt == "JSON" else ".yaml"
        with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False) as tmp:
            out_path = tmp.name
        f.save_schema(schema, out_path)
        with open(out_path) as fh:
            content = fh.read()
        st.code(content, language="json" if fmt == "JSON" else "yaml")
        st.download_button(
            f"Download schema.{fmt.lower()}",
            content,
            file_name=f"schema{suffix}",
        )