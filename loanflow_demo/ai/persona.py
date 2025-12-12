# ai/persona.py

class MasterAgent:
    """
    Conversational Master Agent - Widget-based flow
    """
    
    def __init__(self):
        self.stage = "GREETING"
    
    def get_message(self, stage, context=None):
        """Get agent's message for current stage"""
        
        context = context or {}
        
        messages = {
            "GREETING": "Welcome to LoanFlow AI! I'm Agent Finn, your personal loan assistant. Would you like to apply for a loan today?",
            
            "COLLECT_LOAN_TYPE": "Great! Let me help you find the perfect loan. Please select your loan type and employment status below:",
            
            "COLLECT_AMOUNT": f"Perfect! Now, how much would you like to borrow? Please enter the amount and select your preferred tenure:",
            
            "COLLECT_PAN": "Excellent! To check your eligibility and credit profile, I'll need your PAN number:",
            
            "VERIFICATION_DONE": f"Hi {context.get('name', 'there')}! Great news - your credit score is {context.get('credit_score', 0)}. That's {'excellent' if context.get('credit_score', 0) >= 750 else 'good'}! You're pre-approved for up to ₹{context.get('pre_approved_limit', 0):,}. Let me evaluate your loan now...",
            
            "UNDERWRITING_APPROVED": f"🎉 Congratulations! Your loan is **APPROVED**!\n\n- Monthly EMI: ₹{context.get('emi', 0):,}\n- Interest Rate: {context.get('interest_rate', 0)}%\n- FOIR: {context.get('foir', 0)}%\n\nNow I need to verify your salary slip. Please upload it below:",
            
            "UNDERWRITING_REJECTED": f"I'm sorry, but we cannot approve this loan.\n\n**Reason:** {context.get('reason', 'Eligibility criteria not met')}\n\nTo improve your chances:\n- Improve credit score above 650\n- Reduce existing loan obligations\n- Apply for a lower amount",
            
            "DOCUMENT_REQUIRED": "Please upload your salary slip below to complete the verification:",
            
            "SANCTION_READY": "🎉 Congratulations! Your sanction letter has been generated. You can view and download it below:"
        }
        
        return messages.get(stage, "How can I help you?")
    
    def should_show_widget(self, stage):
        """Check if widgets should be shown for this stage"""
        return stage in ["COLLECT_LOAN_TYPE", "COLLECT_AMOUNT", "COLLECT_PAN", "DOCUMENT_REQUIRED"]
    
    def get_next_stage(self, current_stage, user_action=None):
        """Determine next stage based on current stage and action"""
        
        flow = {
            "GREETING": "COLLECT_LOAN_TYPE",
            "COLLECT_LOAN_TYPE": "COLLECT_AMOUNT",
            "COLLECT_AMOUNT": "COLLECT_PAN",
            "COLLECT_PAN": "VERIFICATION_DONE",
            "VERIFICATION_DONE": "UNDERWRITING",
            "UNDERWRITING": "DOCUMENT_REQUIRED",  # or SANCTION_READY
            "DOCUMENT_REQUIRED": "SANCTION_READY"
        }
        
        return flow.get(current_stage, current_stage)


EXPLANATION_PERSONA = """You are Agent Finn, a friendly loan advisor."""