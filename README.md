# `frictionless` package — 10 feature demo

A Streamlit app demonstrating 10 features of the
[`frictionless`](https://pypi.org/project/frictionless/) PyPI package —
a "DEVT" (Describe, Extract, Validate, Transform) framework for tabular
data, built around real, well-documented top-level functions and classes.

## The 10 features

1. **Describe** (`describe()`) — infer a schema (field names + types) from a file
2. **Extract** (`extract()`) — read and normalize all rows from a file
3. **Validate** (`validate()`) — run default checks, get a `Report`
4. **Custom check** (`validate(checks=[...])`) — e.g. `checks.sequential_value`
5. **Build a schema by hand** (`Schema`, `fields.IntegerField`, etc.)
6. **Detector** — control inference: force a field type, custom sample size
7. **`report.flatten()`** — turn a nested validation report into flat rows
8. **Resource exploration** (`Resource`, `.infer(stats=True)`) — metadata + stats
9. **Transform** (`transform()` + `steps.field_filter` / `steps.row_filter`) — clean/reshape data
10. **Save schema** (`schema.to_json()` / `.to_yaml()`) — persist metadata to disk

## Files

- `features.py` — one function per feature, calling real `frictionless` functions/classes
- `app.py` — the Streamlit UI, one tab per feature
- `sample_data/countries_valid.csv` — a clean sample file
- `sample_data/countries_invalid.csv` — a deliberately messy file (blank
  header, duplicate header, missing cells, a blank row, and an extra
  cell), reproducing the same error categories shown in frictionless's
  own documentation examples

## Running it

```bash
uv sync
streamlit run app.py
```

No upload needed — every tab lets you pick between the two bundled
sample CSVs to see each feature in action on both clean and messy data.
