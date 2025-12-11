"""
Master Agent that orchestrates the entire loan application flow
through conversational interface.
"""

from collections import defaultdict
from ai.groq_client import get_llama_response


class MasterAgent:
    """
    Master Agent (Orchestrator) that manages conversation flow
    and coordinates Worker Agents.
    """
    
    def __init__(self):
        self.stage = "GREETING"
        self.collected_data = {}
        self.pending_data = []
        
    from collections import defaultdict

def build_system_prompt(self, stage, context):
    """Build dynamic system prompt based on conversation stage"""
    
    base_prompt = """
    You are Mr. Finn, the Master Agent for LoanFlow AI - Tata Capital's intelligent loan assistant.

    Your role is to guide customers through a personal loan application via natural conversation.

    IMPORTANT RULES:
    1. Be conversational and friendly, like a real loan officer
    2. Ask ONE question at a time
    3. Validate responses before moving forward
    4. Use the customer's name once you know it
    5. Show empathy and build trust

    Current Stage: {stage}
    """
    
    stage_instructions = {
        "GREETING": """
    STAGE: GREETING
    - Welcome the customer warmly
    - Mention they may be pre-approved for a personal loan
    - Ask if they're interested in exploring loan options
    """,

            "COLLECT_PAN": """
    STAGE: PAN COLLECTION
    - Ask for their PAN number for identity verification
    - Explain: "I'll need your PAN to check your pre-approved limit and credit profile"
    - Format: ABCDE1234F (5 letters, 4 digits, 1 letter)
    - Once provided, say: "Great! Let me verify this with our system..."
    """,
            
            "VERIFICATION_COMPLETE": """
    STAGE: POST-VERIFICATION

    - Credit score: {credit_score}
    - Pre-approved limit: ₹{pre_approved}
    - Existing EMIs: ₹{existing_emi}

    Now inform the customer:
    1. Their credit score (if good, congratulate them)
    2. Their pre-approved limit
    3. Ask: "How much would you like to borrow?"
    """,

            "COLLECT_DETAILS": """
    STAGE: LOAN DETAILS COLLECTION
    Customer wants ₹{loan_amount}

    Now collect:
    1. Loan purpose
    2. Preferred tenure
    3. Monthly income
    4. Employment type
    """,

            "UNDERWRITING_COMPLETE": """
    STAGE: DECISION COMMUNICATION
    Result: {decision}
    """,

            "COMPLETE": """
    STAGE: COMPLETION
    - Thank them for choosing LoanFlow AI
    """
    }
    
    # Build core prompt
    prompt = base_prompt.format(stage=stage)
    prompt += stage_instructions.get(stage, "")

    # SAFE: format with missing keys allowed
    safe_context = defaultdict(str, context or {})
    prompt = prompt.format_map(safe_context)

    # Final rules
    prompt += """

    CRITICAL:
    - When you say "let me verify/process/generate", you are HANDING OFF to a Worker Agent
    - After handoff, WAIT for the system to call the agent and return results
    - NEVER make up credit scores, approval decisions, or EMI amounts
    - Only state facts from context

    Respond naturally and conversationally.
    """

    
    return prompt
def process_message(self, user_input, context=None):
        """
        Main orchestration method.
        Returns: (response_text, action_to_take, next_stage)
        
        Actions: None, "VERIFY", "UNDERWRITE", "SANCTION", "COMPLETE"
        """
        
        if not context:
            context = {}
        
        # Build prompt based on current stage
        system_prompt = self.build_system_prompt(self.stage, context)
        
        # Get AI response
        full_prompt = f"{system_prompt}\n\nUser: {user_input}\n\nMr. Finn:"
        ai_response = get_llama_response(full_prompt)
        
        if not ai_response:
            return "I'm having trouble connecting right now. Please try again.", None, self.stage
        
        # Detect stage transitions and actions
        action = None
        next_stage = self.stage
        
        response_lower = ai_response.lower()
        
        # Stage transition logic
        if self.stage == "GREETING":
            if any(word in response_lower for word in ["pan", "verify", "check"]):
                next_stage = "COLLECT_PAN"
        
        elif self.stage == "COLLECT_PAN":
            if any(phrase in response_lower for phrase in ["let me verify", "verify this", "check this"]):
                action = "VERIFY"
                next_stage = "VERIFICATION_COMPLETE"
        
        elif self.stage == "VERIFICATION_COMPLETE":
            if any(word in response_lower for word in ["borrow", "loan amount", "how much"]):
                next_stage = "COLLECT_DETAILS"
        
        elif self.stage == "COLLECT_DETAILS":
            if any(phrase in response_lower for phrase in ["process", "underwriting", "evaluate"]):
                action = "UNDERWRITE"
                next_stage = "UNDERWRITING_COMPLETE"
        
        elif self.stage == "UNDERWRITING_COMPLETE":
            if any(phrase in response_lower for phrase in ["generate", "sanction letter", "create letter"]):
                action = "SANCTION"
                next_stage = "COMPLETE"
        
        self.stage = next_stage
        
        return ai_response, action, next_stage


def format_agent_handoff(agent_name, status="calling"):
    """Format visual indicator for agent handoff"""
    
    icons = {
        "VERIFY": "🔍",
        "UNDERWRITE": "⚖️",
        "SANCTION": "📄"
    }
    
    messages = {
        "VERIFY": "Verification Agent",
        "UNDERWRITE": "Underwriting Agent", 
        "SANCTION": "Sanction Agent"
    }
    
    icon = icons.get(agent_name, "🤖")
    msg = messages.get(agent_name, "Worker Agent")
    
    if status == "calling":
        return f"{icon} **Calling {msg}...**"
    elif status == "complete":
        return f"✅ **{msg} completed**"
    else:
        return f"⚠️ **{msg} encountered an issue**"