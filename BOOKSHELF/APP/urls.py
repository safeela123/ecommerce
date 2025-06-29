from django.urls import path
from . import views


urlpatterns=[
  path('',views.login,name='login'),
  path('register/',views.reg,name='register'),
  path('index',views.index,name='index'),
  path('adindex',views.adindex),
  path('add2/<name>',views.ad_add2),
  path('adupdate/<int:pk>',views.update),
  path('adupdate2/<name>',views.update2,name='adupdate2'),
  path('addelete/<name>',views.delete),
  path('logout',views.logout,name='logout'),
  path('mlmchild',views.mlmchildbook),
  path('mlmdetective',views.mlmdetective),
  path('mlmfiction',views.mlmfiction),
  path('mlmbiography',views.mlmbiography),
  path('mlmebook',views.mlmebook),
  path('engchild',views.engchildbook),
  path('engdetective',views.engdetective),
  path('engfiction',views.engfiction),
  path('engbiography',views.engbiography),
  path('engebook',views.engebook),
  path('adbookview',views.adview),
  
  # ----order and payment------
   path('order/<int:pk>', views.book_order_view, name='book_order'),   # single order
  path('order_all', views.order_all_view, name='order_all'),          # for cart buy all
  path('payment-success', views.payment_success, name='payment_success'),
  path('adorder_view', views.order_management_view, name='admin_order_management'),
  path('admin_orderupdate/<int:order_id>', views.update_order_status, name='update_order_status'),

  # user order view
  path('userorder_view', views.user_orders, name='user_order_view'),
  path('orders/cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),



  #cart
  path('addcart/<int:item_id>',views.AddCart,name='add_to_cart'),
  path('cart',views.viewcart,name='cart'),
  path('remove/<int:item_id>',views.RemoveCart,name='remove_from_cart'),
  path('cart/update/<int:item_id>', views.update_cart_quantity, name='update_cart_quantity'),



# book details page
path('bookdetails/<int:pk>',views.bookdetails,name='bookdetails'),
path('review/<int:product_id>',views.book_review,name='review'),
# reset password
path('password_reset/', views.password_reset_request, name='password_reset'),
path('password_reset/done/', views.password_reset_done, name='password_reset_done'),
path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
path('reset/done/', views.password_reset_complete, name='password_reset_complete'),
#  stock management

path('dashboard', views.stock_dashboard, name='stock_dashboard'),

# ---------------profile------------------

  path('profile', views.profile_view, name='profile'),
    path('add-address', views.add_address, name='add_address'),
    path('update-address/<int:id>', views.update_address, name='update_address'),
    path('delete-address/<int:id>', views.delete_address, name='delete_address'),
    path('set-default-address/<int:id>', views.set_default_address, name='set_default_address'),

# path('product/<int:product_id>', views.product_detail, name='product_detail'),
  


]


