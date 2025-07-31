logging_db
import sqlite3
from datetime import datetime
import json
# --- 1. Database Setup (Utility Function) ---
def setup_database(db_name='routing_logs.db'):
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS logs (
log_id TEXT PRIMARY KEY,
timestamp TEXT NOT NULL,
sender_id TEXT NOT NULL,
routed_agents TEXT, -- Stored as JSON string
response TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT NOT NULL,
price REAL NOT NULL,
stock INTEGER DEFAULT 0
)
''')

conn.commit()
return conn, cursor

def insert_log_entry(cursor, conn, data):
# Prepare data for insertion based on the dictionary structure
timestamp = data.get('timestamp') # Use existing or current UTC time
sender_id = data.get('sender_id')
log_id = data.get('log_id', f"{sender_id}:{timestamp}") # Generate log_id if not provided

routed_agents_json = json.dumps(data.get('routed_agents', [])) # Convert list to JSON string
response = data.get('response')

if not sender_id or not response:
print("Error: 'sender_id' and 'response' are required for a log entry.")
return

try:
cursor.execute('''
INSERT INTO logs (log_id, timestamp, sender_id, routed_agents, response)
VALUES (?, ?, ?, ?, ?)
''', (log_id, timestamp, sender_id, routed_agents_json, response))
conn.commit()
print(f"Log entry with log_id '{log_id}' inserted successfully.")
except sqlite3.IntegrityError as e:
print(f"Error inserting log entry (log_id: {log_id}): {e}")
except Exception as e:
print(f"An unexpected error occurred: {e}")

def get_logs_by_sender_id(cursor, sender_id):
"""
Retrieves all log entries for a given sender_id,
reconstructing them into Python dictionaries.
"""
results = []
try:
cursor.execute("SELECT log_id, timestamp, sender_id, routed_agents, response FROM logs WHERE sender_id = ?", (sender_id,))
rows = cursor.fetchall() # Fetch all matching rows

for row in rows:
retrieved_log_id, retrieved_timestamp, retrieved_sender_id, \
retrieved_routed_agents_json, retrieved_response = row

# Reconstruct the dictionary for each row
reconstructed_dict = {
'sender_id': retrieved_sender_id,
'timestamp': retrieved_timestamp,
'routed_agents': json.loads(retrieved_routed_agents_json), # Convert JSON string back to list
'response': retrieved_response,
'log_id': retrieved_log_id
}
results.append(reconstructed_dict)

except Exception as e:
print(f"Error retrieving logs for sender_id '{sender_id}': {e}")
return results
