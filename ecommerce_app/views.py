from django.shortcuts import render, redirect, get_object_or_404
from .forms import CheckoutForm
from .models import Product, Category, Order, OrderItem
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import uuid

# Homepage View
def homepage(request):
    categories = Category.objects.all()  # Get all categories
    products = Product.objects.all()  # Get all products
    context = {
        'categories': categories,
        'products': products,
    }
    return render(request, 'ecommerce_app/homepage.html', context)

# Product Page View
# Product Page View
def product_page(request, product_id):
    product = get_object_or_404(Product, id=product_id)  # Handle non-existent products

    if request.method == 'POST':
        # Get product ID and quantity from the form
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))  # Default to 1 if no quantity is selected
        
        # Add to cart logic (store in session)
        cart = request.session.get('cart', {})  # Get the current cart from session
        
        if product_id in cart:
            # If product already in cart, update quantity
            cart[product_id]['quantity'] += quantity
        else:
            # Add new product to cart
            cart[product_id] = {
                'quantity': quantity,
                'price': float(product.price),  # Store product price in cart
                'total': float(product.price) * quantity  # Calculate total for the product
            }

        # Save the updated cart back to the session
        request.session['cart'] = cart
        
        # Redirect to the cart page after adding the product
        return redirect('cart_page')  # Adjust this URL name if necessary

    return render(request, 'ecommerce_app/product_page.html', {'product': product})

# Cart Page View
def cart_page(request):
    if request.method == 'POST':
        # Get the current cart from session
        cart = request.session.get('cart', {})
        
        # Loop through each item in the cart to check if the quantity has been updated
        for product_id in cart.keys():
            new_quantity = request.POST.get(f'quantity_{product_id}')
            if new_quantity:
                new_quantity = int(new_quantity)
                product = get_object_or_404(Product, id=product_id)
                
                # Check if the new quantity is within the available stock
                if new_quantity <= product.stock:
                    cart[product_id]['quantity'] = new_quantity
                    cart[product_id]['total'] = float(cart[product_id]['price']) * new_quantity
        
        # Save the updated cart back to session
        request.session['cart'] = cart

        return redirect('cart_page')  # Redirect back to cart page after updating cart

    # Handle GET request to display cart
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0
    for product_id, cart_item in cart.items():
        product = get_object_or_404(Product, id=product_id)
        cart_items.append({'product': product, 'quantity': cart_item['quantity']})
        total_price += float(cart_item['price']) * cart_item['quantity']

    return render(request, 'ecommerce_app/cart_page.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })
    
# Checkout Page View
def checkout_page(request):
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Generate a unique confirmation number
            confirmation_number = str(uuid.uuid4())  # Generate a unique UUID

            # Process the order here (e.g., save to the database)
            cart_items = request.session.get('cart', {})
            
            # Create an order
            order = Order.objects.create(
                confirmation_number=confirmation_number,
            )

            # Create OrderItems and deduct stock
            for product_id, cart_item in cart_items.items():
                product = get_object_or_404(Product, id=product_id)
                quantity = cart_item['quantity']
                
                # Deduct the stock for each product
                if quantity <= product.stock:
                    product.stock -= quantity  # Deduct stock
                    product.save()  # Save the updated product stock

                    # Create an OrderItem, now passing the price argument correctly
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=product.price  # Ensure price is passed here
                    )

            # Clear the cart after the order is placed
            request.session['cart'] = {}

            # Prepare the confirmation page context
            cart_summary = []
            for product_id, cart_item in cart_items.items():
                product = get_object_or_404(Product, id=product_id)  # Fetch product details
                cart_summary.append({
                    'product_name': product.name,
                    'quantity': cart_item['quantity'],
                    'price': product.price,
                    'item_total': product.price * cart_item['quantity']  # Calculate item total
                })

            return render(request, 'ecommerce_app/confirmation_page.html', {
                'cart': {'items': cart_summary},
                'confirmation_number': confirmation_number
            })
    else:
        form = CheckoutForm()

    # Fetch products for the cart display
    cart_items = request.session.get('cart', {})
    products = Product.objects.filter(id__in=cart_items.keys())  # Get products in cart

    # Calculate total for each item and overall total
    cart_summary = []
    total_price = 0
    for product_id, cart_item in cart_items.items():
        product = get_object_or_404(Product, id=product_id)  # Fetch product details
        item_total = product.price * cart_item['quantity']  # Calculate item total
        total_price += item_total  # Add to overall total

        cart_summary.append({
            'product_name': product.name,
            'quantity': cart_item['quantity'],
            'price': product.price,
            'item_total': item_total  # Store item total for rendering
        })

    return render(request, 'ecommerce_app/checkout_page.html', {
        'form': form,
        'cart': {'items': cart_summary},
        'total_price': total_price,  # Pass the overall total to the template
    })

# Confirmation Page View
def confirmation_page(request):
    return render(request, 'ecommerce_app/confirmation_page.html')
