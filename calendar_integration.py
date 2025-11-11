from datetime import datetime, timedelta, date, time
import calendar as cal_module
from typing import List, Dict, Optional
import json

class CalendarIntegration:
    def __init__(self):
        self.time_slots = {
            'morning': {'start': 8, 'end': 12},
            'afternoon': {'start': 13, 'end': 17},
            'evening': {'start': 18, 'end': 22}
        }
        
    def generate_smart_schedule(self, topics: List[Dict], start_date: date, study_days: int = 5) -> Dict:
        """Generate an intelligent study schedule with calendar integration"""
        schedule = {}
        current_date = start_date
        
        # Sort topics by priority and difficulty
        sorted_topics = sorted(topics, key=lambda x: (x['priority'], x['difficulty']), reverse=True)
        
        for i in range(study_days):
            day_name = current_date.strftime('%A')
            schedule[day_name] = {
                'date': current_date.isoformat(),
                'events': [],
                'total_hours': 0,
                'focus_score': 0
            }
            
            # Distribute topics across the day
            day_topics = self._distribute_topics_for_day(sorted_topics, i, study_days)
            
            for topic in day_topics:
                event = self._create_study_event(topic, current_date)
                schedule[day_name]['events'].append(event)
                schedule[day_name]['total_hours'] += topic['estimated_hours']
            
            # Add breaks and optimize schedule
            schedule[day_name] = self._optimize_daily_schedule(schedule[day_name])
            
            current_date += timedelta(days=1)
        
        return schedule
    
    def _distribute_topics_for_day(self, topics: List[Dict], day_index: int, total_days: int) -> List[Dict]:
        """Distribute topics across days based on priority and difficulty"""
        topics_per_day = len(topics) // total_days
        start_idx = day_index * topics_per_day
        
        if day_index == total_days - 1:  # Last day gets remaining topics
            return topics[start_idx:]
        else:
            return topics[start_idx:start_idx + topics_per_day]
    
    def _create_study_event(self, topic: Dict, event_date: date) -> Dict:
        """Create a calendar event for a study topic"""
        # Determine optimal time slot based on topic difficulty
        time_slot = self._get_optimal_time_slot(topic['difficulty'])
        
        start_time = datetime.combine(event_date, time(hour=time_slot['start']))
        end_time = start_time + timedelta(hours=topic['estimated_hours'])
        
        return {
            'title': f"Study: {topic['name']}",
            'description': f"Category: {topic['category']}\nDifficulty: {topic['difficulty']}\nPriority: {topic['priority']}",
            'start_datetime': start_time.isoformat(),
            'end_datetime': end_time.isoformat(),
            'topic_id': topic.get('id'),
            'event_type': 'study',
            'difficulty': topic['difficulty'],
            'priority': topic['priority'],
            'estimated_hours': topic['estimated_hours']
        }
    
    def _get_optimal_time_slot(self, difficulty: str) -> Dict:
        """Get optimal time slot based on topic difficulty"""
        if difficulty == 'Hard':
            return self.time_slots['morning']  # Hard topics in morning when fresh
        elif difficulty == 'Easy':
            return self.time_slots['evening']  # Easy topics in evening
        else:
            return self.time_slots['afternoon']  # Medium topics in afternoon
    
    def _optimize_daily_schedule(self, day_schedule: Dict) -> Dict:
        """Optimize daily schedule by adding breaks and adjusting timing"""
        events = day_schedule['events']
        optimized_events = []
        
        for i, event in enumerate(events):
            optimized_events.append(event)
            
            # Add break after each study session (except the last one)
            if i < len(events) - 1:
                break_event = self._create_break_event(event['end_datetime'])
                optimized_events.append(break_event)
        
        day_schedule['events'] = optimized_events
        day_schedule['focus_score'] = self._calculate_focus_score(optimized_events)
        
        return day_schedule
    
    def _create_break_event(self, after_time: str) -> Dict:
        """Create a break event after a study session"""
        start_time = datetime.fromisoformat(after_time)
        end_time = start_time + timedelta(minutes=15)  # 15-minute break
        
        return {
            'title': 'Break',
            'description': 'Take a 15-minute break to refresh',
            'start_datetime': start_time.isoformat(),
            'end_datetime': end_time.isoformat(),
            'event_type': 'break',
            'duration_minutes': 15
        }
    
    def _calculate_focus_score(self, events: List[Dict]) -> float:
        """Calculate focus score for the day based on study distribution"""
        study_events = [e for e in events if e['event_type'] == 'study']
        if not study_events:
            return 0.0
        
        # Higher score for morning study sessions and balanced difficulty
        score = 0.0
        for event in study_events:
            hour = datetime.fromisoformat(event['start_datetime']).hour
            
            # Morning sessions get higher score
            if hour < 12:
                score += 10
            elif hour < 17:
                score += 7
            else:
                score += 5
            
            # Bonus for high priority topics
            if event.get('priority', 3) >= 4:
                score += 5
        
        return min(score, 100.0)  # Cap at 100
    
    def export_to_calendar_format(self, schedule: Dict, format_type: str = 'ics') -> str:
        """Export schedule to various calendar formats"""
        if format_type == 'ics':
            return self._export_to_ics(schedule)
        elif format_type == 'json':
            return json.dumps(schedule, indent=2)
        else:
            return json.dumps(schedule, indent=2)
    
    def _export_to_ics(self, schedule: Dict) -> str:
        """Export schedule to ICS (iCalendar) format"""
        ics_content = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//AI Study Planner//EN\n"
        
        for day_name, day_data in schedule.items():
            for event in day_data['events']:
                ics_content += "BEGIN:VEVENT\n"
                ics_content += f"DTSTART:{event['start_datetime'].replace('-', '').replace(':', '').split('.')[0]}Z\n"
                ics_content += f"DTEND:{event['end_datetime'].replace('-', '').replace(':', '').split('.')[0]}Z\n"
                ics_content += f"SUMMARY:{event['title']}\n"
                ics_content += f"DESCRIPTION:{event['description']}\n"
                ics_content += "END:VEVENT\n"
        
        ics_content += "END:VCALENDAR\n"
        return ics_content
    
    def get_calendar_view(self, schedule: Dict, view_type: str = 'week') -> Dict:
        """Get calendar view for different time periods"""
        if view_type == 'week':
            return self._get_weekly_view(schedule)
        elif view_type == 'month':
            return self._get_monthly_view(schedule)
        else:
            return schedule
    
    def _get_weekly_view(self, schedule: Dict) -> Dict:
        """Get weekly calendar view"""
        week_view = {
            'week_start': None,
            'days': [],
            'total_study_hours': 0,
            'average_focus_score': 0
        }
        
        focus_scores = []
        for day_name, day_data in schedule.items():
            # Include events in the day data for template rendering
            week_view['days'].append({
                'day': day_name,
                'date': day_data.get('date', ''),
                'events': day_data.get('events', []),  # Include actual events
                'events_count': len(day_data.get('events', [])),
                'study_hours': day_data.get('total_hours', 0),
                'focus_score': day_data.get('focus_score', 0)
            })
            week_view['total_study_hours'] += day_data.get('total_hours', 0)
            focus_scores.append(day_data.get('focus_score', 0))
        
        week_view['average_focus_score'] = sum(focus_scores) / len(focus_scores) if focus_scores else 0
        
        return week_view
    
    def _get_monthly_view(self, schedule: Dict) -> Dict:
        """Get monthly calendar view"""
        month_view = {
            'month': None,
            'weeks': [],
            'total_study_hours': 0,
            'study_days': 0
        }
        
        for day_name, day_data in schedule.items():
            month_view['total_study_hours'] += day_data['total_hours']
            if day_data['total_hours'] > 0:
                month_view['study_days'] += 1
        
        return month_view

