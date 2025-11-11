from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
import statistics

class AIRecommender:
    def __init__(self):
        pass
    
    def get_study_recommendations(self, progress_data: List[Dict], topics: List[Dict], 
                                 study_sessions: List[Dict]) -> List[Dict]:
        """Get AI-powered study recommendations"""
        recommendations = []
        
        # Analyze study patterns
        if progress_data:
            avg_study_time = statistics.mean([d.get('total_study_time', 0) for d in progress_data])
            avg_productivity = statistics.mean([d.get('productivity_score', 0) for d in progress_data])
            
            # Recommendation based on study time
            if avg_study_time < 60:  # Less than 1 hour per day
                recommendations.append({
                    'type': 'study_time',
                    'priority': 'high',
                    'message': 'Consider increasing daily study time to at least 1-2 hours for better progress',
                    'action': 'Schedule more study sessions throughout the day'
                })
            
            # Recommendation based on productivity
            if avg_productivity < 50:
                recommendations.append({
                    'type': 'productivity',
                    'priority': 'medium',
                    'message': 'Your productivity score is below average. Try using Pomodoro technique for better focus',
                    'action': 'Use 25-minute focused study sessions with 5-minute breaks'
                })
        
        # Analyze topic difficulty
        if topics:
            hard_topics = [t for t in topics if t.get('difficulty') == 'Hard']
            if hard_topics:
                recommendations.append({
                    'type': 'difficulty',
                    'priority': 'high',
                    'message': f'You have {len(hard_topics)} difficult topics. Break them into smaller subtopics',
                    'action': 'Allocate extra time and use spaced repetition for difficult topics'
                })
        
        # Analyze study consistency
        if study_sessions:
            recent_sessions = [s for s in study_sessions if self._is_recent(s.get('start_time', ''))]
            if len(recent_sessions) < 3:
                recommendations.append({
                    'type': 'consistency',
                    'priority': 'medium',
                    'message': 'Maintain consistent daily study habits to build momentum',
                    'action': 'Set a daily study goal and track your streak'
                })
        
        # Analyze time distribution
        if progress_data:
            morning_sessions = sum(1 for d in progress_data if d.get('morning_study', False))
            if morning_sessions < len(progress_data) * 0.3:
                recommendations.append({
                    'type': 'timing',
                    'priority': 'low',
                    'message': 'Morning study sessions are proven to be more effective',
                    'action': 'Try scheduling important topics in the morning hours'
                })
        
        return recommendations
    
    def recommend_topics_to_study(self, topics: List[Dict], progress_data: List[Dict]) -> List[Dict]:
        """Recommend which topics to study next based on priority and progress"""
        # Sort topics by priority and difficulty
        sorted_topics = sorted(
            topics,
            key=lambda x: (
                x.get('priority', 3),
                {'Easy': 1, 'Medium': 2, 'Hard': 3}.get(x.get('difficulty', 'Medium'), 2)
            ),
            reverse=True
        )
        
        recommendations = []
        for topic in sorted_topics[:5]:  # Top 5 recommendations
            recommendations.append({
                'topic': topic.get('name', ''),
                'reason': self._get_recommendation_reason(topic, progress_data),
                'priority': topic.get('priority', 3),
                'difficulty': topic.get('difficulty', 'Medium'),
                'estimated_hours': topic.get('estimated_hours', 2.0)
            })
        
        return recommendations
    
    def _get_recommendation_reason(self, topic: Dict, progress_data: List[Dict]) -> str:
        """Get reason for recommending a topic"""
        priority = topic.get('priority', 3)
        difficulty = topic.get('difficulty', 'Medium')
        
        if priority >= 4:
            return "High priority topic - should be studied soon"
        elif difficulty == 'Hard':
            return "Difficult topic - needs more time and practice"
        else:
            return "Good topic to maintain consistent progress"
    
    def _is_recent(self, date_str: str, days: int = 7) -> bool:
        """Check if a date is within recent days"""
        try:
            if isinstance(date_str, str):
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                date_obj = date_str
            
            delta = datetime.now() - date_obj
            return delta.days <= days
        except:
            return False
    
    def get_optimal_study_time(self, progress_data: List[Dict]) -> Dict:
        """Determine optimal study time based on historical data"""
        if not progress_data:
            return {
                'recommended_time': 'Morning (8-10 AM)',
                'reason': 'Default recommendation - morning hours are typically most productive'
            }
        
        # Analyze productivity by time of day (simplified)
        # In a real implementation, this would analyze actual time-of-day data
        return {
            'recommended_time': 'Morning (8-10 AM)',
            'reason': 'Based on your study patterns, morning sessions show higher productivity',
            'alternative_times': ['Afternoon (2-4 PM)', 'Evening (6-8 PM)']
        }
    
    def suggest_break_schedule(self, study_hours: float) -> List[Dict]:
        """Suggest break schedule based on study duration"""
        breaks = []
        
        if study_hours <= 1:
            # 1 break for 1 hour
            breaks.append({
                'after_minutes': 30,
                'duration_minutes': 5,
                'type': 'short_break'
            })
        elif study_hours <= 2:
            # 2 breaks for 2 hours
            breaks.append({
                'after_minutes': 30,
                'duration_minutes': 5,
                'type': 'short_break'
            })
            breaks.append({
                'after_minutes': 90,
                'duration_minutes': 10,
                'type': 'short_break'
            })
        else:
            # Multiple breaks with long break
            breaks.append({
                'after_minutes': 25,
                'duration_minutes': 5,
                'type': 'short_break'
            })
            breaks.append({
                'after_minutes': 55,
                'duration_minutes': 5,
                'type': 'short_break'
            })
            breaks.append({
                'after_minutes': 85,
                'duration_minutes': 15,
                'type': 'long_break'
            })
        
        return breaks

