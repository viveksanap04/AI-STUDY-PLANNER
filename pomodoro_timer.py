from datetime import datetime, timedelta
from typing import Dict, Optional

class PomodoroTimer:
    def __init__(self):
        self.default_work_duration = 25  # minutes
        self.default_break_duration = 5  # minutes
        self.default_long_break = 15  # minutes
        self.pomodoros_before_long_break = 4
        
    def start_session(self, work_duration: int = None, break_duration: int = None) -> Dict:
        """Start a Pomodoro study session"""
        work_duration = work_duration or self.default_work_duration
        break_duration = break_duration or self.default_break_duration
        
        return {
            'session_type': 'work',
            'duration_minutes': work_duration,
            'start_time': datetime.now().isoformat(),
            'end_time': (datetime.now() + timedelta(minutes=work_duration)).isoformat(),
            'break_duration': break_duration,
            'status': 'active'
        }
    
    def start_break(self, break_duration: int = None, is_long_break: bool = False) -> Dict:
        """Start a break session"""
        if is_long_break:
            break_duration = self.default_long_break
        else:
            break_duration = break_duration or self.default_break_duration
        
        return {
            'session_type': 'break',
            'duration_minutes': break_duration,
            'start_time': datetime.now().isoformat(),
            'end_time': (datetime.now() + timedelta(minutes=break_duration)).isoformat(),
            'is_long_break': is_long_break,
            'status': 'active'
        }
    
    def get_session_stats(self, completed_sessions: int) -> Dict:
        """Get statistics for completed Pomodoro sessions"""
        total_work_time = completed_sessions * self.default_work_duration
        total_breaks = completed_sessions // self.pomodoros_before_long_break
        short_breaks = completed_sessions - total_breaks
        total_break_time = (short_breaks * self.default_break_duration) + (total_breaks * self.default_long_break)
        
        return {
            'completed_sessions': completed_sessions,
            'total_work_minutes': total_work_time,
            'total_break_minutes': total_break_time,
            'total_time_minutes': total_work_time + total_break_time,
            'next_long_break': (completed_sessions + 1) % self.pomodoros_before_long_break == 0
        }
    
    def calculate_productivity_score(self, completed_sessions: int, distractions: int = 0) -> float:
        """Calculate productivity score based on completed sessions and distractions"""
        base_score = min(completed_sessions * 20, 100)
        distraction_penalty = distractions * 5
        return max(0, base_score - distraction_penalty)

