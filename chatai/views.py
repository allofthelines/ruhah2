from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from chatai.models import ChatSession, ChatMessage, Product
from studio.models import Item  # For reference_item
from accounts.models import CustomUser  # For chat_user
from chatai.utils import get_similar_products
from core.models import Outfit

class AIChatStartView(View):
    """Starter view to create session from params and redirect to clean /aichat/."""
    def get(self, request):
        item_id = request.GET.get('item_id')
        outfit_id = request.GET.get('outfit_id')

        # Create session (stores refs in model)
        session = self.create_session(request, item_id, outfit_id)

        if session:
            request.session['chat_session_id'] = session.id
            return redirect('chatai:aichat')

        return redirect('core:home')

        # old i dont know why
        # return redirect('aichat')  # Clean URL (app_name not needed if no namespace conflict)

    def create_session(self, request, item_id=None, outfit_id=None):
        user = request.user if request.user.is_authenticated else None

        # Safely handle outfit_id: Convert to int or None if empty/invalid
        try:
            outfit_id = int(outfit_id) if outfit_id else None
        except (ValueError, TypeError):
            outfit_id = None  # Ignore invalid values; set to None (allowed by model)

        session = ChatSession.objects.create(
            chat_user=user,
            chat_reference_outfit_id=outfit_id
        )

        if item_id:  # Mode 1: From item
            try:
                item = Item.objects.get(id=item_id)
                session.chat_reference_item = item
                session.chat_main_embedding = item.embedding  # Set main embedding (prefix used)
                session.save()

                # Check max user messages (future-proof; always 0 here)
                if session.messages.filter(msg_is_from_user=True).count() >= 1:
                    messages.warning(request, "Max user input reached for this session.")
                    return session

                # Auto user message (counts as the 1 user bubble)
                ChatMessage.objects.create(
                    msg_chat_session=session,
                    msg_is_from_user=True,
                    msg_text=f"Help me find similar products to Item #{item.id}",
                    msg_image_url=item.image.url if item.image else None,  # Show item image in bubble
                    msg_message_type='item'  # Custom type for future (item-based)
                )

                # Auto Ruhah response with recommendations (uses chat_main_embedding)
                similar = get_similar_products(session.chat_main_embedding)
                ChatMessage.objects.create(
                    msg_chat_session=session,
                    msg_is_from_user=False,
                    msg_text="Here are some similar products:",
                    msg_recommendations=similar,
                    msg_message_type='recommendation'
                )
            except Item.DoesNotExist:
                messages.error(request, "Item not found.")
        else:
            # Virgin session: Auto Ruhah greeting
            ChatMessage.objects.create(
                msg_chat_session=session,
                msg_is_from_user=False,
                msg_text="Hello! How can I help? (Future: Type or upload to search.)"
            )

        return session


class AIChatView(TemplateView):
    template_name = 'chatai/aichat.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session_id = self.request.session.get('chat_session_id')

        if not session_id:
            return redirect('chatai:start_aichat')  # Redirect to starter if no session

        try:
            session = ChatSession.objects.get(id=session_id)
            messages = session.messages.order_by('msg_timestamp')

            # Safer Go Back context: Fetch only if reference_outfit_id exists
            reference_outfit_id = session.chat_reference_outfit_id
            profile_user = None
            if reference_outfit_id:
                try:
                    outfit = Outfit.objects.get(id=reference_outfit_id)
                    profile_user = outfit.maker_id  # Assuming maker_id is the CustomUser (from your views.py)
                except Outfit.DoesNotExist:
                    # Optionally log: print("Outfit not found for ID:", reference_outfit_id)
                    pass  # Skip; button will be hidden via template check

            context.update({
                'messages': messages,
                'can_input': messages.filter(msg_is_from_user=True).count() < 1,  # Max 1 user message
                'reference_outfit_id': reference_outfit_id if profile_user else None,  # Only set if valid profile_user
                'profile_user': profile_user,  # None if invalid/no outfit
            })
        except ChatSession.DoesNotExist:
            return redirect('chatai:start_aichat')  # Reset if session invalid

        return context

    # Future: def post(self, request) for text/send or uploads (check can_input first)
