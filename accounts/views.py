from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import StreamingHttpResponse
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import RegisterForm, LoginForm, UserUpdateForm
from .models import User
from notification.models import Notification
from bella_global.local_settings import BASE_URL
import csv


def register_view(request):
    """
    Handle user registration.

    Processes the registration form, creates the user,
    shows success or error messages, and creates a notification
    for the newly registered user. Redirects to login on success.
    """

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            email = user.email

            # Success message
            messages.success(request, "Registration successful.")
            # Notification message
            notification_message = f"Account created: {email}"

            # Optional link
            link = f"{BASE_URL}user-list" if 'BASE_URL' in globals() else None

            # Create notification for NEW USER
            Notification.objects.create(
                user=user,
                message=notification_message,
                link=link
            )
            return redirect('login')

        else:
            messages.error(request, "Please fix the errors below.")
            print(form.errors)

    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """
    Handle user login with email and password.

    Authenticates the user, logs them in if active, 
    and displays appropriate messages. Renders the login form on GET or failed login.
    """
    form = LoginForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f"Logged in as {email}.")
                    return redirect('home')
                else:
                    messages.warning(request, "Account inactive. Check your email to activate.")
            else:
                messages.error(request, "Incorrect email or password.")
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    """
    Log out the current user, display a success message, 
    and redirect to the login page.
    """
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('login')


def user_profile(request, id):
    """
    Display and update a user's profile.

    Allows the user to view and edit their own profile using `UserUpdateForm`.
    If the logged-in user tries to access another user's profile, 
    they are redirected to the home page with an error message.

    Handles:
    - GET: Display the profile form with current user data.
    - POST: Validate and save changes, then show a success message.

    Args:
        request (HttpRequest): The HTTP request object.
        id (int): The ID of the user whose profile is being accessed.

    Returns:
        HttpResponse: Renders the profile page with the form, or redirects on unauthorized access or after update.
    """
    user_obj = get_object_or_404(User, pk=id)

    if request.user != user_obj:
        messages.error(request, "You do not have permission to edit this profile.")
        return redirect('home')

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, request.FILES, instance=user_obj)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Your profile has been updated successfully')
            return redirect('user_profile', id=user_obj.id)
    else:
        user_form = UserUpdateForm(instance=user_obj)
    context = {
        'form': user_form,
        'obj': user_obj
    }
    return render(request, 'accounts/profile.html', context)


def user_list(request):
    """
    Display a paginated list of users with optional search functionality.

    - Retrieves all users ordered by email.
    - If a search query ('q') is provided via GET, filters users by
      first name, last name, email, or contact number.
    - Paginates the results, showing 10 users per page.

    Args:
        request (HttpRequest): The HTTP request object, which may contain 
        'q' for search and 'page' for pagination.

    Returns:
        HttpResponse: Renders the 'user_list.html' 
        template with context including the paginated user list, current page, and search query.
    """
    posts_list = User.objects.all().order_by("email")
    query = request.GET.get('q')
    if query:
        query = query.strip()
        posts_list = posts_list.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(email__icontains=query) |
            Q(contact_number__icontains=query)
        ).distinct()

    paginator = Paginator(posts_list, 10)
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
    return render(request, 'accounts/user_list/user_list.html', context)


# Delete Obj Contact List =============================================
def delete_user(request, id):
    """
    Delete a user from the system (superuser only).

    - Only accessible by superusers; non-superusers are redirected to home with a warning.
    - Displays a confirmation page before deletion.
    - On POST, deletes the user and redirects to the user list with a success message.

    Args:
        request (HttpRequest): The HTTP request object.
        id (int): The ID of the user to be deleted.

    Returns:
        HttpResponse: Renders a confirmation template or redirects after deletion.
    """
    if not request.user.is_superuser:
        messages.warning(request, 'Access restricted: Superuser privileges required.')
        return redirect('home')

    obj = get_object_or_404(User, pk=id)
    context = {'obj': obj}

    if request.method == "POST":
        obj.delete()
        messages.warning(request, 'The contact has been successfully deleted.')
        return redirect("user_list")

    return render(request, 'accounts/user_list/delete_user.html', context)



class Echo:
    """
    A pseudo-buffer object that implements only the `write` method.

    Used to stream CSV data row by row without storing it in memory.
    Each call to `write` returns the value, allowing StreamingHttpResponse
    to handle the output efficiently.
    """
    def write(self, value):
        return value

def export_users_csv(request):
    """
    Export all users as a CSV file using a streaming response.

    - Generates CSV data row by row to avoid loading all data into memory.
    - Columns include: ID, Email, First Name, Last Name, Contact Number,
      Gender, Date of Birth, Is Moderator, Profile URL.
    - Returns a StreamingHttpResponse with 'Content-Disposition' header
      to trigger file download.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        StreamingHttpResponse: Streams the CSV file to the client.
    """
    # Define the column headers
    headers = [
        'ID', 'Email', 'First Name', 'Last Name', 'Contact Number',
        'Gender', 'Date of Birth', 'Is Moderator', 'Profile'
    ]

    # Create a generator that yields each row
    def row_generator():
        yield headers
        for user in User.objects.all():
            yield [
                user.id,
                user.email,
                user.first_name,
                user.last_name,
                user.contact_number,
                user.get_gender_display() if user.gender else '',
                user.date_of_birth,
                'Yes' if user.is_moderator else 'No',
                user.profile.url if user.profile else ''
            ]

    # Create a CSV writer that writes to the Echo instance
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)

    # Create a streaming response
    response = StreamingHttpResponse(
        (writer.writerow(row) for row in row_generator()),
        content_type="text/csv"
    )
    response['Content-Disposition'] = 'attachment; filename="users.csv"'
    return response
