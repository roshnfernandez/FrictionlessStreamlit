# `sql` package — 10 feature demo

A Streamlit app demonstrating 10 use-cases of the [`sql`](https://pypi.org/project/sql/)
PyPI package (`sql>=2022.4.0`), a tiny "DB API 2.0 for Humans" wrapper.

## Why only 4 methods power 10 "features"?

The `sql` package itself is intentionally minimal — its entire public API is:

| Method | Purpose |
|---|---|
| `run(query, args=None)` | execute a statement, ignore the result, returns `self` |
| `commit()` | shortcut for `connection.commit()`, also returns `self` |
| `one(query, args=None)` | fetch one row — scalar if 1 column, namedtuple if several |
| `all(query, args=None)` | fetch every row — same scalar/namedtuple rule |

The 10 "features" in this demo are 10 different real-world use-cases built
by combining those 4 methods with different SQL statements:

1. Create table (`run` + DDL)
2. Single parameterized insert (`run` + one tuple of args)
3. Batch insert (`run` + a *list* of tuples → `executemany` under the hood)
4. Chained `run(...).commit()` (since `run` returns `self`)
5. Standalone `commit()`
6. Fetch a single row (`one`) — shows both the namedtuple and scalar cases
7. Fetch all rows (`all`) — shows both the namedtuple-list and scalar-list cases
8. Update (`run` + UPDATE)
9. Delete (`run` + DELETE)
10. Drop / reset table (`run` + DDL)

## Files

- `sql.py` — vendored copy of the real `sql` package source (since this dev
  sandbox has no internet access for `pip install`). Behavior matches the
  published package exactly. **In your own environment, just run
  `pip install "sql>=2022.4.0"` and delete this file** — `import sql` will
  then resolve to the real PyPI package instead.
- `features.py` — one function per feature, calling only `sql.SQL`'s
  `run`/`commit`/`one`/`all` methods.
- `app.py` — the Streamlit UI, one tab per feature.

## Running it

```bash
pip install -r requirements.txt   # streamlit + the real sql package
# if you keep the vendored sql.py alongside app.py, the pip-installed
# `sql` package is simply shadowed by the local file — either way works
streamlit run app.py
```

Data lives in an in-memory SQLite database for the lifetime of the
Streamlit session (`st.session_state`), so it persists across button
clicks within a session but resets if the app restarts.
