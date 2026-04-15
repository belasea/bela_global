from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Notification, Subscribe
from django.db.models import Q
from django.contrib import messages
import csv
from datetime import datetime


def notification_list(request):
    if request.user.is_authenticated and request.user.is_superuser:
        queryset = Notification.objects.filter(user=request.user).order_by('-id')
        query = request.GET.get('q')
        if query:
            # Using strip method to remove extra white space
            query = query.strip()
            queryset = Notification.objects.filter(
                Q(message__icontains=query) |
                Q(message__istartswith=query) |
                Q(message__endswith=query) |
                Q(user__email__icontains=query)
            ).distinct()
        page = request.GET.get('page')
        paginator = Paginator(queryset, 7)  # 10 posts per page
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        context = {
            'object_list': posts,
            'page': page
        }
        return render(request, 'notification/notification.html', context)
    else:
        messages.add_message(request, messages.WARNING, "Sorry you don't have access this file")
        return redirect('dashboard')
    

def read_notification(request, pk):
    notification = get_object_or_404(Notification, id=pk)

    # Optional: Ensure only owner or superuser can mark it read
    if request.user == notification.user or request.user.is_superuser:
        notification.read = True
        notification.save()

        # Redirect to the actual link
        if notification.link:
            return redirect(notification.link)
    return redirect('notification') 


def delete_notification(request, id):
    obj = get_object_or_404(Notification, pk=id)
    obj.delete()
    messages.add_message(request, messages.WARNING, "Successfully delete notification !")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



def subscribe_list(request):
    if request.user.is_authenticated and request.user.is_superuser:
        queryset = Subscribe.objects.all()
        query = request.GET.get('q')
        if query:
            # Using strip method to remove extra white space
            query = query.strip()
            queryset = Subscribe.objects.filter(
                Q(email__icontains=query) |
                Q(email__istartswith=query) |
                Q(email__endswith=query)
            ).distinct()
        page = request.GET.get('page')
        paginator = Paginator(queryset, 7)  # 10 posts per page
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        context = {
            'object_list': posts,
            'page': page,
            'total_subscribe': queryset.count()
        }
        return render(request, 'notification/subscribe.html', context)
    else:
        messages.add_message(request, messages.WARNING, "Sorry you don't have access this file")
        return redirect('dashboard')



def delete_subscribe(request, id):
    obj = get_object_or_404(Subscribe, pk=id)
    obj.delete()
    messages.add_message(request, messages.WARNING, "Successfully delete subscribe !")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



# Download CSV file subscribe  chunk_size 
def export_subscribe_csv(request):
    chunk_size = 1000  
    queryset = Subscribe.objects.all().values_list('id', 'email',)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="subscribe.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'E-mail',])

    for chunk in range(0, queryset.count(), chunk_size):
        queryset_chunk = queryset[chunk:chunk + chunk_size]
        writer.writerows(queryset_chunk)

    return response


# Download CSV file subscribe list  
def export_subscribe_csv_by_date(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Check if start_date and end_date are not provided
    if not (start_date and end_date):
        messages.warning(request, "Please select both start and end dates.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    # Convert date strings to datetime objects
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    queryset = Subscribe.objects.filter(timestamp__range=(start_date, end_date)).values_list(
        'id', 'email',
    )
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="subscribe.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'E-mail',])
    writer.writerows(queryset)

    return response

