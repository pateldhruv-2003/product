from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
from .import views

urlpatterns = [
    path('',views.showproductlist,name="showproductlist"),
    path('addproduct',views.addproduct,name="addproduct"),
    path('delete_product/<int:id>',views.delete_product,name="delete_product"),
    path('edit_product/<int:id>',views.edit_product,name="edit_product"),
    path('cart_view/', views.cart_view,name="cart_view"),
    path('add_to_cart/<int:product_id>',views.add_to_cart,name="add_to_cart"),
    path('logout',views.logout,name="logout"),
    path('login_view',views.login_view,name="login_view"),
    path('register',views.register,name="register"),
    path('update_cart/<int:product_id>/<str:action>/', views.update_cart, name="update_cart"),
    path('delete_from_cart/<int:product_id>', views.delete_from_cart, name="delete_from_cart"),
    path('productdetail/<int:id>',views.productdetail,name="productdetail"),
    path('payment/', views.payment, name='payment'),
    path('payment/callback/', views.payment_callback, name='payment_callback'),
    path('chekout/', views.chekout, name='chekout'),
    
    
]
