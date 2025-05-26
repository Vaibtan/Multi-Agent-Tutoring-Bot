from datetime import datetime
from typing import Any, Dict, List, Optional

from google.adk.tools import ToolContext


class ConversationHistoryTool:
    @staticmethod
    def add_context(topic: str, key_points: str, tool_context: ToolContext) -> Dict[str, Any]:
        conversation_history = tool_context.state.get("conversation_history", [])
        new_context = {
            "timestamp": datetime.now().isoformat(),
            "topic": topic,
            "key_points": key_points,
            "interaction_count": len(conversation_history) + 1
        }
        conversation_history.append(new_context)
        tool_context.state["conversation_history"] = conversation_history
        return {
            "status": "success",
            "message": f"Added context for topic '{topic}' to conversation history",
            "total_interactions": len(conversation_history)
        }
    
    @staticmethod
    def get_context(topic: str = None, tool_context: ToolContext = None) -> Dict[str, Any]:
        conversation_history = tool_context.state.get("conversation_history", [])
        if not conversation_history:
            return {
                "status": "info",
                "message": "No conversation history found",
                "context": []
            }
        if topic:
            filtered_context = [ctx for ctx in conversation_history \
                if topic.lower() in ctx["topic"].lower()]
            return {
                "status": "success",
                "message": f"Found {len(filtered_context)} relevant interactions for topic '{topic}'",
                "context": filtered_context
            }        
        recent_context = conversation_history[-5:]
        return {
            "status": "success", 
            "message": f"Retrieved {len(recent_context)} recent interactions",
            "context": recent_context
        }
    
    @staticmethod
    def update_progress(subject: str, concept: str, \
        understanding_level: str, tool_context: ToolContext) -> Dict[str, Any]:
        learning_progress = tool_context.state.get("learning_progress", {})
        if subject not in learning_progress: learning_progress[subject] = {}
        learning_progress[subject][concept] = {"level": understanding_level, "last_updated": datetime.now().isoformat()}
        tool_context.state["learning_progress"] = learning_progress
        return {
            "status": "success",
            "message": f"Updated progress for {concept} in {subject} to {understanding_level}",
            "progress": learning_progress[subject]
        }
    
    @staticmethod
    def get_progress(subject: str = None, tool_context: ToolContext = None) -> Dict[str, Any]:
        learning_progress = tool_context.state.get("learning_progress", {})
        if not learning_progress:
            return {
                "status": "info",
                "message": "No learning progress tracked yet",
                "progress": {}
            }     
        if subject and subject in learning_progress:
            return {
                "status": "success",
                "message": f"Progress in {subject}",
                "progress": {subject: learning_progress[subject]}
            }
        return {
            "status": "success",
            "message": "All learning progress",
            "progress": learning_progress
        }
def add_context(topic: str, key_points: str, tool_context: ToolContext) -> dict:
    return ConversationHistoryTool.add_context(topic, key_points, tool_context)

def get_context(topic: Optional[str] = None, tool_context: ToolContext = None) -> dict:
    return ConversationHistoryTool.get_context(topic, tool_context)

def update_progress(subject: str, concept: str, understanding_level: str, tool_context: ToolContext) -> dict:
    return ConversationHistoryTool.update_progress(subject, concept, understanding_level, tool_context)

def get_progress(subject: Optional[str] = None, tool_context: ToolContext = None) -> dict:
    return ConversationHistoryTool.get_progress(subject, tool_context)
