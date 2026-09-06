import sys
sys.path.append('.')
from app.database.mongodb import db
from collections import Counter

docs = list(db.verification_collection.find())

total = len(docs)
labels = Counter(d.get('label') for d in docs)
sources = Counter(d.get('source') for d in docs)

real_human = sum(1 for d in docs if d.get('label') == 'human' and 'synthetic' not in str(d.get('source', '')))
real_bot = sum(1 for d in docs if d.get('label') == 'bot' and 'synthetic' not in str(d.get('source', '')))
synthetic = total - real_human - real_bot

has_session_id = all('session_id' in d for d in docs)
has_participant = any('participant_id' in d for d in docs)
has_collection_run = any('collection_run' in d for d in docs)

print(f"Total sessions: {total}")
print(f"Human labels: {labels.get('human', 0)}")
print(f"Bot labels: {labels.get('bot', 0)}")
print(f"Synthetic sessions: {synthetic}")
print(f"Real human sessions: {real_human}")
print(f"Real bot sessions: {real_bot}")
print(f"Sources: {dict(sources)}")
print(f"Session IDs present: {has_session_id}")
print(f"Participant ID present: {has_participant}")
print(f"Collection Run present: {has_collection_run}")
