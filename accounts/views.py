from django.shortcuts import render, redirect, HttpResponseRedirect
from django.contrib import messages, auth
from django.contrib.auth import update_session_auth_hash
from django.core.urlresolvers import reverse, reverse_lazy
from .forms import (UserLoginForm, UserRegistrationForm, ProfileForm,
                    UserUpdateForm)
from django.template.context_processors import csrf
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from .models import Profile
from checkout.models import Order, OrderLineItem


# Create your views here.
def index(request):
    """A view that displays the index page"""
    return render(request, "index.html")


def logout(request):
    """A view that logs the user out and redirects back to the index page"""
    auth.logout(request)
    messages.success(request, 'You have successfully logged out')
    return redirect(reverse('index'))


def login(request):
    """A view that manages the login form"""
    if request.method == 'POST':
        user_form = UserLoginForm(request.POST)
        if user_form.is_valid():
            user = auth.authenticate(request.POST['username_or_email'],
                                     password=request.POST['password'])

            if user:
                auth.login(request, user)
                messages.error(request, "You have successfully logged in")

                if request.GET and request.GET['next'] != '':
                    next = request.GET['next']
                    return HttpResponseRedirect(next)
                else:
                    return redirect(reverse('index'))
            else:
                user_form.add_error(None,
                                    "Your username or password are incorrect")
    else:
        user_form = UserLoginForm()

    args = {'user_form': user_form, 'next': request.GET.get('next', '')}
    return render(request, 'login.html', args)


@login_required
def profile(request):
    """A view that displays the profile page of a logged in user"""
    try:
        # retrieves the current user
        user_id = request.user.pk
        # retrieves the Profile object associated with current user
        currentprofile = Profile.objects.get(user=user_id)
        # renders profile.html with the Profile info of the current user
        return render(request, 'profile.html', {'profile': currentprofile})
    except Profile.DoesNotExist:
        # renders profile.html without Profile information,
        # typically because user has not yet filled in
        # their profile information
        return render(request, 'profile.html')


def register(request):
    """A view that manages the registration form"""
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            user_form.save()

            user = auth.authenticate(request.POST.get('email'),
                                     password=request.POST.get('password1'))

            if user:
                auth.login(request, user)
                messages.success(request, "You have successfully registered")
                return redirect(reverse('index'))

            else:
                messages.error(request, "unable to log you in at this time!")
    else:
        user_form = UserRegistrationForm()

    args = {'user_form': user_form}
    return render(request, 'register.html', args)


@login_required(login_url=reverse_lazy("login"))
def edit_profile(request):
    """
    view to handle the form for users to enter/edit their profile information
    """
    # retrieves the current user
    user_id = request.user.pk
    if request.method == 'POST':
        baseform = UserUpdateForm(request.POST, user=request.user)
        profile_form = ProfileForm(request.POST)
        if baseform.is_valid() and profile_form.is_valid():
            # save the new email and/or password
            # but only if the user tried to change it!
            data = baseform.cleaned_data
            if baseform.fields["email"].has_changed(request.user.email,
                                                    data["email"]):
                request.user.email = data["email"]
                request.user.save()
            if (baseform.fields["current_password"].
                has_changed(None, data["current_password"]) or
                baseform.fields["new_password1"].
                has_changed(None, data["new_password1"]) or
                baseform.fields["new_password2"].
                    has_changed(None, data["new_password2"])):
                request.user.set_password(data["new_password1"])
                request.user.save()
                update_session_auth_hash(request, request.user)
            # save the profile details and redirects to profile.html
            details = profile_form.save(commit=False)
            details.user = request.user
            try:
                details.save()
                return redirect(profile)
            except IntegrityError:
                # updates the user's Profile info
                # and redirects them back their profile page
                # where they can now view the info they've uploaded.
                details.pk = Profile.objects.get(user=user_id).pk
                details.save()
                messages.success(request,
                                 "You successfully updated your profile")
                return redirect(profile)
        else:
            messages.error(request, "Please correct the highlighted errors:")
    else:
        # display the user's current details, if they exist
        try:
            user_profile = Profile.objects.get(user=user_id)
            profile_form = ProfileForm(instance=user_profile)
        except Profile.DoesNotExist:
            profile_form = ProfileForm()
        baseform = UserUpdateForm(initial={"email": request.user.email})

    args = {"base_form": baseform, "profile_form": profile_form}
    args.update(csrf(request))
    return render(request, "editprofile.html", args)


def delete_profile(request):
    """
    This view renders the deleteprofile page
    where the user must confirm that they wish to delete their user/profile
    """
    # requests the current user
    user = request.user
    if request.method == "POST":
        user.delete()
        # redirects back to the home page
        return redirect(reverse('index'))
    context = {
        "object": user
    }
    return render(request, "deleteprofile.html", context)


def orders(request):
    """A view that displays the orders page"""
    orders = Order.objects.all().order_by('date')
    order_line_items = OrderLineItem.objects.all().order_by('-order')
    return render(request, "orders.html",
                  {'orders': orders, 'order_line_items': order_line_items})
