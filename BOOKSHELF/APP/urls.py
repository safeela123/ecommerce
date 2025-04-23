from django.urls import path
from . import views


urlpatterns=[
  path('',views.login),
  path('register/',views.reg,name='register'),
  path('index',views.index),
  path('adindex',views.adindex),
  path('adupdate/<int:pk>',views.update),
  path('addelete/<int:pk>',views.delete),
  path('logout',views.logout),
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
  path('order',views.order),
  path('adress',views.adress),
  #cart
  path('addcart/<int:item_id>',views.AddCart,name='add_to_cart'),
  path('cart',views.viewcart,name='cart'),
  path('remove/<int:item_id>',views.RemoveCart,name='remove'),



  


]


