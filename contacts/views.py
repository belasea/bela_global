import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from notification.models import Notification
from .forms import ContactForm, ReplayContactForm
from .models import Contact
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime
from sea_bright_education.local_settings import BASE_URL


# Contact Page ====================================================
def contact(request):
    """
    Renders the contact form and handles form submission.
    
    Retrieves the latest contact information and processes form submission.
    If the form is valid, saves the data and displays a success message.
    If the form is invalid, displays errors alongside the form.
    """
    form = ContactForm(request.POST or None)
    errors = None
    
    if request.method == 'POST':
        if form.is_valid():
            subject = form.cleaned_data['subject']
            form.save()
            messages.add_message(request, messages.SUCCESS, "Success! Thank you for your message.")
            # Create a notification for the user
            notification_message = f'Created : {subject}'
            try:
                # Set the appropriate link if needed
                link = BASE_URL + "/contact-list"
            except:
                link = None
            notification = Notification(user=request.user, message=notification_message, link=link)
            notification.save()
            return redirect('home')
            # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            errors = form.errors

    context = {
        'form': form,
        'errors': errors
    }
    return render(request, 'contacts/contacts.html', context)


# Contact List CRUD =================================================
def contact_list(request):
    """
    Renders a paginated list of contacts based on the user's permissions and search query.

    Args:
    - request: The HTTP request object.

    Returns:
    - Rendered HTML page displaying a paginated list of contacts.
    """
    posts_list = Contact.objects.order_by("-timestamp")

    query = request.GET.get('q')
    if query:
        query = query.strip()
        posts_list = posts_list.filter(
            Q(subject__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        ).distinct()

    paginator = Paginator(posts_list, 8)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    context = {
        'object_list': posts,
        'page': page,
        'query': query
    }
    return render(request, 'contacts/contact_list/contact-list.html', context)


# Update Obj Contact List ==================================================
def update_contact(request, id):
    """
    Updates contact information based on the provided ID.

    Args:
    - request: The HTTP request object.
    - id: The ID of the contact to be updated.

    Returns:
    - Renders a form to update contact details or redirects to the contact list if the update is successful.
    """
    page = request.GET.get("page")
    
    # Fetch the object or return 404 if not found
    obj = get_object_or_404(Contact, pk=id)
    
    if request.method == "POST":
        form = ContactForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Contact information updated successfully.")
            url = reverse_lazy("contact-list") + "?page=" + str(page)
            return redirect(url)
    else:
        # Use the instance directly for GET requests
        form = ContactForm(instance=obj)

    return render(request, 'contacts/contact_list/contact-update.html', {'form': form})


# Delete Obj Contact List =============================================
def delete_contact(request, id):
    """
    Deletes a contact by its ID.

    Args:
    - request: The HTTP request object.
    - id: The ID of the contact to be deleted.

    Returns:
    - Renders a confirmation page for deleting the contact or redirects to the contact list after deletion.
    - If the user is not a superuser, redirects to the home page with a warning message.
    """
    if not request.user.is_superuser:
        messages.warning(request, "Access restricted: Superuser privileges required.")
        return redirect('home')

    obj = get_object_or_404(Contact, pk=id)
    context = {'obj': obj}

    if request.method == "POST":
        obj.delete()
        messages.warning(request, 'Contact successfully deleted')
        return redirect("contact-list")

    return render(request, "contacts/contact_list/delete-contact.html", context)


# Replay Message to user  ====================================
def replay_contact(request, id):
    """
    Sends a reply message to a specific contact based on the provided ID.

    Args:
    - request: The HTTP request object.
    - id: The ID of the contact to send a reply message.

    Returns:
    - Renders a form to send a reply message or redirects to the contact list after sending the message.
    - If the email host is not configured, displays a warning message.
    - If sending the email fails due to an exception, shows a warning message.
    """
    contact = get_object_or_404(Contact, id=id)

    if request.method == "POST":
        form = ReplayContactForm(request.POST or None)
        if form.is_valid():
            message = form.cleaned_data['message']
            try:
                if not settings.EMAIL_HOST_USER:
                    messages.warning(request, "Email host is not configured. Unable to send message.")
                else:
                    send_mail(contact.subject, message, settings.EMAIL_HOST_USER, [contact.email])
                    messages.success(request, "Your message has been sent successfully.")
                    contact.is_message_send = True
                    contact.save()
                    form.save()
                    return redirect('contact-list')
            except Exception as e:
                messages.warning(request, f"Failed to send email: Email server not configured.")
    else:
        form = ReplayContactForm(initial={'replay': contact})

    context = {
        'form': form,
        'contact': contact
    }
    return render(request, 'contacts/contact_list/replay_form.html', context)


# Download CSV file contact list  chunk_size 
def download_contact_csv(request):
    """
    Downloads a CSV file containing contact information.

    This function retrieves contact data from the database and exports it to a CSV file.
    The CSV file includes columns for 'ID', 'Subject', 'Full Name', 'E-mail', and 'Message'.

    Returns:
    - Downloads a CSV file containing contact information with the specified column headers.
    """
    chunk_size = 1000  # Adjust the chunk size as needed
    queryset = Contact.objects.all().values_list('id', 'subject', 'first_name', 'last_name', 'email', 'message')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="contact-list.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Subject', 'First Name', 'Last Name', 'E-mail', 'Message'])

    for chunk in range(0, queryset.count(), chunk_size):
        queryset_chunk = queryset[chunk:chunk + chunk_size]
        writer.writerows(queryset_chunk)

    return response


# Download CSV file contact list  
def download_contact_csv_by_date(request):
    """
    Downloads a CSV file containing contact information filtered by date.

    This function retrieves contact data based on the provided start_date and end_date.
    It exports the filtered data to a CSV file that includes columns for 'ID', 'Subject',
    'Full Name', 'E-mail', 'Phone', and 'Message'.

    Arguments:
    - request: HTTP request object containing start_date and end_date parameters.

    Returns:
    - Downloads a CSV file containing contact information within the specified date range,
      or redirects with a warning message if start_date or end_date is not provided.
    """
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Check if start_date and end_date are not provided
    if not (start_date and end_date):
        messages.warning(request, "Please select both start and end dates.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    # Convert date strings to datetime objects
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    queryset = Contact.objects.filter(timestamp__range=(start_date, end_date)).values_list(
        'id', 'subject', 'first_name', 'last_name', 'email', 'message'
    )
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="contact-list.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Subject', 'First Name', 'Last Name', 'E-mail', 'Message'])
    writer.writerows(queryset)

    return response

