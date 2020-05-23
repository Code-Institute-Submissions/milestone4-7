from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import MakePaymentForm, OrderForm
from .models import OrderLineItem
from django.conf import settings
from django.utils import timezone
from products.models import Product
from accounts.views import index
from accounts.models import Profile
from accounts.forms import ProfileForm
import stripe

# Create your views here.
stripe.api_key = settings.STRIPE_SECRET


@login_required()
def checkout(request):
    user_id = request.user.pk 
    currentprofile = Profile.objects.get(user=user_id)
    profile_form = ProfileForm(initial = {'full_name':currentprofile.full_name})
    if request.method == "POST":
        order_form = OrderForm(request.POST)
        payment_form = MakePaymentForm(request.POST)

        if order_form.is_valid() and payment_form.is_valid():
            order = order_form.save(commit=False)
            order.date = timezone.now()
            order.save()

            cart = request.session.get('cart', {})
            total = 0
            for id, quantity in cart.items():
                product = get_object_or_404(Product, pk=id)
                total += quantity * product.price
                order_line_item = OrderLineItem(
                    order=order,
                    product=product,
                    quantity=quantity
                )
                order_line_item.save()
            
            try:
                customer = stripe.Charge.create(
                    amount=int(total * 100),
                    currency="EUR",
                    description=request.user.email,
                    card=payment_form.cleaned_data['stripe_id']
                )
            except stripe.error.CardError:
                messages.error(request, "Your card was declined!")
            
            if customer.paid:
                messages.error(request, "You have successfully paid")
                request.session['cart'] = {}
                return redirect(reverse('index'))
            else:
                messages.error(request, "Unable to take payment")
        else:
            print(payment_form.errors)
            messages.error(request, "We were unable to take a payment with that card!")
    else:
        payment_form = MakePaymentForm()
        order_form = OrderForm()
    
    # auto-fills name and address information if those details have been completed on Profile page
    try:
        return render(request, "checkout.html", {"order_form": profile_form, "payment_form": payment_form, "publishable": settings.STRIPE_PUBLISHABLE})
        
    except Profile.DoesNotExist:
        return render(request, "checkout.html", {"order_form": order_form, "payment_form": payment_form, "publishable": settings.STRIPE_PUBLISHABLE})