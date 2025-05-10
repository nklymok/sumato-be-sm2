#!/usr/bin/env python3
"""
Import kanji from an Anki .apkg file into a Postgres database
without using psycopg2 (uses the pure-Python pg8000 driver).

Usage:
    pip install pg8000
    python import_kanji_no_psycopg2.py --apkg /path/to/file.apkg --db-url postgresql://user:pass@host:port/dbname
"""
import argparse
import zipfile
import tempfile
import os
import sqlite3
from urllib.parse import urlparse
import pg8000


def main():
    # Parse the DB URL
    url = urlparse('<DB_URL>>')
    user = url.username
    password = url.password
    host = url.hostname
    port = url.port or 5432
    database = url.path.lstrip("/")

    # Extract the Anki SQLite database
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile('All_in_One_Kanji_Deck_Heisigs_RTK_Order_6th_edition.apkg', "r") as zf:
            zf.extract("collection.anki2", tmpdir)
        sqlite_path = os.path.join(tmpdir, "collection.anki2")
        sqconn = sqlite3.connect(sqlite_path)
        sqcur = sqconn.cursor()
        sqcur.execute("SELECT flds FROM notes")
        notes = sqcur.fetchall()
        sqconn.close()

    # Connect to Postgres via pg8000
    conn = pg8000.connect(
        user=user,
        password=password,
        host=host,
        port=port,
        database=database
    )
    cur = conn.cursor()

    # Insert into sumato_kanji, returning the new id
    insert_kanji_sql = """
    INSERT INTO sumato_kanji
      (value, onyomi, kunyomi, meaning, koohii_story, frequency, grade)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    RETURNING id
    """

    # Prepare insert for examples
    insert_example_sql = """
    INSERT INTO sumato_kanji_example (kanji_id, example)
    VALUES (%s, %s)
    """

    for (flds,) in notes:
        fields = flds.split("\x1f")
        value = fields[0].strip() if len(fields) > 0 else None
        onyomi = fields[1].strip() if len(fields) > 1 else None
        kunyomi = fields[2].strip() if len(fields) > 2 else None
        meaning = fields[4].strip() if len(fields) > 4 else None

        # Koohii stories may be in fields 18 & 19
        story1 = fields[18].strip() if len(fields) > 18 else ""
        story2 = fields[19].strip() if len(fields) > 19 else ""
        koohii_story = "\n\n".join([s for s in (story1, story2) if s]) or None

        # Frequency at field 8
        try:
            frequency = int(fields[8]) if len(fields) > 8 and fields[8].strip() else None
        except ValueError:
            frequency = None

        # Grade at field 7
        grade = fields[7].strip() if len(fields) > 7 else None

        # Insert the kanji row and get its new ID
        cur.execute(insert_kanji_sql, (
            value, onyomi, kunyomi,
            meaning, koohii_story,
            frequency, grade
        ))
        kanji_id = cur.fetchone()[0]

        # Parse and insert examples (field 5)
        examples_field = fields[5] if len(fields) > 5 else ""
        examples = [
            ex.strip()
            for ex in examples_field.split("<br>")
            if ex.strip()
        ]
        for example in examples:
            cur.execute(insert_example_sql, (kanji_id, example))

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()

