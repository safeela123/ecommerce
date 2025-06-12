from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Category(models.Model):
    cname=models.CharField()
    def __str__(self):
        return self.cname

class Language(models.Model):
    lname=models.CharField()
    def __str__(self):
        return self.lname
    

class Add(models.Model):
    doc=models.FileField()
    lname=models.ForeignKey(Language,on_delete=models.CASCADE)
    cname=models.ForeignKey(Category,on_delete=models.CASCADE)
    name=models.TextField()
    price=models.IntegerField()
    oldprice=models.IntegerField()
    discount=models.IntegerField()

class Add2(models.Model):
    author=models.TextField()
    description=models.TextField()
    publishdate=models.DateField(auto_now_add=True)
    edition=models.IntegerField()
    publisher=models.TextField()
    pages=models.IntegerField()
    isbn=models.IntegerField()
    binding=models.TextField()
    stock=models.TextField(default='in stock')
    book = models.ForeignKey(Add, null=True, blank=True, on_delete=models.CASCADE)


class Review(models.Model):
    book_basic = models.ForeignKey(Add, on_delete=models.CASCADE, related_name='reviews')
    book_detail = models.ForeignKey(Add2, on_delete=models.CASCADE, related_name='detailed_reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s review for {self.book_basic.name}"
    
    class Meta:
        unique_together = ('book_basic', 'user')

class adress(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    name=models.TextField()
    email=models.EmailField()
    phone=models.IntegerField()
    address=models.TextField()
    city=models.TextField()
    state=models.TextField()
    country=models.TextField()
    pincode=models.IntegerField()
    wp=models.IntegerField()
    district=models.TextField()


class Cartitem(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    item=models.ForeignKey(Add,on_delete=models.CASCADE)
    quantity=models.IntegerField(default=1)

    def Total_price(self):
        return self.item.price * self.quantity
    
    def __str__(self):
        return self.item.name
