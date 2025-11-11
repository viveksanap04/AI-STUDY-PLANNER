from datetime import datetime, date, timedelta
from typing import List, Dict, Optional

class DeadlineManager:
    def __init__(self):
        self.priority_levels = {
            'Low': 1,
            'Medium': 2,
            'High': 3,
            'Critical': 4
        }
    
    def create_deadline(self, title: str, description: str, deadline_date: datetime, priority: str = 'Medium') -> Dict:
        """Create a new deadline"""
        return {
            'title': title,
            'description': description,
            'deadline_date': deadline_date.isoformat(),
            'priority': priority,
            'is_completed': False,
            'created_at': datetime.now().isoformat()
        }
    
    def get_days_until_deadline(self, deadline_date: datetime) -> int:
        """Calculate days until deadline"""
        today = datetime.now()
        delta = deadline_date - today
        return delta.days
    
    def get_deadline_status(self, deadline: Dict) -> Dict:
        """Get detailed status of a deadline"""
        deadline_date = datetime.fromisoformat(deadline['deadline_date']) if isinstance(deadline['deadline_date'], str) else deadline['deadline_date']
        days_remaining = self.get_days_until_deadline(deadline_date)
        priority = deadline.get('priority', 'Medium')
        
        # Determine urgency
        if days_remaining < 0:
            urgency = 'overdue'
        elif days_remaining <= 1:
            urgency = 'critical'
        elif days_remaining <= 3:
            urgency = 'urgent'
        elif days_remaining <= 7:
            urgency = 'soon'
        else:
            urgency = 'upcoming'
        
        return {
            'deadline': deadline,
            'days_remaining': days_remaining,
            'urgency': urgency,
            'priority': priority,
            'is_overdue': days_remaining < 0,
            'is_completed': deadline.get('is_completed', False)
        }
    
    def get_upcoming_deadlines(self, deadlines: List[Dict], days: int = 7) -> List[Dict]:
        """Get deadlines within specified days"""
        upcoming = []
        cutoff_date = datetime.now() + timedelta(days=days)
        
        for deadline in deadlines:
            if deadline.get('is_completed', False):
                continue
            
            deadline_date = datetime.fromisoformat(deadline['deadline_date']) if isinstance(deadline['deadline_date'], str) else deadline['deadline_date']
            if deadline_date <= cutoff_date:
                upcoming.append(deadline)
        
        # Sort by deadline date
        upcoming.sort(key=lambda x: datetime.fromisoformat(x['deadline_date']) if isinstance(x['deadline_date'], str) else x['deadline_date'])
        return upcoming
    
    def get_overdue_deadlines(self, deadlines: List[Dict]) -> List[Dict]:
        """Get all overdue deadlines"""
        overdue = []
        now = datetime.now()
        
        for deadline in deadlines:
            if deadline.get('is_completed', False):
                continue
            
            deadline_date = datetime.fromisoformat(deadline['deadline_date']) if isinstance(deadline['deadline_date'], str) else deadline['deadline_date']
            if deadline_date < now:
                overdue.append(deadline)
        
        return overdue
    
    def sort_by_priority(self, deadlines: List[Dict]) -> List[Dict]:
        """Sort deadlines by priority"""
        return sorted(
            deadlines,
            key=lambda x: self.priority_levels.get(x.get('priority', 'Medium'), 2),
            reverse=True
        )

