# read kanji.csv and parse it (it's tab separated)

import csv
import json

import psycopg2 as psycopg2


def parse_kanji():
    kanji = []
    with open('kanji.csv', 'r') as csvfile:
        # kanji, onyomi, kunyomi, nanori (skip), meaning, examples (delimited by newline), then skip all until the pre-last one, which is a koohii story.
        kanji_reader = csv.reader(csvfile, delimiter='\t')
        for row in kanji_reader:
            try:
                if len(row[7]) > 0:
                    kanji.append({
                        'kanji': row[0],
                        'onyomi': row[1],
                        'kunyomi': row[2],
                        'meaning': row[4],
                        'examples': list(filter(lambda example: len(example.strip()) > 0, row[5].split('<br>'))),
                        'story': row[-2],
                        'grade': row[7],
                        'frequency': int(row[8]),
                    })
            except:
                continue
    return kanji

kanji = parse_kanji()
# save the kanji into a postgresdb:
# table sumato_kanji: insert value, onyomi, kunyomi, English, koohii story, frequency, grade
# table sumato_kanji_example: insert kanji_id (from previous insert), all examples for examples array

db_url = 'postgresql://postgres:postgres@localhost:5432/sumato'

try:
    connection = psycopg2.connect(db_url)
    cursor = connection.cursor()
    for k in kanji:
        # Insert data into sumato_kanji table
        cursor.execute('''
            INSERT INTO sumato_kanji (value, onyomi, kunyomi, meaning, koohii_story, grade, frequency)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (k['kanji'], k['onyomi'], k['kunyomi'], k['meaning'], k['story'], k['grade'], k['frequency']))
        # Get the last inserted kanji_id
        cursor.execute('SELECT LASTVAL()')
        kanji_id = cursor.fetchone()[0]
        # Insert examples into sumato_kanji_example table
        for example in k['examples']:
            cursor.execute('''
                INSERT INTO sumato_kanji_example (kanji_id, example)
                VALUES (%s, %s)
            ''', (kanji_id, example))
    connection.commit()
    print("Data inserted successfully.")
except Exception as error:
    print("Error while inserting data into PostgreSQL", error)
finally:
    if connection:
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed.")