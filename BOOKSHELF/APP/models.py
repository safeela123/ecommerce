from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Language(models.Model):
    lname=models.CharField(max_length=200)

    def __str__(self):
        return self.lname


class Category(models.Model):
    cname=models.CharField(max_length=200)

    def __str__(self):
        return self.cname

class Add(models.Model):
    doc=models.FileField()
    lname=models.ForeignKey(Language,on_delete=models.CASCADE)
    cname=models.ForeignKey(Category,on_delete=models.CASCADE)
    name=models.TextField()
    price=models.IntegerField()
    oldprice=models.IntegerField()
    discount=models.IntegerField()

class Cartitem(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    item=models.ForeignKey(Add,on_delete=models.CASCADE)
    quantity=models.IntegerField(default=1)

    def Total_price(self):
        return self.item.price * self.quantity
    
    def __str__(self):
        return self.item.name
