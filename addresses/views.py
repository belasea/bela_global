from django.http.response import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Address
from .forms import shippingForm
import csv


# Address List ========================================================================
def billing_addresses_view(request):
    queryset = Address.objects.all()
    query = request.GET.get('q')

    if query:
        query = query.strip()
        filter_conditions = (
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(email__icontains=query) |
                Q(contact_number__icontains=query) |
                Q(address__icontains=query) |
                Q(city__icontains=query) |
                Q(location__icontains=query)
        )
        queryset = queryset.filter(filter_conditions).distinct()

    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, 10)

    try:
        queryset_page = paginator.page(page)
    except PageNotAnInteger:
        queryset_page = paginator.page(1)
    except EmptyPage:
        queryset_page = paginator.page(paginator.num_pages)

    context = {
        'object_list': queryset_page,
        'query': query
    }

    return render(request, 'addresses/billing_address.html', context)


# Address Create Form ==================================================================================
def address_create_form(request):
    if request.method == "POST":
        form = shippingForm(request.POST or None)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, 'Create new address successfully Created.')
            return redirect('billing-addresses')
    else:
        form = shippingForm()
    context = {
        'form': form
    }
    return render(request, 'addresses/address_update.html', context)


# Address Update Form ==================================================================================
def updated_user_address(request, id):
    # Retrieve the address object based on the provided id
    obj = get_object_or_404(Address, pk=id)

    # Initialize the form with the data from the retrieved address object
    form = shippingForm(instance=obj)

    if request.method == "POST":
        # If a POST request is made, populate the form with the submitted data
        form = shippingForm(request.POST, instance=obj)
        if form.is_valid():
            # Save the updated data and provide a success message
            form.save()
            messages.success(request, 'Address successfully updated.')
            return redirect('billing-addresses')  # Redirect to the billing addresses page

    context = {
        'form': form
    }
    return render(request, 'addresses/address_update.html', context)


# Delete User Address ==========================================================================
def delete_user_address(request, id):
    obj = get_object_or_404(Address, id=id)

    # Check if the address is linked to any orders
    if obj.order_set.exists():
        messages.warning(request, "Please delete the associated orders before deleting the user address.")
        return redirect(request.META.get("HTTP_REFERER"))

    if request.method == "POST":
        obj.delete()
        messages.warning(request, "User address successfully deleted.")
        return redirect("billing-addresses")

    return render(request, "addresses/delete_address.html", {"obj": obj})


# Download All User Address CSV ==================================================================
def all_user_address_csv(request):
    try:
        queryset = Address.objects.all()
        filename = 'user-addresses.csv'
        response = HttpResponse(content_type="text/csv")
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        writer = csv.writer(response)
        writer.writerow([
            'ID', 'First Name', 'Last Name', 'E-mail', 'Phone Number', 'Address Type',
            'Address', 'City', 'Location'
        ])

        for address in queryset:
            row = [
                address.id, address.first_name, address.last_name, address.email,
                address.contact_number, address.address_type, address.address,
                address.city, address.location
            ]
            writer.writerow(row)

        return response

    except Exception as e:
        messages.add_message(request, messages.SUCCESS, "Oops, something went wrong.")
        return redirect('billing-addresses')


# Download User Address CSV ==================================================================
def address_csv_by_date(request):
    try:
        if request.method == "POST":
            start_date = request.POST.get('start-date')
            end_date = request.POST.get('end-date', None)
            queryset = Address.objects.all()
            filename = 'billing-addresses.csv'
            queryset = queryset.address_by_date(start_date, end_date)
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            writer = csv.writer(response)

            writer.writerow([
                'ID', 'First Name', 'Last Name', 'E-mail', 'Phone Number', 'Address Type',
                'Address', 'City', 'Location'
            ])
            for address in queryset:
                row = [
                    address.id, address.first_name, address.last_name, address.email,
                    address.contact_number, address.address_type, address.address,
                    address.city, address.location
                ]
                writer.writerow(row)

            return response
    except Exception as e:
        messages.warning(request, "An error occurred. Please try again.")
        return redirect('billing-addresses')