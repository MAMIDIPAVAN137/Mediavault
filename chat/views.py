from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import ChatThread, ChatMessage

User = get_user_model()

@login_required
def chat_list(request):
    threads = ChatThread.objects.filter(participants=request.user)
    return render(request, 'chat/chat_list.html', {'threads': threads})

@login_required
def chat_room(request, thread_id):
    thread = get_object_or_404(ChatThread, id=thread_id, participants=request.user)
    messages = thread.messages.all()
    
    # Mark messages as read when opening thread
    ChatMessage.objects.filter(thread=thread, is_read=False).exclude(sender=request.user).update(is_read=True, read_at=timezone_now())
    
    # Get the other participant
    other_user = thread.participants.exclude(id=request.user.id).first()
    
    threads = ChatThread.objects.filter(participants=request.user)
    
    return render(request, 'chat/chat_room.html', {
        'thread': thread,
        'chat_messages': messages,
        'other_user': other_user,
        'threads': threads
    })

@login_required
def start_chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    thread = ChatThread.get_or_create_thread(request.user, other_user)
    if thread:
        return redirect('chat:chat_room', thread_id=thread.id)
    return redirect('chat:chat_list')
@login_required
def upload_chat_media(request, thread_id):
    if request.method == 'POST' and request.FILES.get('file'):
        thread = get_object_or_404(ChatThread, id=thread_id, participants=request.user)
        msg = ChatMessage.objects.create(
            thread=thread,
            sender=request.user,
            content="Sent a file",
            attachment=request.FILES['file']
        )
        return JsonResponse({
            'message_id': msg.id,
            'temp_id': request.POST.get('temp_id'),
            'attachment_url': msg.attachment.url if msg.attachment else None,
            'timestamp': msg.timestamp.strftime('%H:%M'),
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)

from django.http import JsonResponse

# Helper to avoid import error in views for timezone
from django.utils.timezone import now as timezone_now
