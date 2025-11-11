from datetime import datetime
from typing import List, Dict, Optional

class NotesManager:
    def __init__(self):
        pass
    
    def create_note(self, topic_id: int, title: str, content: str) -> Dict:
        """Create a new study note"""
        return {
            'topic_id': topic_id,
            'title': title,
            'content': content,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
    
    def format_note_for_display(self, note: Dict) -> Dict:
        """Format note for display with metadata"""
        return {
            'id': note.get('id'),
            'topic_id': note.get('topic_id'),
            'title': note.get('title'),
            'content': note.get('content'),
            'preview': note.get('content', '')[:100] + '...' if len(note.get('content', '')) > 100 else note.get('content', ''),
            'created_at': note.get('created_at'),
            'updated_at': note.get('updated_at'),
            'word_count': len(note.get('content', '').split())
        }
    
    def search_notes(self, notes: List[Dict], query: str) -> List[Dict]:
        """Search notes by title or content"""
        query_lower = query.lower()
        results = []
        for note in notes:
            title = note.get('title', '').lower()
            content = note.get('content', '').lower()
            if query_lower in title or query_lower in content:
                results.append(note)
        return results
    
    def get_notes_by_topic(self, notes: List[Dict], topic_id: int) -> List[Dict]:
        """Get all notes for a specific topic"""
        return [note for note in notes if note.get('topic_id') == topic_id]
    
    def get_recent_notes(self, notes: List[Dict], limit: int = 10) -> List[Dict]:
        """Get most recently updated notes"""
        sorted_notes = sorted(notes, key=lambda x: x.get('updated_at', ''), reverse=True)
        return sorted_notes[:limit]

