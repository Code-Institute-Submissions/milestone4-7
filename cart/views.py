from django.shortcuts import render, redirect, reverse
from django.contrib import messages


# Create your views here.
def view_cart(request):
    """A View that renders the cart contents page"""
    return render(request, "cart.html")


def add_to_cart(request, id):
    """Add a quantity of the product, specified by id, to the cart"""
    try:
        quantity = int(request.POST.get('quantity'))
        cart = request.session.get('cart', {})
        cart[id] = cart.get(id, quantity)

        request.session['cart'] = cart
        return redirect(request.META['HTTP_REFERER'])
    except ValueError:
        messages.error(request, "Cannot add a null value quantity to the cart")
        return redirect(request.META['HTTP_REFERER'])


def adjust_cart(request, id):
    """
    Adjust the quantity of the product, specified by id,
    to the specified amount
    """
    try:
        quantity = int(request.POST.get('quantity'))
        cart = request.session.get('cart', {})

        if quantity > 0:
            cart[id] = quantity
        else:
            cart.pop(id)

        request.session['cart'] = cart
        return redirect(reverse('view_cart'))
    except ValueError:
        messages.error(request, "Cannot add a null value quantity to the cart")
        return redirect(request.META['HTTP_REFERER'])
