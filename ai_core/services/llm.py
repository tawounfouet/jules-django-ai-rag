from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain.tools import tool
import json

class LLMService:
    def __init__(self, provider='openai', model_name='gpt-4o'):
        self.provider = provider
        self.model_name = model_name

        # Initialize LLM based on provider
        if provider == 'openai':
            self.llm = ChatOpenAI(model=model_name, temperature=0.0)
        # Add other providers here
        else:
            raise ValueError(f"Provider {provider} not supported")

    def detect_intent_and_generate(self, context_text, history, user_question, available_tools=None):
        """
        Uses Function Calling (Tools) to detect intent or answer directly.
        """

        system_prompt = f"""
        Tu es un assistant IA pour CogniFlow.

        CONTEXTE DE LA BASE DE CONNAISSANCES:
        {context_text}

        Réponds à la question de l'utilisateur en te basant sur le contexte ci-dessus.
        Si l'utilisateur a une intention spécifique (achat, suivi de commande), utilise l'outil approprié.
        Sinon, réponds simplement en texte.
        """

        messages = [SystemMessage(content=system_prompt)]

        # Add history
        for msg in history:
            if msg.get('role') == 'user':
                messages.append(HumanMessage(content=msg.get('content')))
            elif msg.get('role') == 'assistant':
                messages.append(AIMessage(content=msg.get('content')))

        messages.append(HumanMessage(content=user_question))

        # Bind tools if provided
        if available_tools:
            llm_with_tools = self.llm.bind_tools(available_tools)
            response = llm_with_tools.invoke(messages)
        else:
            response = self.llm.invoke(messages)

        return response

# Definition of Intent Tools
# These are schemas that the LLM can "call"

@tool
def create_draft_order_intent(product_name: str = None, quantity: int = 1):
    """Signale une intention d'achat pour créer un brouillon de commande."""
    return "create_order"

@tool
def order_status_intent(order_id: str = None):
    """Signale une intention de suivi de commande."""
    return "order_status"

INTENT_TOOLS = [create_draft_order_intent, order_status_intent]
