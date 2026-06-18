"""
app.py
======
Streamlit demo of 10 features of the `sql` package (sql>=2022.4.0),
a tiny "DB API 2.0 for Humans" wrapper around any PEP 249 connection.

Run with:
    streamlit run app.py

Everything in this UI is backed by features.py, which itself only calls
sql.SQL's four real methods: run(), commit(), one(), all().
"""
import streamlit as st
import features as f

st.set_page_config(page_title="sql package demo", page_icon="🗄️", layout="wide")


# --- session state: one sql.SQL instance shared across reruns ----------
if "bliss" not in st.session_state:
    st.session_state.bliss = f.get_bliss(":memory:")
    f.create_table(st.session_state.bliss)
    st.session_state.bliss.commit()

bliss = st.session_state.bliss


def render_records(records, empty_msg="No rows."):
    """Render a list of namedtuples (from sql.SQL.all) as a table."""
    if not records:
        st.info(empty_msg)
        return
    columns = records[0]._fields
    data = [dict(zip(columns, r)) for r in records]
    st.table(data)


st.title("`sql` package")
st.caption(
    "Every action below calls straight into `sql.SQL.run()`, `.commit()`, "
    "`.one()`, or `.all()` — the package's entire public API."
)

with st.expander("What is the `sql` package?", expanded=False):
    st.markdown(
        "[`sql`](https://pypi.org/project/sql/) (`uv add sql`) is a "
        "tiny wrapper around any DB API 2.0 connection (sqlite3, psycopg2, "
        "etc). It has exactly **4 methods**:\n\n"
        "- `run(query, args=None)` — execute a statement, ignore the result, return `self`\n"
        "- `commit()` — shortcut for `connection.commit()`, also returns `self` so it chains\n"
        "- `one(query, args=None)` — fetch a single row: a scalar if one column, a namedtuple if several\n"
        "- `all(query, args=None)` — fetch every row, same scalar/namedtuple rule\n\n"
        "The 10 tabs here show 10 different ways of combining those 4 methods."
    )

tabs = st.tabs([
    "1. Create table",
    "2. Single insert",
    "3. Batch insert",
    "4. Chained insert+commit",
    "5. Commit",
    "6. Fetch one",
    "7. Fetch all",
    "8. Update",
    "9. Delete",
    "10. Reset (drop table)",
])

# 1. CREATE TABLE ---------------------------------------------------------
with tabs[0]:
    st.subheader("Feature 1 — `run()` for DDL: CREATE TABLE")
    st.code(
        'bliss.run("CREATE TABLE IF NOT EXISTS contributors '
        '(firstname VARCHAR, lastname VARCHAR, commits INTEGER)")',
        language="python",
    )
    if st.button("Create table", key="btn_create"):
        msg = f.create_table(bliss)
        bliss.commit()
        st.success(msg)

# 2. SINGLE INSERT ----------------------------------------------------------
with tabs[1]:
    st.subheader("Feature 2 — `run()` with a single tuple of args: INSERT")
    st.code(
        'bliss.run("INSERT INTO contributors VALUES (?, ?, ?)", '
        '(firstname, lastname, commits))',
        language="python",
    )
    c1, c2, c3 = st.columns(3)
    fn = c1.text_input("First name", value="Guido", key="ins_fn")
    ln = c2.text_input("Last name", value="van Rossum", key="ins_ln")
    cm = c3.number_input("Commits", min_value=0, value=100, key="ins_cm")
    if st.button("Insert row", key="btn_insert_one"):
        msg = f.insert_one(bliss, fn, ln, int(cm))
        bliss.commit()
        st.success(msg)

# 3. BATCH INSERT -----------------------------------------------------------
with tabs[2]:
    st.subheader("Feature 3 — `run()` with a *list* of tuples: batch INSERT")
    st.caption("Internally this routes to `cursor.executemany(...)`.")
    st.code(
        'bliss.run("INSERT INTO contributors VALUES (?, ?, ?)", [\n'
        '    ("Andrew", "Kuchling", 5),\n'
        '    ("James", "Henstridge", 12),\n'
        '    ("Daniele", "Varrazzo", 30),\n'
        '])',
        language="python",
    )
    if st.button("Insert sample batch of 3 contributors", key="btn_batch"):
        sample_rows = [
            ("Andrew", "Kuchling", 5),
            ("James", "Henstridge", 12),
            ("Daniele", "Varrazzo", 30),
        ]
        msg = f.insert_many(bliss, sample_rows)
        bliss.commit()
        st.success(msg)

# 4. CHAINED run().commit() ---------------------------------------------
with tabs[3]:
    st.subheader("Feature 4 — `run()` returns `self`, so chain `.commit()`")
    st.code(
        'bliss.run("INSERT INTO contributors VALUES (?, ?, ?)", '
        '(firstname, lastname, commits)).commit()',
        language="python",
    )
    c1, c2, c3 = st.columns(3)
    fn2 = c1.text_input("First name", value="Marc-Andre", key="chain_fn")
    ln2 = c2.text_input("Last name", value="Lemburg", key="chain_ln")
    cm2 = c3.number_input("Commits", min_value=0, value=50, key="chain_cm")
    if st.button("Insert + commit in one chained call", key="btn_chain"):
        msg = f.insert_and_commit(bliss, fn2, ln2, int(cm2))
        st.success(msg)

