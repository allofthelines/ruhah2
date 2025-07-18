from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from chatai.models import ChatSession, ChatMessage, Product
from studio.models import Item  # For reference_item
from accounts.models import CustomUser  # For chat_user
from chatai.utils import get_similar_products
from core.models import Outfit
from django.views.generic import TemplateView

from django.views.generic import TemplateView
from django.shortcuts import redirect, get_object_or_404

class AIChatStartView(View):
    """Starter view to create session from params and redirect to /aichat/<chat_id>/."""
    def get(self, request):
        item_id = request.GET.get('item_id')
        outfit_id = request.GET.get('outfit_id')

        # Create session (stores refs in model, all old logic stays the same)
        session = self.create_session(request, item_id, outfit_id)

        if session:
            # OLD: request.session['chat_session_id'] = session.id
            # INSTEAD: redirect to the chat with chat_id in url!
            return redirect('chatai:aichat', chat_id=session.chat_id)

        return redirect('core:home')

    def create_session(self, request, item_id=None, outfit_id=None):
        user = request.user if request.user.is_authenticated else None

        # Safely handle outfit_id: Convert to int or None if empty/invalid
        try:
            outfit_id = int(outfit_id) if outfit_id else None
        except (ValueError, TypeError):
            outfit_id = None

        session = ChatSession.objects.create(
            chat_user=user,
            chat_reference_outfit_id=outfit_id
        )

        if item_id:
            try:
                item = Item.objects.get(id=item_id)
                session.chat_reference_item = item
                session.chat_main_embedding = item.embedding  # Set main embedding (prefix used)
                session.save()

                if session.messages.filter(msg_is_from_user=True).count() >= 1:
                    messages.warning(request, "Max user input reached for this session.")
                    return session

                # Auto user message (grey bubble)
                ChatMessage.objects.create(
                    msg_chat_session=session,
                    msg_is_from_user=True,
                    msg_text=f"Help me find similar products to Item #{item.id}",
                    msg_image_url=item.image.url if item.image else None,
                    msg_message_type='item'
                )

                # Auto Ruhah response
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
                msg_text="Hello! How can I help? This is extra long and unecessary text to check the chat bubble appearence. Ignore me!" # Future: Type or upload to search
            )

        return session


class AIChatView(TemplateView):
    template_name = 'chatai/aichat.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        chat_id = self.kwargs.get('chat_id')
        session = get_object_or_404(ChatSession, chat_id=chat_id)  # <--- by chat_id instead of session_id

        messages_queryset = session.messages.order_by('msg_created_at')

        reference_outfit_id = session.chat_reference_outfit_id
        profile_user = None
        if reference_outfit_id:
            try:
                outfit = Outfit.objects.get(id=reference_outfit_id)
                profile_user = outfit.maker_id  # Assuming maker_id is CustomUser
            except Outfit.DoesNotExist:
                pass

        context.update({
            'session': session,  # Add this for convenience
            'messages': messages_queryset,
            'can_input': messages_queryset.filter(msg_is_from_user=True).count() < 1,  # Max 1 user message
            'reference_outfit_id': reference_outfit_id if profile_user else None,
            'profile_user': profile_user,
        })

        # No more redirect on missing session: handled by url pattern now
        return context