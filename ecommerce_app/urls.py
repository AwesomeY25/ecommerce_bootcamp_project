from django.contrib import admin
from django.urls import path
from .views import homepage, product_page, order_list, display_content, order_update_status, cart_page, checkout_page, check_order_status, content_page_list, content_page_edit, confirmation_page, product_form, sales_dashboard, product_search

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', homepage, name='homepage'),
    path('orders/track/', check_order_status, name='check_order_status'),
    path('orders/', order_list, name='order_list'),
    path('orders/update/<int:order_id>/', order_update_status, name='order_update_status'),
    path('sales-dashboard/', sales_dashboard, name='sales_dashboard'),
    path('product/<int:product_id>/', product_page, name='product_page'),
    path('cart/', cart_page, name='cart_page'),
    path('checkout/', checkout_page, name='checkout_page'),
    path('confirmation/', confirmation_page, name='confirmation_page'),
    path('product/new/', product_form, name='product_form'),
    path('pages/', content_page_list, name='content_page_list'),
    path('pages/edit/<slug:slug>/', content_page_edit, name='content_page_edit'),
    path('content/<slug:slug>/', display_content, name='display_content'),
    path('product/search/<str:tags>/', product_search, name='product_search'),
    path('product/search/<str:tags>/price-ascending/', product_search, {'sort_order': 'price_ascending'}, name='product_search_price_ascending'),
    path('product/search/<str:tags>/price-descending/', product_search, {'sort_order': 'price_descending'}, name='product_search_price_descending'),
]