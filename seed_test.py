import sqlite3
import json
import os

DB_PATH = '/home/benjaminkahr/School/Zeugnise/PyGrade/pygrade.db'

test_data = {
    "subjects": {
        "Module 117": {"grade": 5.5, "category": "berufskunde"},
        "Module 122": {"grade": 4.8, "category": "berufskunde"},
        "Language A": {"grade": 5.0, "category": "allgemeinbildung"},
        "Semester 1 Math": {"grade": 4.5, "category": "erfahrungsnote"},
        "IPA Project": {"grade": 6.0, "category": "ipa"}
    }
}

def seed():
    conn = sqlite3.connect(DB_PATH)
    # This assumes your user_id is 1. If you just registered, it likely is.
    user_id = 1 
    data_json = json.dumps(test_data)
    
    conn.execute('''
        INSERT INTO user_data (user_id, data_json) 
        VALUES (?, ?) 
        ON CONFLICT(user_id) DO UPDATE SET data_json=excluded.data_json
    ''', (user_id, data_json))
    conn.commit()
    conn.close()
    print("Local database seeded with BiVo test data!")

if __name__ == "__main__":
    seed()