import re
from collections import defaultdict
import json

class AdvancedTopicCategorizer:
    def __init__(self):
        self.categories = {
            'Programming': {
                'keywords': ['programming', 'coding', 'algorithm', 'data structure', 'software', 'development', 'programming language', 'code', 'function', 'variable', 'loop', 'array', 'object', 'class'],
                'subcategories': ['Web Development', 'Mobile Development', 'Desktop Applications', 'Game Development', 'System Programming']
            },
            'Mathematics': {
                'keywords': ['mathematics', 'math', 'calculus', 'algebra', 'geometry', 'statistics', 'probability', 'linear algebra', 'differential', 'integral', 'equation', 'theorem', 'proof'],
                'subcategories': ['Calculus', 'Linear Algebra', 'Statistics', 'Discrete Mathematics', 'Applied Mathematics']
            },
            'Computer Science': {
                'keywords': ['computer science', 'computing', 'computer', 'system', 'network', 'database', 'operating system', 'computer architecture', 'compiler', 'artificial intelligence'],
                'subcategories': ['Computer Architecture', 'Operating Systems', 'Networks', 'Databases', 'Theory of Computation']
            },
            'Data Science': {
                'keywords': ['data science', 'machine learning', 'artificial intelligence', 'data analysis', 'big data', 'data mining', 'predictive modeling', 'neural network', 'deep learning'],
                'subcategories': ['Machine Learning', 'Deep Learning', 'Data Analysis', 'Big Data', 'Predictive Analytics']
            },
            'Engineering': {
                'keywords': ['engineering', 'design', 'mechanical', 'electrical', 'civil', 'chemical', 'aerospace', 'biomedical', 'industrial', 'structural'],
                'subcategories': ['Mechanical Engineering', 'Electrical Engineering', 'Civil Engineering', 'Chemical Engineering', 'Biomedical Engineering']
            },
            'Business': {
                'keywords': ['business', 'management', 'marketing', 'finance', 'economics', 'accounting', 'strategy', 'leadership', 'entrepreneurship', 'operations'],
                'subcategories': ['Finance', 'Marketing', 'Management', 'Economics', 'Accounting']
            },
            'Science': {
                'keywords': ['physics', 'chemistry', 'biology', 'science', 'laboratory', 'experiment', 'research', 'scientific method', 'hypothesis', 'theory'],
                'subcategories': ['Physics', 'Chemistry', 'Biology', 'Environmental Science', 'Materials Science']
            },
            'Language & Communication': {
                'keywords': ['language', 'communication', 'writing', 'speaking', 'literature', 'grammar', 'vocabulary', 'linguistics', 'translation', 'rhetoric'],
                'subcategories': ['English', 'Foreign Languages', 'Technical Writing', 'Public Speaking', 'Linguistics']
            },
            'General Studies': {
                'keywords': ['general', 'introduction', 'overview', 'fundamentals', 'basics', 'principles', 'concepts', 'theory', 'practice'],
                'subcategories': ['Introduction', 'Fundamentals', 'Principles', 'Concepts', 'Overview']
            }
        }
        
        self.difficulty_keywords = {
            'Easy': ['introduction', 'basic', 'fundamental', 'overview', 'beginner', 'simple', 'elementary'],
            'Medium': ['intermediate', 'advanced', 'complex', 'detailed', 'comprehensive', 'thorough'],
            'Hard': ['expert', 'master', 'advanced', 'complex', 'sophisticated', 'specialized', 'research']
        }
        
        # Simple stop words list
        self.stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}

    def categorize_topic(self, topic_text):
        """Categorize a topic and determine its difficulty level"""
        topic_lower = topic_text.lower()
        
        # Simple tokenization without NLTK
        words = [word for word in topic_lower.split() if word.isalpha() and word not in self.stop_words]
        
        # Find best matching category
        category_scores = defaultdict(int)
        for category, data in self.categories.items():
            for keyword in data['keywords']:
                if keyword in topic_lower:
                    category_scores[category] += 1
        
        # Determine main category
        main_category = max(category_scores, key=category_scores.get) if category_scores else 'General Studies'
        
        # Determine subcategory
        subcategory = self._determine_subcategory(topic_text, main_category)
        
        # Determine difficulty
        difficulty = self._determine_difficulty(topic_text)
        
        # Estimate study hours based on complexity
        estimated_hours = self._estimate_study_hours(topic_text, difficulty)
        
        # Determine priority based on keywords
        priority = self._determine_priority(topic_text)
        
        return {
            'category': main_category,
            'subcategory': subcategory,
            'difficulty': difficulty,
            'estimated_hours': estimated_hours,
            'priority': priority,
            'confidence': max(category_scores.values()) / len(words) if words else 0
        }

    def _determine_subcategory(self, topic_text, main_category):
        """Determine the specific subcategory within the main category"""
        topic_lower = topic_text.lower()
        subcategories = self.categories[main_category]['subcategories']
        
        for subcat in subcategories:
            if subcat.lower() in topic_lower:
                return subcat
        
        # Default to first subcategory if no match
        return subcategories[0] if subcategories else main_category

    def _determine_difficulty(self, topic_text):
        """Determine difficulty level based on keywords"""
        topic_lower = topic_text.lower()
        
        for difficulty, keywords in self.difficulty_keywords.items():
            for keyword in keywords:
                if keyword in topic_lower:
                    return difficulty
        
        return 'Medium'  # Default difficulty

    def _estimate_study_hours(self, topic_text, difficulty):
        """Estimate study hours based on topic complexity and difficulty"""
        base_hours = {
            'Easy': 1.0,
            'Medium': 2.5,
            'Hard': 4.0
        }
        
        # Adjust based on topic length and complexity indicators
        complexity_indicators = ['advanced', 'comprehensive', 'detailed', 'thorough', 'complete']
        topic_lower = topic_text.lower()
        
        multiplier = 1.0
        for indicator in complexity_indicators:
            if indicator in topic_lower:
                multiplier += 0.5
        
        return base_hours[difficulty] * multiplier

    def _determine_priority(self, topic_text):
        """Determine priority level (1-5) based on keywords"""
        topic_lower = topic_text.lower()
        
        high_priority_keywords = ['exam', 'test', 'final', 'important', 'critical', 'urgent', 'deadline']
        low_priority_keywords = ['optional', 'extra', 'bonus', 'additional', 'supplementary']
        
        for keyword in high_priority_keywords:
            if keyword in topic_lower:
                return 5
        
        for keyword in low_priority_keywords:
            if keyword in topic_lower:
                return 1
        
        return 3  # Default priority

    def get_study_recommendations(self, topic_data):
        """Get personalized study recommendations based on topic analysis"""
        recommendations = []
        
        if topic_data['difficulty'] == 'Hard':
            recommendations.append("Break this topic into smaller subtopics")
            recommendations.append("Allocate extra study time")
            recommendations.append("Consider finding additional resources")
        
        if topic_data['priority'] >= 4:
            recommendations.append("Schedule this topic early in your study plan")
            recommendations.append("Review multiple times before exams")
        
        if topic_data['estimated_hours'] > 3:
            recommendations.append("Split into multiple study sessions")
            recommendations.append("Take regular breaks during study")
        
        return recommendations