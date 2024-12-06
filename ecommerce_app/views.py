from django.shortcuts import render, redirect, get_object_or_404
from .forms import CheckoutForm, ContentPageForm, OrderStatusForm, RefundForm
from .models import Product, Category, Order, OrderItem, ContentPage
from django.http import JsonResponse
from django.db.models import Sum, Avg, Count, Q, F
from datetime import timedelta, date
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
def product_page(request, product_id):
    product = get_object_or_404(Product, id=product_id)  # Handle non-existent products

    if request.method == 'POST':
        # Get product ID and quantity from the form
        quantity = int(request.POST.get('quantity', 1))  # Default to 1 if no quantity is selected
        
        # Add to cart logic (store in session)
        cart = request.session.get('cart', {})  # Get the current cart from session
        
        if str(product_id) in cart:
            # If product already in cart, update quantity
            cart[str(product_id)]['quantity'] += quantity
        else:
            # Add new product to cart
            cart[str(product_id)] = {
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
            total_order_price = 0  # Initialize total order price
            
            # Create an order
            order = Order.objects.create(
                confirmation_number=confirmation_number,
            )

            # Create OrderItems and deduct stock
            for product_id, cart_item in cart_items.items():
                product = get_object_or_404(Product, id=product_id)
                quantity = cart_item['quantity']
                
                # Check if there's enough stock
                if quantity <= product.stock:
                    product.stock -= quantity  # Deduct stock
                    product.save()  # Save the updated product stock

                    # Create an OrderItem
                    order_item = OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=product.price  # Ensure price is passed here
                    )
                    total_order_price += order_item.price * quantity  # Update total order price
                else:
                    # Handle insufficient stock (e.g., return an error message)
                    return render(request, 'ecommerce_app/checkout_page.html', {
                        'form': form,
                        'error': f'Insufficient stock for {product.name}.',
                    })

            # Save the total price to the order
            order.total_price = total_order_price
            order.save()

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
    
def display_content(request, slug):
    # Fetch the content page based on the slug
    content_page = get_object_or_404(ContentPage, slug=slug)
    return render(request, 'ecommerce_app/display_content.html', {'page': content_page})

# View to list all orders
def order_list(request):
    orders = Order.objects.all()
    return render(request, 'ecommerce_app/order_list.html', {'orders': orders})

# View to update order status and issue a refund
def order_update_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        if 'update_status' in request.POST:  # Handle status update
            form = OrderStatusForm(request.POST, instance=order)
            if form.is_valid():
                form.save()
                return redirect('order_list')  # Redirect to order list after update
        elif 'issue_refund' in request.POST:  # Handle refund
            refund_form = RefundForm(request.POST)
            if refund_form.is_valid():
                refund = refund_form.save(commit=False)
                refund.order = order
                refund.save()
                # Optionally, update the order status to 'Refunded'
                order.status = 'Refunded'
                order.save()
                return redirect('order_list')  # Redirect to order list after issuing refund
    else:
        form = OrderStatusForm(instance=order)
        refund_form = RefundForm()

    return render(request, 'ecommerce_app/order_update_status.html', {
        'form': form,
        'refund_form': refund_form,
        'order': order
    })

# Check Order Status
def check_order_status(request):
    order = None
    error_message = None  # Initialize an error message variable

    if request.method == 'POST':
        order_number = request.POST.get('order_number')
        try:
            order = Order.objects.get(confirmation_number=order_number)  # Attempt to retrieve the order
        except Order.DoesNotExist:
            error_message = "No order found with that number. Please check and try again."  # Set error message if order does not exist

    return render(request, 'ecommerce_app/check_order_status.html', {
        'order': order,
        'error_message': error_message  # Pass the error message to the template
    })

# Sales Dashboard
# Sales Dashboard
def sales_dashboard(request):
    # Total Sales, Orders, and Average Order Value
    total_sales = Order.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0
    total_orders = Order.objects.count()
    average_order_value = total_sales / total_orders if total_orders > 0 else 0

    # Revenue Trend (Last Month)
    last_month = date.today() - timedelta(days=30)
    revenue_trend = Order.objects.filter(created_at__gte=last_month).aggregate(Sum('total_price'))['total_price__sum'] or 0

    # Product Performance (with Category and Sales Growth)
    product_performance = (
        OrderItem.objects.values('product__name', 'product__category__name')
        .annotate(
            total_sales=Sum('price'),
            sales_growth=F('price') * 100 / total_sales  # Simplified growth calculation (adjust as needed)
        )
        .order_by('-total_sales')
    )

    # Customer Insights
    total_customers = Order.objects.values('customer_name').distinct().count()
    repeat_customers = (
        Order.objects.values('customer_name')
        .annotate(order_count=Count('id'))
        .filter(order_count__gt=1)
        .count()
    )
    repeat_customer_percentage = (repeat_customers / total_customers * 100) if total_customers > 0 else 0

    avg_customer_spend = total_sales / total_customers if total_customers > 0 else 0

    new_customers_last_month = (
        Order.objects.filter(created_at__gte=last_month)
        .values('customer_name')
        .distinct()
        .count()
    )

    # Top Region (e.g., based on shipping_address) — Adjust field as necessary
    top_region = (
        Order.objects.values('shipping_address')
        .annotate(region_count=Count('id'))
        .order_by('-region_count')
        .first()
    )
    top_region_name = top_region['shipping_address'] if top_region else "Unknown"

    return render(request, 'ecommerce_app/sales_dashboard.html', {
        'total_sales': total_sales,
        'total_orders': total_orders,
        'average_order_value': average_order_value,
        'revenue_trend': revenue_trend,
        'product_performance': product_performance,
        'repeat_customers': round(repeat_customer_percentage, 2),
        'avg_customer_spend': round(avg_customer_spend, 2),
        'new_customers': new_customers_last_month,
        'top_region': top_region_name,
    })

# Process Refund
def process_refund(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        return redirect('order_management')
    return render(request, 'ecommerce_app/refund_form.html', {'order': order})

# Content Management
def content_page_list(request):
    pages = ContentPage.objects.all()
    return render(request, 'ecommerce_app/content_page_list.html', {'pages': pages})

def content_page_edit(request, slug):
    if slug == "new":
        page = ContentPage()  # Create a new instance
    else:
        page = get_object_or_404(ContentPage, slug=slug)

    if request.method == "POST":
        form = ContentPageForm(request.POST, instance=page)
        if form.is_valid():
            form.save()
            return redirect("content_page_list")  # Redirect to the list view after saving
    else:
        form = ContentPageForm(instance=page)

    return render(request, "ecommerce_app/content_page_form.html", {"form": form})

# Confirmation Page View
def confirmation_page(request):
    return render(request, 'ecommerce_app/confirmation_page.html')