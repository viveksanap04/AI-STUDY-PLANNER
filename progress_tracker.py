from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
import json
import statistics

class ProgressTracker:
    def __init__(self):
        self.analytics_cache = {}
        
    def track_study_session(self, user_id: int, topic_id: int, start_time: datetime, 
                          end_time: Optional[datetime] = None, progress_percentage: float = 0.0,
                          notes: str = "") -> Dict:
        """Track a study session"""
        session_data = {
            'user_id': user_id,
            'topic_id': topic_id,
            'start_time': start_time,
            'end_time': end_time,
            'progress_percentage': progress_percentage,
            'notes': notes,
            'status': 'completed' if end_time else 'in_progress'
        }
        
        if end_time:
            duration = end_time - start_time
            session_data['duration_minutes'] = int(duration.total_seconds() / 60)
            session_data['status'] = 'completed'
        else:
            session_data['status'] = 'in_progress'
        
        return session_data
    
    def calculate_daily_progress(self, user_id: int, target_date: date, 
                               study_sessions: List[Dict]) -> Dict:
        """Calculate daily progress analytics"""
        daily_data = {
            'date': target_date.isoformat(),
            'total_study_time': 0,
            'topics_completed': 0,
            'topics_in_progress': 0,
            'productivity_score': 0.0,
            'focus_time': 0,
            'break_time': 0,
            'session_count': len(study_sessions),
            'average_session_length': 0,
            'topics_by_category': {},
            'difficulty_distribution': {'Easy': 0, 'Medium': 0, 'Hard': 0}
        }
        
        if not study_sessions:
            return daily_data
        
        session_lengths = []
        
        for session in study_sessions:
            # Total study time
            if session.get('duration_minutes'):
                daily_data['total_study_time'] += session['duration_minutes']
                session_lengths.append(session['duration_minutes'])
            
            # Topics completed/in progress
            if session.get('status') == 'completed':
                daily_data['topics_completed'] += 1
            elif session.get('status') == 'in_progress':
                daily_data['topics_in_progress'] += 1
            
            # Focus time (sessions longer than 25 minutes)
            if session.get('duration_minutes', 0) >= 25:
                daily_data['focus_time'] += session['duration_minutes']
        
        # Calculate averages
        if session_lengths:
            daily_data['average_session_length'] = statistics.mean(session_lengths)
        
        # Calculate productivity score
        daily_data['productivity_score'] = self._calculate_productivity_score(daily_data)
        
        return daily_data
    
    def calculate_weekly_progress(self, user_id: int, week_start: date, 
                                daily_progress: List[Dict]) -> Dict:
        """Calculate weekly progress analytics"""
        weekly_data = {
            'week_start': week_start.isoformat(),
            'week_end': (week_start + timedelta(days=6)).isoformat(),
            'total_study_hours': 0,
            'average_daily_study_time': 0,
            'total_topics_completed': 0,
            'total_topics_in_progress': 0,
            'average_productivity_score': 0.0,
            'study_streak_days': 0,
            'most_productive_day': None,
            'least_productive_day': None,
            'progress_trend': 'stable',
            'recommendations': []
        }
        
        if not daily_progress:
            return weekly_data
        
        study_times = []
        productivity_scores = []
        study_days = 0
        
        for day_data in daily_progress:
            study_time = day_data['total_study_time']
            weekly_data['total_study_hours'] += study_time / 60
            weekly_data['total_topics_completed'] += day_data['topics_completed']
            weekly_data['total_topics_in_progress'] += day_data['topics_in_progress']
            
            study_times.append(study_time)
            productivity_scores.append(day_data['productivity_score'])
            
            if study_time > 0:
                study_days += 1
        
        # Calculate averages
        if study_times:
            weekly_data['average_daily_study_time'] = statistics.mean(study_times) / 60
            weekly_data['average_productivity_score'] = statistics.mean(productivity_scores)
            
            # Find most/least productive days
            max_idx = study_times.index(max(study_times))
            min_idx = study_times.index(min(study_times))
            weekly_data['most_productive_day'] = daily_progress[max_idx]['date']
            weekly_data['least_productive_day'] = daily_progress[min_idx]['date']
        
        # Calculate study streak
        weekly_data['study_streak_days'] = study_days
        
        # Determine progress trend
        weekly_data['progress_trend'] = self._calculate_progress_trend(study_times)
        
        # Generate recommendations
        weekly_data['recommendations'] = self._generate_weekly_recommendations(weekly_data)
        
        return weekly_data
    
    def calculate_monthly_progress(self, user_id: int, month: int, year: int,
                                 weekly_progress: List[Dict]) -> Dict:
        """Calculate monthly progress analytics"""
        monthly_data = {
            'month': month,
            'year': year,
            'total_study_hours': 0,
            'total_topics_completed': 0,
            'average_weekly_study_time': 0,
            'average_productivity_score': 0.0,
            'study_consistency_score': 0.0,
            'top_performing_weeks': [],
            'areas_for_improvement': [],
            'monthly_goals_achieved': 0,
            'next_month_recommendations': []
        }
        
        if not weekly_progress:
            return monthly_data
        
        weekly_study_times = []
        weekly_productivity_scores = []
        
        for week_data in weekly_progress:
            weekly_study_times.append(week_data['total_study_hours'])
            weekly_productivity_scores.append(week_data['average_productivity_score'])
            monthly_data['total_study_hours'] += week_data['total_study_hours']
            monthly_data['total_topics_completed'] += week_data['total_topics_completed']
        
        # Calculate averages
        if weekly_study_times:
            monthly_data['average_weekly_study_time'] = statistics.mean(weekly_study_times)
            monthly_data['average_productivity_score'] = statistics.mean(weekly_productivity_scores)
            
            # Calculate consistency score
            monthly_data['study_consistency_score'] = self._calculate_consistency_score(weekly_study_times)
            
            # Find top performing weeks
            sorted_weeks = sorted(enumerate(weekly_study_times), key=lambda x: x[1], reverse=True)
            monthly_data['top_performing_weeks'] = [weekly_progress[i]['week_start'] for i, _ in sorted_weeks[:2]]
        
        # Generate recommendations
        monthly_data['next_month_recommendations'] = self._generate_monthly_recommendations(monthly_data)
        
        return monthly_data
    
    def _calculate_productivity_score(self, daily_data: Dict) -> float:
        """Calculate productivity score based on study metrics"""
        score = 0.0
        
        # Base score from study time (max 40 points)
        study_hours = daily_data['total_study_time'] / 60
        score += min(study_hours * 10, 40)
        
        # Bonus for completed topics (max 30 points)
        score += min(daily_data['topics_completed'] * 10, 30)
        
        # Bonus for focus time (max 20 points)
        focus_hours = daily_data['focus_time'] / 60
        score += min(focus_hours * 5, 20)
        
        # Bonus for session consistency (max 10 points)
        if daily_data['session_count'] > 0:
            avg_session = daily_data['average_session_length']
            if 20 <= avg_session <= 60:  # Optimal session length
                score += 10
        
        return min(score, 100.0)
    
    def _calculate_progress_trend(self, study_times: List[int]) -> str:
        """Calculate progress trend over time"""
        if len(study_times) < 2:
            return 'stable'
        
        # Simple trend calculation
        first_half = study_times[:len(study_times)//2]
        second_half = study_times[len(study_times)//2:]
        
        first_avg = statistics.mean(first_half)
        second_avg = statistics.mean(second_half)
        
        if second_avg > first_avg * 1.1:
            return 'improving'
        elif second_avg < first_avg * 0.9:
            return 'declining'
        else:
            return 'stable'
    
    def _calculate_consistency_score(self, weekly_times: List[float]) -> float:
        """Calculate consistency score based on variance in study times"""
        if len(weekly_times) < 2:
            return 100.0
        
        mean_time = statistics.mean(weekly_times)
        if mean_time == 0:
            return 0.0
        
        variance = statistics.variance(weekly_times)
        coefficient_of_variation = (variance ** 0.5) / mean_time
        
        # Lower coefficient of variation = higher consistency
        consistency_score = max(0, 100 - (coefficient_of_variation * 100))
        return consistency_score
    
    def _generate_weekly_recommendations(self, weekly_data: Dict) -> List[str]:
        """Generate personalized recommendations based on weekly progress"""
        recommendations = []
        
        if weekly_data['average_productivity_score'] < 50:
            recommendations.append("Consider increasing study time or improving focus during sessions")
        
        if weekly_data['study_streak_days'] < 5:
            recommendations.append("Try to maintain more consistent daily study habits")
        
        if weekly_data['total_study_hours'] < 10:
            recommendations.append("Increase weekly study hours to meet learning goals")
        
        if weekly_data['average_productivity_score'] > 80:
            recommendations.append("Great job! Consider taking on more challenging topics")
        
        return recommendations
    
    def _generate_monthly_recommendations(self, monthly_data: Dict) -> List[str]:
        """Generate monthly recommendations for improvement"""
        recommendations = []
        
        if monthly_data['study_consistency_score'] < 70:
            recommendations.append("Focus on maintaining more consistent study schedules")
        
        if monthly_data['average_productivity_score'] < 60:
            recommendations.append("Work on improving study techniques and focus")
        
        if monthly_data['total_study_hours'] < 40:
            recommendations.append("Consider increasing monthly study hours")
        
        return recommendations
    
    def get_progress_insights(self, user_id: int, time_period: str = 'week') -> Dict:
        """Get comprehensive progress insights"""
        insights = {
            'time_period': time_period,
            'summary': {},
            'trends': {},
            'achievements': [],
            'challenges': [],
            'recommendations': []
        }
        
        # This would typically fetch data from database
        # For now, return a template structure
        return insights
    
    def export_progress_report(self, progress_data: Dict, format_type: str = 'json') -> str:
        """Export progress report in various formats"""
        if format_type == 'json':
            return json.dumps(progress_data, indent=2, default=str)
        elif format_type == 'csv':
            return self._export_to_csv(progress_data)
        else:
            return json.dumps(progress_data, indent=2, default=str)
    
    def _export_to_csv(self, progress_data: Dict) -> str:
        """Export progress data to CSV format"""
        # Simplified CSV export - would be more comprehensive in production
        csv_lines = ["Date,Study Hours,Topics Completed,Productivity Score"]
        
        if 'daily_progress' in progress_data:
            for day in progress_data['daily_progress']:
                csv_lines.append(f"{day['date']},{day['total_study_time']/60:.1f},{day['topics_completed']},{day['productivity_score']:.1f}")
        
        return '\n'.join(csv_lines)

