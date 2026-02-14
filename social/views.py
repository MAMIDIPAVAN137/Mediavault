from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Like, Review, Follow, Favorite
from .serializers import LikeSerializer, ReviewSerializer, FollowSerializer
from media.models import MediaItem
from django.contrib.auth import get_user_model

class LikeToggleAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        media_item = get_object_or_404(MediaItem, pk=pk)
        like, created = Like.objects.get_or_create(user=request.user, media_item=media_item)
        if not created:
            like.delete()
            return Response({'status': 'unliked'}, status=status.HTTP_200_OK)
        return Response({'status': 'liked'}, status=status.HTTP_201_CREATED)

class FavoriteToggleAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        media_item = get_object_or_404(MediaItem, pk=pk)
        fav, created = Favorite.objects.get_or_create(user=request.user, media_item=media_item)
        if not created:
            fav.delete()
            return Response({'status': 'unfavorited'}, status=status.HTTP_200_OK)
        return Response({'status': 'favorited'}, status=status.HTTP_201_CREATED)

class ReviewListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        media_id = self.kwargs.get('pk') # Assuming media_id in URL
        return Review.objects.filter(media_item_id=media_id)

    def perform_create(self, serializer):
        media_item_id = self.kwargs.get('pk')
        media_item = get_object_or_404(MediaItem, pk=media_item_id)
        serializer.save(user=self.request.user, media_item=media_item)

from .models import Like, Review, Follow, Favorite, Notification

class FollowToggleAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        user_to_follow = get_object_or_404(get_user_model(), pk=pk)
        if user_to_follow == request.user:
            return Response({'error': 'You cannot follow yourself.'}, status=status.HTTP_400_BAD_REQUEST)
        
        follow = Follow.objects.filter(follower=request.user, followed=user_to_follow).first()
        
        if follow:
            follow.delete()
            return Response({'status': 'unfollowed'}, status=status.HTTP_200_OK)
        else:
            # Check if user being followed is private
            is_accepted = not user_to_follow.is_private
            follow = Follow.objects.create(
                follower=request.user, 
                followed=user_to_follow,
                is_accepted=is_accepted
            )
            
            # Create notification
            notif_type = 'FOLLOW_REQUEST' if user_to_follow.is_private else 'FOLLOW'
            message = f"{request.user.username} wants to follow you." if user_to_follow.is_private else f"{request.user.username} started following you."
            
            Notification.objects.create(
                recipient=user_to_follow,
                sender=request.user,
                notification_type=notif_type,
                message=message,
                target_url=f"/profile/{request.user.username}/"
            )
            
            status_text = 'request_sent' if user_to_follow.is_private else 'followed'
            return Response({'status': status_text}, status=status.HTTP_201_CREATED)

class NotificationListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(recipient=request.user)[:20]
        data = []
        for n in notifications:
            data.append({
                'id': n.id,
                'type': n.notification_type,
                'message': n.message,
                'is_read': n.is_read,
                'target_url': n.target_url,
                'created_at': n.created_at,
                'sender_id': n.sender.id if n.sender else None
            })
        return Response(data)

class AcceptFollowRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        # pk is the follower ID
        follow = get_object_or_404(Follow, follower_id=pk, followed=request.user, is_accepted=False)
        follow.is_accepted = True
        follow.save()
        
        # Notify follower
        Notification.objects.create(
            recipient=follow.follower,
            sender=request.user,
            notification_type='FOLLOW_ACCEPT',
            message=f"{request.user.username} accepted your follow request.",
            target_url=f"/profile/{request.user.username}/"
        )
        
        # Mark notification as read
        Notification.objects.filter(recipient=request.user, sender_id=pk, notification_type='FOLLOW_REQUEST').update(is_read=True)
        
        return Response({'status': 'accepted'})

class MarkAllNotificationsReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return Response({'status': 'marked_all_read'})

@login_required
def notifications_page(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    # Mark as read when page is opened? User might want to do it manually. 
    # For now, let's just show them.
    return render(request, 'social/notifications.html', {
        'all_notifications': notifications
    })
