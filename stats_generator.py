import csv
import json
import random
from datetime import datetime, timedelta
import psycopg2

db_url = 'postgresql://postgres:postgres@localhost:5432/sumato'
connection = psycopg2.connect(db_url)
cursor = connection.cursor()

def random_timestamp(start, end):
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return start + timedelta(seconds=random_second)

# Define the minimum and maximum dates for the reviewed_at and next_review_at columns
min_date = datetime(2024, 1, 1, 0, 0, 0)
max_date = datetime(2024, 4, 28, 23, 59, 59)
min_next_date = datetime(2024, 1, 1, 0, 0, 0)
max_next_date = datetime(2024, 12, 31, 23, 59, 59)

# Loop through kanji_ids from 1 to 800
for kanji_id in range(1, 1001):
    # Set is_first_review to True for the first occurrence of each kanji_id
    is_first_review = True

    # Generate random reviewed_at timestamp
    reviewed_at = random_timestamp(min_date, max_date)

    # Generate next_review_at timestamp
    # 75% chance of next_review_at being less than 21 days in the future
    if random.random() < 0.75:
        next_review_at = reviewed_at + timedelta(days=random.randint(1, 20))
    else:
        next_review_at = random_timestamp(min_next_date, max_next_date)

    # Insert data into the table
    query = """
        INSERT INTO sumato_user_kanji_review (user_id, kanji_id, is_first_review, reviewed_at, next_review_at, dango_earned)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    dango_earned = random.randint(1, 2)
    cursor.execute(query, (11, kanji_id, is_first_review, reviewed_at, next_review_at, dango_earned))

    # Set is_first_review to False for subsequent occurrences of the same kanji_id
    is_first_review = False

# Commit the changes and close the database connection
connection.commit()
connection.close()