import os
import random
import time

try:
    from groq import Groq
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
    groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
except ImportError:
    groq_client = None

try:
    import google.generativeai as genai
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
    gemini_client = True if GEMINI_API_KEY else None
except ImportError:
    gemini_client = None


class BaseAgent:
    def __init__(self, name, role, llm_rate=0.05):
        self.name = name
        self.role = role
        # Only use LLM for a fraction of actions to avoid rate limits
        self.llm_rate = llm_rate

    @property
    def needs_llm(self):
        return random.random() < self.llm_rate

    def act(self, state):
        # Default mock action
        action_data = {
            "agent": self.name,
            "role": self.role,
            "action": "idle",
            "event_type": "info",
            "details": "Routine waiting"
        }
        
        if self.needs_llm and groq_client:
            try:
                chat_completion = groq_client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": f"Act as a {self.role} named {self.name} in a corporate IT network. Generate 1 JSON log entry describing your current action. The state is {state}. Format must be exact valid JSON with keys: action, event_type, details.",
                        }
                    ],
                    model="llama3.1-8b-instant",  # Updated to a valid free model name or just llama3-8b-8192
                    response_format={"type": "json_object"}
                )
                import json
                llm_response = json.loads(chat_completion.choices[0].message.content)
                action_data["action"] = llm_response.get("action", action_data["action"])
                action_data["event_type"] = llm_response.get("event_type", "info")
                action_data["details"] = f"[GROQ] {llm_response.get('details', '')}"
            except Exception as e:
                action_data["details"] = f"LLM Error fallback: {str(e)}"
        elif self.needs_llm and gemini_client:
            # Fallback to Gemini if Groq fails or rate limits
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(f"Act as a {self.role}. Generate a 1-sentence action log based on state {state}.")
                action_data["action"] = "llm_generated_action"
                action_data["details"] = f"[GEMINI] {response.text.strip()}"
            except Exception as e:
                action_data["details"] = f"Gemini Error fallback: {str(e)}"
        else:
            # Deterministic mock behaviors if LLM is not needed
            action_data = self.mock_act(state)
            
        return action_data

    def mock_act(self, state):
        return {
            "agent": self.name,
            "role": self.role,
            "action": "routine_operation",
            "event_type": "info",
            "details": "Performing standard daily tasks."
        }


class UserAgent(BaseAgent):
    def __init__(self, name):
        super().__init__(name, role="Employee")
        
    def mock_act(self, state):
        actions = [
            ("login", "Login success"),
            ("file_access", "Opened Q3_report.pdf"),
            ("web_browsing", "Browsed external news site"),
            ("email", "Sent email to external client")
        ]
        action, details = random.choice(actions)
        return {
            "agent": self.name,
            "role": self.role,
            "action": action,
            "event_type": "info",
            "details": details
        }


class SysAdminAgent(BaseAgent):
    def __init__(self, name):
        super().__init__(name, role="SysAdmin", llm_rate=0.1) # SysAdmins use LLM slightly more often
        
    def mock_act(self, state):
        if state["suspicious_events"] > 10:
            return {
                "agent": self.name,
                "role": self.role,
                "action": "investigate_alerts",
                "event_type": "security",
                "details": f"Investigating {state['suspicious_events']} suspicious events."
            }
        return {
            "agent": self.name,
            "role": self.role,
            "action": "system_patching",
            "event_type": "info",
            "details": "Applied routine OS updates to standard fleet."
        }


class AttackerAgent(BaseAgent):
    def __init__(self, name):
        super().__init__(name, role="Attacker", llm_rate=0.2)
        
    def mock_act(self, state):
        actions = [
            ("port_scan", "Scanning subnet 10.0.0.x", "suspicious"),
            ("phishing_attempt", "Sent phishing to 5 users", "suspicious"),
            ("exploit_execution", "Attempted RCE on internal server", "compromise"),
            ("idle_recon", "Gathering open-source intelligence on employees", "info")
        ]
        action, details, evt_type = random.choice(actions)
        return {
            "agent": self.name,
            "role": self.role,
            "action": action,
            "event_type": evt_type,
            "details": details
        }


class CEOAgent(BaseAgent):
    def __init__(self, name):
        super().__init__(name, role="CEO", llm_rate=0.1)
        
    def mock_act(self, state):
        if state["compromised_hosts"] > 0:
            return {
                "agent": self.name,
                "role": self.role,
                "action": "emergency_meeting",
                "event_type": "critical",
                "details": "Called all-hands meeting regarding breach."
            }
        return {
            "agent": self.name,
            "role": self.role,
            "action": "strategic_review",
            "event_type": "info",
            "details": "Reviewing quarterly cyber risk reports."
        }