# 5. COMMIT ---------------------------------------------------------------
with tabs[4]:
    st.subheader("Feature 5 — `commit()` on its own")
    st.caption("Shortcut for `bliss.connection.commit()`.")
    st.code('bliss.commit()', language="python")
    if st.button("Commit current transaction", key="btn_commit"):
        msg = f.commit(bliss)
        st.success(msg)

# 6. FETCH ONE --------------------------------------------------------------
with tabs[5]:
    st.subheader("Feature 6 — `one()`: fetch a single row")
    st.caption(
        "Multiple columns selected → `one()` returns a **namedtuple**."
    )
    st.code(
        'bliss.one("SELECT firstname, lastname, commits FROM contributors '
        'WHERE lastname = ?", (lastname,))',
        language="python",
    )
    existing = f.list_lastnames(bliss)
    if existing:
        chosen = st.selectbox("Lastname to look up", existing, key="one_ln")
        if st.button("Fetch one", key="btn_one"):
            row = f.fetch_one(bliss, chosen)
            if row is None:
                st.warning("No matching row.")
            else:
                st.success(f"Got back: `{row}`  (type: `{type(row).__name__}`)")
                st.write(f"row.firstname = **{row.firstname}**, row.commits = **{row.commits}**")
    else:
        st.info("No contributors yet — insert some rows in the earlier tabs first.")

    st.divider()
    st.caption("`one()` also returns a plain scalar when only one column is selected:")
    st.code('bliss.one("SELECT COUNT(*) FROM contributors")', language="python")
    if st.button("Count rows (scalar one())", key="btn_count_one"):
        n = f.count_rows(bliss)
        st.success(f"COUNT(*) = {n}  (type: `{type(n).__name__}`)")

# 7. FETCH ALL --------------------------------------------------------------
with tabs[6]:
    st.subheader("Feature 7 — `all()`: fetch every row")
    st.caption("Multiple columns selected → `all()` returns a list of namedtuples.")
    st.code(
        'bliss.all("SELECT firstname, lastname, commits FROM contributors '
        'ORDER BY commits DESC")',
        language="python",
    )
    if st.button("Fetch all contributors", key="btn_all"):
        records = f.fetch_all(bliss)
        render_records(records, empty_msg="Table is empty — insert some rows first.")

    st.divider()
    st.caption("Single column selected → `all()` returns a plain list of scalars:")
    st.code('bliss.all("SELECT lastname FROM contributors ORDER BY lastname")', language="python")
    if st.button("List lastnames only", key="btn_lastnames"):
        st.write(f.list_lastnames(bliss))

# 8. UPDATE -------------------------------------------------------------
with tabs[7]:
    st.subheader("Feature 8 — `run()` for UPDATE")
    st.code(
        'bliss.run("UPDATE contributors SET commits = ? WHERE lastname = ?", '
        '(new_commits, lastname))',
        language="python",
    )
    existing2 = f.list_lastnames(bliss)
    if existing2:
        target = st.selectbox("Lastname to update", existing2, key="upd_ln")
        new_val = st.number_input("New commit count", min_value=0, value=0, key="upd_val")
        if st.button("Update", key="btn_update"):
            msg = f.update_commits(bliss, target, int(new_val))
            bliss.commit()
            st.success(msg)
    else:
        st.info("No contributors yet — insert some rows in the earlier tabs first.")

# 9. DELETE ---------------------------------------------------------------
with tabs[8]:
    st.subheader("Feature 9 — `run()` for DELETE")
    st.code('bliss.run("DELETE FROM contributors WHERE lastname = ?", (lastname,))', language="python")
    existing3 = f.list_lastnames(bliss)
    if existing3:
        target3 = st.selectbox("Lastname to delete", existing3, key="del_ln")
        if st.button("Delete", key="btn_delete"):
            msg = f.delete_contributor(bliss, target3)
            bliss.commit()
            st.success(msg)
    else:
        st.info("No contributors yet — insert some rows in the earlier tabs first.")

# 10. RESET / DROP TABLE -----------------------------------------------
with tabs[9]:
    st.subheader("Feature 10 — `run()` for DDL: DROP TABLE (reset demo)")
    st.code('bliss.run("DROP TABLE IF EXISTS contributors")', language="python")
    st.warning("This wipes all demo data so you can start fresh.")
    if st.button("Drop table", key="btn_drop"):
        msg = f.drop_table(bliss)
        f.create_table(bliss)
        bliss.commit()
        st.success(msg + " (recreated empty, ready to use again)")

# --- Always-visible live view of current table state --------------------
st.divider()
st.subheader("📋 Current `contributors` table")
records = f.fetch_all(bliss)
render_records(records, empty_msg="Table is empty.")
col_a, col_b = st.columns(2)
col_a.metric("Row count", f.count_rows(bliss) or 0)
col_b.metric("Total commits", f.total_commits(bliss) or 0)
