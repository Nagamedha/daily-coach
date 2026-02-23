from typing import Dict, List, Any
from openai import OpenAI
from services.config_service import ConfigService


class AIServiceError(Exception):
    """Raised when AI service encounters an error."""
    pass


class AIService:
    """Modular interface to LLM providers for coaching feedback and chat."""
    
    def __init__(self, config: ConfigService):
        """Initialize OpenAI client."""
        self.config = config
        try:
            # Using same config methods but for OpenAI
            self.client = OpenAI(api_key=config.get_claude_api_key())
            self.model = config.get_claude_model()
        except Exception as e:
            raise AIServiceError(f"Failed to initialize AI service: {str(e)}")
    
    def generate_end_of_day_coaching(
        self,
        date: str,
        mode: str,
        checked: Dict[str, bool],
        score: int,
        total: int,
        done: int,
        note: str,
        streaks: Dict[str, int],
        history: List[Dict[str, Any]],
        blocks: List[Dict[str, str]]
    ) -> str:
        """Generate personalized end-of-day coaching message."""
        try:
            prompt = self._build_coaching_prompt(
                date, mode, checked, score, total, done, note, streaks, history, blocks
            )
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.7,
                timeout=30.0
            )
            
            response_text = response.choices[0].message.content
            if not response_text:
                return "Unable to generate coaching feedback at this time"
            
            return response_text
        except Exception as e:
            raise AIServiceError(f"AI service error: {str(e)}")
    
    def generate_chat_response(
        self,
        user_message: str,
        history: List[Dict[str, Any]],
        streaks: Dict[str, int]
    ) -> str:
        """Generate conversational response to user query."""
        try:
            prompt = self._build_chat_prompt(user_message, history, streaks)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7,
                timeout=30.0
            )
            
            response_text = response.choices[0].message.content
            if not response_text:
                return "I'm having trouble generating a response right now. Please try again."
            
            return response_text
        except Exception as e:
            raise AIServiceError(f"AI service error: {str(e)}")
    
    def _build_coaching_prompt(
        self,
        date: str,
        mode: str,
        checked: Dict[str, bool],
        score: int,
        total: int,
        done: int,
        note: str,
        streaks: Dict[str, int],
        history: List[Dict[str, Any]],
        blocks: List[Dict[str, str]]
    ) -> str:
        """Build prompt for strict trainer personality."""
        completed = [b["label"] for b in blocks if checked.get(b["id"])]
        missed = [b["label"] for b in blocks if not checked.get(b["id"])]
        
        history_summary = ""
        if history:
            history_summary = "ACTUAL RECENT PERFORMANCE (from database):\n"
            for h in history[-7:]:
                history_summary += f"- {h.get('date')}: {h.get('score')}% ({h.get('done')}/{h.get('total')} blocks), mode: {h.get('mode')}\n"
        
        prompt = f"""You are a STRICT personal trainer and life coach. You care deeply about your client's success, but you don't sugarcoat reality. Your role is to keep them accountable, motivated, and on track to achieve their goals: getting a job, staying fit, and maintaining a healthy lifestyle.

CRITICAL RULES:
1. ONLY reference the ACTUAL DATA provided below - NEVER make up or assume information
2. If data is missing, acknowledge it - don't invent numbers
3. Reject any questions unrelated to: schedule tracking, productivity, health, Gen AI topics, AI agents
4. For off-topic questions, respond: "That's not my role. I'm your healthy lifestyle coach here to help you follow your daily schedule, get a job, be fit, and have a healthy lifestyle."

TODAY'S ACTUAL DATA (from database):
- Date: {date}
- Schedule mode: {mode.replace('_', ' ').title()}
- Blocks completed: {done}/{total} ({score}%)
- Completed tasks: {', '.join(completed) if completed else 'None'}
- Missed tasks: {', '.join(missed) if missed else 'None'}
- Their note: "{note if note else 'No note'}"

ACTUAL CUMULATIVE STATS (from database):
- Total gym days tracked: {streaks.get('gym_days', 0)}
- Total study days tracked: {streaks.get('study_days', 0)}
- Total job application days tracked: {streaks.get('job_days', 0)}

{history_summary}

YOUR COACHING APPROACH:
- Score >= 80%: Genuinely praise them. Be specific about what they did well. Boost their confidence. They earned it.
- Score 50-79%: Acknowledge effort, but be real about what slipped. Explain the CONSEQUENCES: missed gym = slower fitness progress, skipped study = delayed job search, no applications = longer unemployment. Create healthy urgency.
- Score < 50%: Be honest and direct. Don't crush them, but don't pretend it's okay. Remind them WHY they started this journey. What are they working toward? What happens if they keep missing days?

When they do well, CELEBRATE it specifically. When they slip, explain REAL consequences and provide COMPENSATION STRATEGIES.

Write 4-6 sentences. Be personal, direct, and motivating. Reference specific tasks from today. End with one sharp sentence for tomorrow."""
        
        return prompt
    
    def _build_chat_prompt(
        self,
        user_message: str,
        history: List[Dict[str, Any]],
        streaks: Dict[str, int]
    ) -> str:
        """Build prompt for conversational responses with strict personality."""
        
        history_context = ""
        if history:
            history_context = "ACTUAL USER DATA (from database):\n"
            for log in history[:14]:
                history_context += f"- {log.get('date')}: {log.get('score')}% ({log.get('done')}/{log.get('total')} blocks), mode: {log.get('mode')}\n"
        
        prompt = f"""You are a STRICT personal trainer and life coach. You're having a conversation with your client who is working to get a job, stay fit, and maintain a healthy lifestyle.

CRITICAL RULES:
1. ONLY reference the ACTUAL DATA provided below - NEVER make up information
2. If asked about data you don't have, say "I don't have that information in my records"
3. ONLY answer questions about: schedule tracking, productivity, health, Gen AI topics, AI agents
4. For ANY other topic, respond EXACTLY: "That's not my role. I'm your healthy lifestyle coach here to help you follow your daily schedule, get a job, be fit, and have a healthy lifestyle."

User's question: "{user_message}"

ACTUAL CUMULATIVE STATS (from database):
- Total gym days tracked: {streaks.get('gym_days', 0)}
- Total study days tracked: {streaks.get('study_days', 0)}
- Total job application days tracked: {streaks.get('job_days', 0)}

{history_context}

YOUR RESPONSE STYLE:
- Be direct and honest - use the actual numbers above
- If they're doing well, celebrate it with specifics
- If they're slipping, explain REAL consequences and provide strategies
- Create healthy urgency when needed
- Be warm but strict - you care about their success
- Keep it conversational (3-5 sentences)
- Reference specific dates and numbers from the data above"""
        
        return prompt
