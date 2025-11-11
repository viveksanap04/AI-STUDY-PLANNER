import json
import csv
from datetime import datetime, date
from typing import Dict, List
from io import StringIO

class ExportManager:
    def __init__(self):
        pass
    
    def export_schedule_to_json(self, schedule: Dict) -> str:
        """Export study schedule to JSON format"""
        return json.dumps(schedule, indent=2, default=str)
    
    def export_schedule_to_csv(self, schedule: Dict) -> str:
        """Export study schedule to CSV format"""
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['Day', 'Date', 'Topic', 'Start Time', 'End Time', 'Duration (hours)', 'Difficulty', 'Priority'])
        
        # Data rows
        for day_name, day_data in schedule.items():
            date_str = day_data.get('date', '')
            for event in day_data.get('events', []):
                if event.get('event_type') == 'study':
                    start_time = event.get('start_datetime', '').split('T')[1][:5] if 'T' in event.get('start_datetime', '') else ''
                    end_time = event.get('end_datetime', '').split('T')[1][:5] if 'T' in event.get('end_datetime', '') else ''
                    duration = event.get('estimated_hours', 0)
                    difficulty = event.get('difficulty', 'Medium')
                    priority = event.get('priority', 3)
                    topic = event.get('title', '').replace('Study: ', '')
                    
                    writer.writerow([day_name, date_str, topic, start_time, end_time, duration, difficulty, priority])
        
        return output.getvalue()
    
    def export_progress_to_csv(self, progress_data: List[Dict]) -> str:
        """Export progress data to CSV format"""
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['Date', 'Study Time (minutes)', 'Topics Completed', 'Productivity Score', 'Focus Time (minutes)'])
        
        # Data rows
        for day in progress_data:
            writer.writerow([
                day.get('date', ''),
                day.get('total_study_time', 0),
                day.get('topics_completed', 0),
                day.get('productivity_score', 0),
                day.get('focus_time', 0)
            ])
        
        return output.getvalue()
    
    def export_notes_to_txt(self, notes: List[Dict]) -> str:
        """Export study notes to text format"""
        output = []
        output.append("=" * 80)
        output.append("STUDY NOTES EXPORT")
        output.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output.append("=" * 80)
        output.append("")
        
        for note in notes:
            output.append(f"Title: {note.get('title', 'Untitled')}")
            output.append(f"Created: {note.get('created_at', '')}")
            output.append(f"Updated: {note.get('updated_at', '')}")
            output.append("-" * 80)
            output.append(note.get('content', ''))
            output.append("")
            output.append("=" * 80)
            output.append("")
        
        return "\n".join(output)
    
    def export_flashcards_to_csv(self, flashcards: List[Dict]) -> str:
        """Export flashcards to CSV format"""
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['Question', 'Answer', 'Topic', 'Difficulty', 'Mastery Level', 'Times Studied'])
        
        # Data rows
        for card in flashcards:
            writer.writerow([
                card.get('question', ''),
                card.get('answer', ''),
                card.get('topic_name', ''),
                card.get('difficulty', 'Medium'),
                card.get('mastery_level', 0),
                card.get('times_studied', 0)
            ])
        
        return output.getvalue()
    
    def create_study_report(self, schedule: Dict, progress: List[Dict], goals: List[Dict]) -> str:
        """Create a comprehensive study report"""
        report = []
        report.append("=" * 80)
        report.append("AI STUDY PLANNER - COMPREHENSIVE REPORT")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 80)
        report.append("")
        
        # Schedule Summary
        report.append("STUDY SCHEDULE SUMMARY")
        report.append("-" * 80)
        total_hours = 0
        for day_name, day_data in schedule.items():
            report.append(f"{day_name}: {day_data.get('total_hours', 0)} hours")
            total_hours += day_data.get('total_hours', 0)
        report.append(f"Total Study Hours: {total_hours}")
        report.append("")
        
        # Progress Summary
        if progress:
            report.append("PROGRESS SUMMARY")
            report.append("-" * 80)
            total_study_time = sum(d.get('total_study_time', 0) for d in progress)
            total_completed = sum(d.get('topics_completed', 0) for d in progress)
            avg_productivity = sum(d.get('productivity_score', 0) for d in progress) / len(progress) if progress else 0
            report.append(f"Total Study Time: {total_study_time} minutes")
            report.append(f"Topics Completed: {total_completed}")
            report.append(f"Average Productivity Score: {avg_productivity:.1f}")
            report.append("")
        
        # Goals Summary
        if goals:
            report.append("GOALS SUMMARY")
            report.append("-" * 80)
            for goal in goals:
                status = goal.get('status', 'active')
                progress_pct = (goal.get('current_progress', 0) / goal.get('target_hours', 1) * 100) if goal.get('target_hours', 0) > 0 else 0
                report.append(f"{goal.get('title', 'Untitled')}: {progress_pct:.1f}% ({status})")
            report.append("")
        
        report.append("=" * 80)
        return "\n".join(report)

