from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Notification

def notification_context(request):
    """Context processor providing unread notifications across all templates"""
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(recipient=request.user, isRead=False).count()
        recent_notifications = Notification.objects.filter(recipient=request.user).order_by('-createdAt')[:5]
        return {
            'unread_notifications_count': unread_count,
            'recent_notifications': recent_notifications,
        }
    return {
        'unread_notifications_count': 0,
        'recent_notifications': [],
    }

@login_required
def notification_list(request):
    notifications = Notification.objects.filter(recipient=request.user).select_related('case')
    return render(request, 'notifications/notification_list.html', {'notifications': notifications})

@login_required
def mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.markAsRead()
    if notification.case:
        return redirect('cases:case_detail', pk=notification.case.pk)
    return redirect('notifications:list')

@login_required
def mark_all_read(request):
    Notification.objects.filter(recipient=request.user, isRead=False).update(isRead=True)
    messages.success(request, "সকল নোটিফিকেশন পঠিত হিসেবে চিহ্নিত করা হয়েছে।")
    return redirect('notifications:list')
