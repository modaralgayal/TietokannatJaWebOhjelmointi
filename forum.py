import datetime

import db


def get_threads():
    sql_command = """
        SELECT t.id, t.title, COUNT(m.id) AS total, MAX(m.sent_at) AS last
        FROM threads t
        LEFT JOIN messages m ON t.id = m.thread_id
        GROUP BY t.id
        ORDER BY t.id DESC
    """
    threads = db.query(sql_command)
    return threads


def create_thread(title, user_id):
    sql_command = "INSERT INTO threads (title, user_id) VALUES (?, ?)"
    db.execute(sql_command, [title, user_id])


def add_thread(title, content, user_id):
    sql = "INSERT INTO threads (title, user_id) VALUES (?, ?)"
    db.execute(sql, [title, user_id])
    thread_id = db.last_insert_id()
    add_message(content, user_id, thread_id)
    return thread_id


def add_message(content, user_id, thread_id):
    sql = """INSERT INTO messages (content, sent_at, user_id, thread_id)
             VALUES (?, datetime('now'), ?, ?)"""
    db.execute(sql, [content, user_id, thread_id])


def get_thread(thread_id):
    sql = "SELECT id, title FROM threads WHERE id = ?"
    result = db.query(sql, [thread_id])
    return result[0] if result else None


def get_messages(thread_id):
    sql = """ SELECT m.id, m.content, m.sent_at, m.user_id, u.username
    FROM messages m, users u
    WHERE m.user_id = u.id AND m.thread_id = ?
    ORDER BY m.id"""

    return db.query(sql, [thread_id])


def get_message(message_id):
    sql = "SELECT id, content, sent_at, thread_id FROM messages WHERE id = ?"
    message = db.query(sql, [message_id])[0]
    if message:
        return message
    else:
        return None


def update_message(message_id, content):
    sql = "UPDATE messages SET content = ? WHERE id = ?"
    db.execute(sql, [content, message_id])


def remove_message(message_id):
    sql = "DELETE FROM messages WHERE id = ?"
    db.execute(sql, [message_id])


def remove_thread(thread_id):
    try:
        print("Deleting thread: ", thread_id)
        sql = "DELETE FROM threads WHERE id = ?"
        db.execute(sql, [int(thread_id)])
    except:
        return "Cannot delete threads with messages in them", 401


def search(query):
    sql = """SELECT m.id message_id,
                    m.thread_id,
                    t.title thread_title,
                    m.sent_at,
                    u.username
             FROM threads t, messages m, users u
             WHERE t.id = m.thread_id AND
                   u.id = m.user_id AND
                   m.content LIKE ?
             ORDER BY m.sent_at DESC"""
    return db.query(sql, ["%" + query + "%"])
