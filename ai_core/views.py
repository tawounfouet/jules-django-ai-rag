import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404

from core.models import Company
from knowledge.models import KnowledgeBase
from commerce.models import Order, Customer, Product
from .services.vector_store import VectorStoreService
from .services.llm import LLMService, INTENT_TOOLS

class ChatAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data

        # 1. Validate Input
        company_slug = data.get('company_slug')
        kb_id_param = data.get('knowledge_base_id')
        question = data.get('question')
        history = data.get('history', [])

        if not all([company_slug, question]):
            return Response({"error": "Missing company_slug or question"}, status=400)

        # Security check: Ensure user belongs to company or is superuser
        # (Assuming the authenticated user context)
        # For this skeleton, we assume the token identifies the user.
        # We check if user.company matches company_slug

        user = request.user
        if not user.is_staff and (not user.company or user.company.slug != company_slug):
             return Response({"error": "Unauthorized access to this company"}, status=403)

        company = get_object_or_404(Company, slug=company_slug)

        # Resolve KnowledgeBase
        if kb_id_param == 'default' or not kb_id_param:
            kb = KnowledgeBase.objects.filter(company=company, is_default=True).first()
            if not kb:
                # Fallback to any active KB
                kb = KnowledgeBase.objects.filter(company=company, est_active=True).first()
        else:
            kb = get_object_or_404(KnowledgeBase, id=kb_id_param, company=company)

        if not kb:
            return Response({"error": "No knowledge base found"}, status=404)

        # 2. RAG Retrieval
        vector_store = VectorStoreService()
        try:
            results = vector_store.search(
                company_id=company.id,
                knowledge_base_id=kb.id,
                query=question,
                k=3
            )
            # Flatten documents list (Chroma returns [[doc1, doc2]])
            context_docs = results['documents'][0] if results['documents'] else []
            context_text = "\n\n".join(context_docs)
        except Exception as e:
            # Handle case where collection might not exist yet
            context_text = ""
            print(f"Vector search warning: {e}")

        # 3. LLM Call
        llm_service = LLMService(provider='openai') # Default

        # We pass intent tools
        response_msg = llm_service.detect_intent_and_generate(
            context_text=context_text,
            history=history,
            user_question=question,
            available_tools=INTENT_TOOLS
        )

        # 4. Analyze Intent / Response
        answer_text = response_msg.content
        intent_detected = None
        actions = []

        # Check for tool calls
        if response_msg.tool_calls:
            # We take the first tool call as the primary intent
            tool_call = response_msg.tool_calls[0]
            func_name = tool_call['name']
            args = tool_call['args']

            if func_name == 'create_draft_order_intent':
                intent_detected = "intention_achat"
                # Logic to create draft order could go here
                # For now we just return the suggestion action
                actions.append("order_preview")
                # We might want to append a confirmation message to the answer
                if not answer_text:
                    answer_text = "J'ai bien noté votre intention d'achat. Je prépare cela."

            elif func_name == 'order_status_intent':
                intent_detected = "suivi_commande"
                # Logic to fetch order status
                # Here we could actually fetch data if we had the ID, or ask for it.
                actions.append("check_status")

        else:
            intent_detected = "information"

        return Response({
            "answer": answer_text,
            "intent": intent_detected,
            "actions": actions,
            "tool_calls": response_msg.tool_calls if response_msg.tool_calls else None
        })
