from datetime import datetime, date, timedelta
from typing import List, Dict, Optional

class GoalManager:
    def __init__(self):
        pass
    
    def create_goal(self, title: str, description: str, target_date: date, target_hours: float = 0.0) -> Dict:
        """Create a new study goal"""
        return {
            'title': title,
            'description': description,
            'target_date': target_date.isoformat(),
            'target_hours': target_hours,
            'current_progress': 0.0,
            'status': 'active',
            'created_at': datetime.now().isoformat()
        }
    
    def update_goal_progress(self, goal: Dict, hours_studied: float) -> Dict:
        """Update goal progress"""
        current_progress = goal.get('current_progress', 0.0) + hours_studied
        target_hours = goal.get('target_hours', 0.0)
        
        progress_percentage = (current_progress / target_hours * 100) if target_hours > 0 else 0
        
        goal['current_progress'] = current_progress
        goal['progress_percentage'] = min(100, progress_percentage)
        
        # Check if goal is completed
        if target_hours > 0 and current_progress >= target_hours:
            goal['status'] = 'completed'
        
        return goal
    
    def calculate_days_remaining(self, target_date: date) -> int:
        """Calculate days remaining until target date"""
        today = date.today()
        delta = target_date - today
        return max(0, delta.days)
    
    def get_goal_status(self, goal: Dict) -> Dict:
        """Get detailed status of a goal"""
        target_date = datetime.fromisoformat(goal['target_date']).date() if isinstance(goal['target_date'], str) else goal['target_date']
        days_remaining = self.calculate_days_remaining(target_date)
        target_hours = goal.get('target_hours', 0.0)
        current_progress = goal.get('current_progress', 0.0)
        
        progress_percentage = (current_progress / target_hours * 100) if target_hours > 0 else 0
        hours_per_day = (target_hours - current_progress) / days_remaining if days_remaining > 0 else 0
        
        return {
            'goal': goal,
            'days_remaining': days_remaining,
            'progress_percentage': progress_percentage,
            'hours_per_day_needed': hours_per_day,
            'is_on_track': hours_per_day <= (target_hours / 30) if days_remaining > 0 else False,
            'status': goal.get('status', 'active')
        }
    
    def get_active_goals(self, goals: List[Dict]) -> List[Dict]:
        """Get all active goals"""
        return [goal for goal in goals if goal.get('status') == 'active']
    
    def get_completed_goals(self, goals: List[Dict]) -> List[Dict]:
        """Get all completed goals"""
        return [goal for goal in goals if goal.get('status') == 'completed']

