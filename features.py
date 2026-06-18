"""
features.py
============
Ten small, self-contained demonstrations of the `sql` package
(https://pypi.org/project/sql/, sql>=2022.4.0).

Every function below talks to the database ONLY through an `sql.SQL`
instance's four real methods: run(), commit(), one(), all().
No raw cursor.execute()/fetchone()/fetchall() calls are sprinkled in here -
that would defeat the point of demoing the library. The only place a raw
sqlite3 connection is used is to open the connection itself, since `sql.SQL`
wraps -- but does not create -- a DB API 2.0 connection.
"""
import sqlite3
import sql


def get_bliss(db_path=":memory:"):
    """Open a sqlite3 connection and wrap it in sql.SQL, the package's
    single entry point. Named `bliss` to match the package's own docs."""
    connection = sqlite3.connect(db_path, check_same_thread=False)
    return sql.SQL(connection)


# 1. CREATE TABLE -------------------------------------------------------
def create_table(bliss):
    """Feature 1: run() for DDL - create the contributors table."""
    bliss.run(
        "CREATE TABLE IF NOT EXISTS contributors "
        "(firstname VARCHAR, lastname VARCHAR, commits INTEGER)"
    )
    return "Table 'contributors' created (or already existed)."


# 2. DROP TABLE (reset) --------------------------------------------------
def drop_table(bliss):
    """Feature 2: run() for DDL - drop the table, useful for resetting demo."""
    bliss.run("DROP TABLE IF EXISTS contributors")
    return "Table 'contributors' dropped."


# 3. SINGLE INSERT --------------------------------------------------------
def insert_one(bliss, firstname, lastname, commits):
    """Feature 3: run() with a single tuple of args - one parameterized INSERT."""
    bliss.run(
        "INSERT INTO contributors VALUES (?, ?, ?)",
        (firstname, lastname, commits),
    )
    return f"Inserted {firstname} {lastname}."


# 4. BATCH INSERT (executemany under the hood) ----------------------------
def insert_many(bliss, rows):
    """Feature 4: run() with a list of tuples - batch INSERT (executemany)."""
    bliss.run("INSERT INTO contributors VALUES (?, ?, ?)", rows)
    return f"Inserted {len(rows)} rows in one batch."


# 5. CHAINED run().commit() ------------------------------------------------
def insert_and_commit(bliss, firstname, lastname, commits):
    """Feature 5: run() returns self, so commit() can be chained directly,
    exactly as shown in the package README."""
    bliss.run(
        "INSERT INTO contributors VALUES (?, ?, ?)",
        (firstname, lastname, commits),
    ).commit()
    return f"Inserted and committed {firstname} {lastname} in one chained call."


# 6. COMMIT (explicit) ------------------------------------------------------
def commit(bliss):
    """Feature 6: commit() - shortcut for connection.commit()."""
    bliss.commit()
    return "Transaction committed."


# 7. FETCH ONE ROW ------------------------------------------------------
def fetch_one(bliss, lastname):
    """Feature 7: one() - fetch a single row. Returns a namedtuple since
    the query selects multiple columns."""
    return bliss.one(
        "SELECT firstname, lastname, commits FROM contributors WHERE lastname = ?",
        (lastname,),
    )


# 8. FETCH ALL ROWS -----------------------------------------------------
def fetch_all(bliss):
    """Feature 8: all() - fetch every row, ordered by commits desc."""
    return bliss.all(
        "SELECT firstname, lastname, commits FROM contributors "
        "ORDER BY commits DESC"
    )


# 9. UPDATE ---------------------------------------------------------------
def update_commits(bliss, lastname, new_commits):
    """Feature 9: run() for an UPDATE statement."""
    bliss.run(
        "UPDATE contributors SET commits = ? WHERE lastname = ?",
        (new_commits, lastname),
    )
    return f"Updated commits for {lastname} to {new_commits}."


# 10. DELETE ----------------------------------------------------------------
def delete_contributor(bliss, lastname):
    """Feature 10: run() for a DELETE statement."""
    bliss.run("DELETE FROM contributors WHERE lastname = ?", (lastname,))
    return f"Deleted contributor with lastname {lastname}."


# Bonus / supporting helpers used by the UI (still only via SQL methods) ---
def count_rows(bliss):
    """Uses one() on a single-column aggregate query -> returns a scalar."""
    return bliss.one("SELECT COUNT(*) FROM contributors")


def total_commits(bliss):
    """Uses one() on a single-column aggregate query -> returns a scalar
    (None if the table is empty, matching sql.SQL.one's documented behavior)."""
    return bliss.one("SELECT SUM(commits) FROM contributors")


def list_lastnames(bliss):
    """Uses all() on a single-column query -> returns a plain list of
    scalar values (no namedtuple wrapping, since only 1 column selected)."""
    return bliss.all("SELECT lastname FROM contributors ORDER BY lastname")
