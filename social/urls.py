from django.urls import path
from .views import (
    LikeToggleAPIView, ReviewListCreateAPIView, FollowToggleAPIView, 
    FavoriteToggleAPIView, NotificationListView, AcceptFollowRequestView,
    MarkAllNotificationsReadView, notifications_page
)

urlpatterns = [
    path('like/<int:pk>/', LikeToggleAPIView.as_view(), name='like-toggle'),
    path('favorite/<int:pk>/', FavoriteToggleAPIView.as_view(), name='favorite-toggle'),
    path('reviews/<int:pk>/', ReviewListCreateAPIView.as_view(), name='review-list-create'),
    path('follow/<int:pk>/', FollowToggleAPIView.as_view(), name='follow-toggle'),
    path('notifications/', NotificationListView.as_view(), name='notifications-list'),
    path('notifications/read-all/', MarkAllNotificationsReadView.as_view(), name='notifications-read-all'),
    path('follow/accept/<int:pk>/', AcceptFollowRequestView.as_view(), name='follow-accept'),
    path('notifications/all/', notifications_page, name='notifications-page'),
]
