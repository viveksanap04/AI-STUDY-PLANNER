import re
from typing import List, Dict
from datetime import datetime

class FlashcardGenerator:
    def __init__(self):
        self.question_patterns = [
            "What is {topic}?",
            "Explain {topic}",
            "Define {topic}",
            "Describe {topic}",
            "What are the key concepts of {topic}?",
            "How does {topic} work?",
            "What is the importance of {topic}?",
            "List the main features of {topic}"
        ]
    
    def generate_flashcards_from_topic(self, topic_name: str, topic_content: str = None, count: int = 5) -> List[Dict]:
        """Generate flashcards from a topic"""
        flashcards = []
        
        # Generate basic flashcards
        for i in range(min(count, len(self.question_patterns))):
            question = self.question_patterns[i].format(topic=topic_name)
            answer = self._generate_answer(topic_name, topic_content)
            
            flashcards.append({
                'question': question,
                'answer': answer,
                'topic_name': topic_name,
                'difficulty': 'Medium',
                'created_at': datetime.now().isoformat()
            })
        
        return flashcards
    
    def _generate_answer(self, topic_name: str, content: str = None) -> str:
        """Generate an answer for a flashcard"""
        if content:
            # Extract key points from content
            sentences = content.split('.')[:3]
            answer = '. '.join(sentences).strip()
            if answer:
                return answer
        
        # Default answer
        return f"{topic_name} is an important concept that requires understanding of its fundamental principles and applications."
    
    def generate_flashcards_from_text(self, text: str, topic_name: str) -> List[Dict]:
        """Generate flashcards from text content"""
        flashcards = []
        
        # Extract key sentences
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
        
        for i, sentence in enumerate(sentences[:5]):
            # Create question-answer pair
            question = f"What is mentioned about {topic_name} in this context?"
            flashcards.append({
                'question': question,
                'answer': sentence,
                'topic_name': topic_name,
                'difficulty': 'Medium',
                'created_at': datetime.now().isoformat()
            })
        
        return flashcards
    
    def update_mastery_level(self, flashcard: Dict, was_correct: bool) -> float:
        """Update mastery level based on study result"""
        current_mastery = flashcard.get('mastery_level', 0.0)
        times_studied = flashcard.get('times_studied', 0) + 1
        
        if was_correct:
            # Increase mastery
            mastery_increase = 0.1 * (1 - current_mastery)
            new_mastery = min(1.0, current_mastery + mastery_increase)
        else:
            # Decrease mastery slightly
            mastery_decrease = 0.05
            new_mastery = max(0.0, current_mastery - mastery_decrease)
        
        return new_mastery
    
    def get_study_queue(self, flashcards: List[Dict], limit: int = 10) -> List[Dict]:
        """Get flashcards that need to be studied (low mastery or not studied recently)"""
        # Sort by mastery level (lowest first) and last studied date
        sorted_cards = sorted(
            flashcards,
            key=lambda x: (
                x.get('mastery_level', 0.0),
                x.get('last_studied', datetime.min) if x.get('last_studied') else datetime.min
            )
        )
        return sorted_cards[:limit]

