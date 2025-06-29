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
    stock=models.IntegerField(default=1)
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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.TextField()
    email = models.EmailField()
    phone = models.IntegerField()
    wp = models.IntegerField()
    address = models.TextField()
    city = models.TextField()
    district = models.TextField()
    state = models.TextField()
    country = models.TextField()
    pincode = models.IntegerField()
    is_default = models.BooleanField(default=False)  # <- Add this field

    def __str__(self):
        return f"{self.name} - {self.city}"



class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Add, on_delete=models.CASCADE)
    address = models.ForeignKey(adress, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)  # ✅ Added
    amount = models.FloatField()
    order_date = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')  # ✅ Added

    # Razorpay
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    refund_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"
    
    def is_cancellable(self):
        return self.status in ['Pending', 'Paid', 'Processing'] and self.is_paid




class Cartitem(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    item=models.ForeignKey(Add,on_delete=models.CASCADE)
    quantity=models.IntegerField(default=1)

    def Total_price(self):
        return self.item.price * self.quantity
    
    def __str__(self):
        return self.item.name
    
class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query = models.CharField(max_length=255)
    searched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} searched '{self.query}'"                 

class ViewHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Add2, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'product')  # prevent duplicates
        ordering = ['-viewed_at']

    def __str__(self):
        return f"{self.user.username} viewed {self.product.name}"