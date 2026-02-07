"""
Strategist Agent for the Todo App.

This module provides the StrategistAgent class which analyzes user tasks
and provides intelligent insights, suggestions, and recommendations.
"""
from typing import List, Dict, Any
from datetime import datetime
from collections import Counter
import re


class StrategistAgent:
    """
    Analyzes user tasks and provides strategic insights and recommendations.

    The StrategistAgent examines task patterns, completion rates, and provides
    actionable suggestions to help users manage their tasks more effectively.
    """

    def __init__(self, tasks: List[Any]):
        """
        Initialize the StrategistAgent with a list of tasks.

        Args:
            tasks: List of Task objects to analyze
        """
        self.tasks = tasks
        self.total_tasks = len(tasks)
        self.completed_tasks = [t for t in tasks if t.completed]
        self.pending_tasks = [t for t in tasks if not t.completed]
        self.completion_rate = (len(self.completed_tasks) / self.total_tasks * 100) if self.total_tasks > 0 else 0

    def analyze(self) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of user tasks.

        Returns:
            A dictionary containing analysis results and recommendations
        """
        if self.total_tasks == 0:
            return {
                "summary": "You have no tasks yet. Start by adding your first task!",
                "insights": [],
                "recommendations": ["Create your first task to get started with productivity tracking."],
                "stats": {
                    "total": 0,
                    "completed": 0,
                    "pending": 0,
                    "completion_rate": 0
                }
            }

        insights = self._generate_insights()
        recommendations = self._generate_recommendations()
        patterns = self._detect_patterns()

        return {
            "summary": self._generate_summary(),
            "insights": insights,
            "recommendations": recommendations,
            "patterns": patterns,
            "stats": {
                "total": self.total_tasks,
                "completed": len(self.completed_tasks),
                "pending": len(self.pending_tasks),
                "completion_rate": round(self.completion_rate, 1)
            }
        }

    def _generate_summary(self) -> str:
        """Generate a high-level summary of task status."""
        if self.completion_rate == 100:
            return f"🎉 Excellent work! All {self.total_tasks} tasks are completed!"
        elif self.completion_rate >= 75:
            return f"💪 Great progress! {len(self.completed_tasks)} of {self.total_tasks} tasks completed ({self.completion_rate:.0f}%)."
        elif self.completion_rate >= 50:
            return f"📊 You're halfway there! {len(self.completed_tasks)} of {self.total_tasks} tasks completed ({self.completion_rate:.0f}%)."
        elif self.completion_rate >= 25:
            return f"🚀 Keep going! {len(self.completed_tasks)} of {self.total_tasks} tasks completed ({self.completion_rate:.0f}%)."
        else:
            return f"📝 You have {self.total_tasks} tasks with {len(self.pending_tasks)} pending. Let's get started!"

    def _generate_insights(self) -> List[str]:
        """Generate actionable insights based on task analysis."""
        insights = []

        # Completion rate insight
        if self.completion_rate >= 80:
            insights.append("You have an excellent completion rate! Keep up the momentum.")
        elif self.completion_rate < 30 and self.total_tasks > 5:
            insights.append("Many tasks are pending. Consider breaking them into smaller, manageable steps.")

        # Task volume insight
        if self.total_tasks > 20:
            insights.append("You have a large number of tasks. Consider archiving completed ones to reduce clutter.")
        elif self.total_tasks < 5:
            insights.append("Your task list is lean. This is great for maintaining focus!")

        # Recent activity insight
        recent_tasks = [t for t in self.tasks if self._is_recent(t.created_at)]
        if len(recent_tasks) > 5:
            insights.append(f"You've been very active recently with {len(recent_tasks)} tasks created in the last 7 days.")

        return insights

    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        # Pending tasks recommendation
        if len(self.pending_tasks) > 0:
            oldest_pending = min(self.pending_tasks, key=lambda t: t.created_at)
            recommendations.append(f"Start with task #{oldest_pending.id}: '{oldest_pending.title}' - it's been pending the longest.")

        # Quick wins recommendation
        if len(self.pending_tasks) > 3:
            recommendations.append("Try completing 2-3 small tasks today for quick wins and momentum.")

        # Completion celebration
        if self.completion_rate >= 50 and len(self.pending_tasks) <= 3:
            recommendations.append("You're close to clearing your list! Finish the remaining tasks to achieve inbox zero.")

        # Pattern-based recommendations
        task_keywords = self._extract_keywords()
        if task_keywords:
            top_keyword = task_keywords.most_common(1)[0][0]
            related_count = task_keywords[top_keyword]
            if related_count >= 3:
                recommendations.append(f"You have {related_count} tasks related to '{top_keyword}'. Consider batching them together.")

        return recommendations

    def _detect_patterns(self) -> List[str]:
        """Detect patterns in task titles and descriptions."""
        patterns = []

        # Keyword frequency analysis
        keywords = self._extract_keywords()
        if keywords:
            top_3 = keywords.most_common(3)
            pattern_text = "Common themes: " + ", ".join([f"{word} ({count})" for word, count in top_3])
            patterns.append(pattern_text)

        # Task length analysis
        avg_title_length = sum(len(t.title) for t in self.tasks) / self.total_tasks if self.total_tasks > 0 else 0
        if avg_title_length < 15:
            patterns.append("Your tasks have concise titles - great for quick scanning!")
        elif avg_title_length > 50:
            patterns.append("Your tasks have detailed titles - consider using descriptions for extra details.")

        return patterns

    def _extract_keywords(self) -> Counter:
        """Extract and count keywords from task titles."""
        # Common stop words to ignore
        stop_words = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'be', 'been', 'being'}

        all_words = []
        for task in self.tasks:
            # Extract words from title
            words = re.findall(r'\b[a-z]{3,}\b', task.title.lower())
            # Filter out stop words
            words = [w for w in words if w not in stop_words]
            all_words.extend(words)

        return Counter(all_words)

    def _is_recent(self, timestamp: str) -> bool:
        """Check if a timestamp is within the last 7 days."""
        try:
            task_date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            now = datetime.now(task_date.tzinfo)
            delta = now - task_date
            return delta.days <= 7
        except:
            return False

    def get_formatted_response(self) -> str:
        """
        Get a formatted text response suitable for display.

        Returns:
            A formatted string with analysis results
        """
        analysis = self.analyze()

        response_parts = [
            f"📊 **Task Analysis Report**\n",
            f"{analysis['summary']}\n",
            f"\n**Statistics:**",
            f"• Total Tasks: {analysis['stats']['total']}",
            f"• Completed: {analysis['stats']['completed']}",
            f"• Pending: {analysis['stats']['pending']}",
            f"• Completion Rate: {analysis['stats']['completion_rate']}%\n"
        ]

        if analysis['insights']:
            response_parts.append("\n**Insights:**")
            for insight in analysis['insights']:
                response_parts.append(f"• {insight}")

        if analysis['recommendations']:
            response_parts.append("\n**Recommendations:**")
            for i, rec in enumerate(analysis['recommendations'], 1):
                response_parts.append(f"{i}. {rec}")

        if analysis['patterns']:
            response_parts.append("\n**Patterns Detected:**")
            for pattern in analysis['patterns']:
                response_parts.append(f"• {pattern}")

        return "\n".join(response_parts)
