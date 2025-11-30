from django.contrib import admin
from django.urls import path
from payment import views
urlpatterns = [
  

    path('create-checkout-session/', views.create_checkout_session, name='stripe_checkout'),
    path('checkout/success/<str:order_id>/', views.checkout_success, name='checkout_success'),
    path('falid_success/', views.falid_success, name='falid_success'),
    path('checkout/info/', views.checkout_info, name='checkout_info'),
    path("product/<int:product_id>/review/", views.create_review, name="create_review"),

]

