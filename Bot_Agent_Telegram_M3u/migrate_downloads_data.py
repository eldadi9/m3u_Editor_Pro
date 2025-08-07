import sqlite3

def migrate_downloads_table():
    # התחברות לקבצים
    source_conn = sqlite3.connect("downloads_group.db")
    dest_conn = sqlite3.connect("downloads.db")

    source_cursor = source_conn.cursor()
    dest_cursor = dest_conn.cursor()

    # שלוף את כל הנתונים מהטבלה downloads בקובץ הישן
    try:
        source_cursor.execute("SELECT * FROM downloads")
        rows = source_cursor.fetchall()
    except sqlite3.Error as e:
        print(f"❌ שגיאה בשליפת נתונים מהטבלה downloads בקובץ הישן: {e}")
        return

    if not rows:
        print("ℹ️ אין נתונים להעביר.")
        return

    # הוסף את הנתונים לטבלה downloads בקובץ החדש
    try:
        dest_cursor.executemany("""
            INSERT INTO downloads (
                download_id, file_name, downloader_id, username,
                first_name, last_name, download_time, source,
                chat_id, topic_name, device_type, platform, version,
                notes, file_size
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, rows)
        dest_conn.commit()
        print(f"✅ הועתקו {len(rows)} שורות לטבלה downloads בקובץ downloads.db")
    except sqlite3.Error as e:
        print(f"❌ שגיאה בהעתקה למסד החדש: {e}")
    finally:
        source_conn.close()
        dest_conn.close()

if __name__ == "__main__":
    migrate_downloads_table()
