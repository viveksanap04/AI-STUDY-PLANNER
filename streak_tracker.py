from datetime import datetime, date, timedelta
from typing import Dict, Optional, List

class StreakTracker:
    def __init__(self):
        pass
    
    def update_streak(self, streak_data: Dict, study_date: date = None) -> Dict:
        """Update study streak based on study activity"""
        if study_date is None:
            study_date = date.today()
        
        last_study_date = streak_data.get('last_study_date')
        current_streak = streak_data.get('current_streak', 0)
        longest_streak = streak_data.get('longest_streak', 0)
        total_study_days = streak_data.get('total_study_days', 0)
        
        # Convert string to date if needed
        if isinstance(last_study_date, str):
            last_study_date = datetime.fromisoformat(last_study_date).date()
        
        if last_study_date is None:
            # First study session
            current_streak = 1
            total_study_days = 1
        elif last_study_date == study_date:
            # Same day, don't update streak
            pass
        elif last_study_date == study_date - timedelta(days=1):
            # Consecutive day
            current_streak += 1
            total_study_days += 1
        else:
            # Streak broken
            if current_streak > longest_streak:
                longest_streak = current_streak
            current_streak = 1
            total_study_days += 1
        
        # Update longest streak if current is longer
        if current_streak > longest_streak:
            longest_streak = current_streak
        
        return {
            'current_streak': current_streak,
            'longest_streak': longest_streak,
            'last_study_date': study_date.isoformat(),
            'total_study_days': total_study_days,
            'updated_at': datetime.now().isoformat()
        }
    
    def get_streak_info(self, streak_data: Dict) -> Dict:
        """Get detailed streak information"""
        current_streak = streak_data.get('current_streak', 0)
        longest_streak = streak_data.get('longest_streak', 0)
        last_study_date = streak_data.get('last_study_date')
        
        if isinstance(last_study_date, str):
            last_study_date = datetime.fromisoformat(last_study_date).date()
        
        days_since_last_study = None
        if last_study_date:
            days_since_last_study = (date.today() - last_study_date).days
        
        # Determine streak status
        if current_streak == 0:
            status = 'no_streak'
        elif current_streak < 7:
            status = 'beginner'
        elif current_streak < 30:
            status = 'consistent'
        elif current_streak < 100:
            status = 'dedicated'
        else:
            status = 'legendary'
        
        return {
            'current_streak': current_streak,
            'longest_streak': longest_streak,
            'total_study_days': streak_data.get('total_study_days', 0),
            'days_since_last_study': days_since_last_study,
            'status': status,
            'is_active': days_since_last_study == 0 if days_since_last_study is not None else False
        }
    
    def get_milestones(self, streak_data: Dict) -> List[Dict]:
        """Get upcoming streak milestones"""
        current_streak = streak_data.get('current_streak', 0)
        milestones = [
            {'days': 7, 'name': 'Week Warrior', 'achieved': current_streak >= 7},
            {'days': 14, 'name': 'Two Week Champion', 'achieved': current_streak >= 14},
            {'days': 30, 'name': 'Monthly Master', 'achieved': current_streak >= 30},
            {'days': 50, 'name': 'Half Century', 'achieved': current_streak >= 50},
            {'days': 100, 'name': 'Century Club', 'achieved': current_streak >= 100},
            {'days': 365, 'name': 'Year Warrior', 'achieved': current_streak >= 365}
        ]
        
        # Filter to show next unachieved milestone
        upcoming = [m for m in milestones if not m['achieved'] and m['days'] > current_streak]
        return upcoming[:3]  # Return next 3 milestones

