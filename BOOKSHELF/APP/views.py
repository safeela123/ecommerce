from django.shortcuts import get_object_or_404, render,redirect
from .models import *
from django.contrib.auth.models import User,auth
from django.db.models import Avg
from django.http import HttpResponse
# Create your views here.
def reg(request):
    if request.method=='POST':
        a=request.POST['name']
        b=request.POST['email']
        c=request.POST['psw']
        d=request.POST['cnf_psw']
        if c==d:
            data=User.objects.create_user(username=a,email=b,password=c)
            data.save()
            return redirect(login)
        else:
            print('cannot register ')
    return render(request,'user_register.html')

def login(request):
    if request.method=='POST':
        name=request.POST['name']
        psw=request.POST['psw']
        user=auth.authenticate(username=name,password=psw)
        if user is not None:
            if user.is_superuser:
                auth.login(request, user)  # Log in the superuser
                return redirect(adindex)  # Redirect to superuser index page
            else:
                auth.login(request, user)  # Log in the regular user
                return redirect(index)  # Redirect to regular user index page
        else:
            return redirect(login)  
    return render(request,'user_login.html')

def logout(request):
 
        if request.user.is_authenticated:
            auth.logout(request)
            return redirect(login)
        else:
            return redirect(login)

def index(request):

    query = request.GET.get('q')
    if query:
        products = Add.objects.filter(name__icontains=query)
    else:
        products = Add.objects.all()
    # return render(request, 'products.html', {'products': products})

        # data=Add.objects.all()
     
    return render(request,'user_index.html',{'data':products})
    
    # book add 1st page : add page

def adindex(request):
    lnames=Language.objects.all()
    cnames=Category.objects.all()
    if request.user.is_authenticated:
            if request.method=='POST':
                doc=request.FILES['file']
                name=request.POST['name']
                price=request.POST['price']
                oldprice=request.POST['old_price']
                discount=request.POST['discount']
                cpk=request.POST['cname']
                lpk=request.POST['lname']
                cname=Category.objects.get(pk=cpk)
                lname=Language.objects.get(pk=lpk)

                data=Add.objects.create(doc=doc,name=name,cname=cname,lname=lname,price=price,oldprice=oldprice,discount=discount)
                data.save()
                return redirect(ad_add2,data.name)
    return render(request,'admin_index.html',{'cnames':cnames,'lnames':lnames})
        
def update(request,pk):
    lnames=Language.objects.all()
    cnames=Category.objects.all()
    data=Add.objects.get(pk=pk) #first pk is pk of database,other is of fn
    if request.method=='POST':
        doc = request.FILES.get('file', None)  # Get file safely
        name = request.POST['name']
        price = request.POST['price']
        oldprice = request.POST['old_price']
        discount = request.POST['discount']
        cname = request.POST.get('cname')
        lname = request.POST.get('lname')
        

        category = Category.objects.get(id=cname)
        language = Language.objects.get(id=lname)


        # Update fields and save object
     
        data.name = name
        data.price = price
        data.oldprice = oldprice    
        data.discount = discount
        data.cname = category
        data.lname = language
        
        # Update the file only if it's new
        if doc:
            # Optional: remove the old file if it exists and is replaced
            if data.doc:
                data.doc.delete()  # Delete the old file
            
            data.doc = doc  # Assign the new file
        
            data.save()
        return redirect('adupdate2',data.name)

    return render(request,'ad_update.html',{'data':data,'lnames':lnames,'cnames':cnames})

def delete(request,name):
    Add.objects.filter(name=name).delete()
    Add2.objects.filter(name=name).delete()
    return redirect(adview)

# book add second page :add2 page


def ad_add2(request,name):  
    data=Add.objects.all()    
    if request.user.is_authenticated:
       if request.method=='POST':
            author=request.POST['author']
            description=request.POST['describe']
            publishdate=request.POST['date']
            edition=request.POST['edition']
            publisher=request.POST['publisher']
            pages=request.POST['pagenumber']
            isbn=request.POST['isbn']
            stock=request.POST['stock']
            binding=request.POST['binding']
            name=request.POST['name']
            book=Add.objects.get(name=name)

            data1=Add2.objects.create(author=author,description=description,publishdate=publishdate,
                                     edition=edition,publisher=publisher,pages=pages,isbn=isbn,stock=stock,binding=binding,book=book)
            data1.save()
            return redirect(adview)
    return render(request,'admin_add2.html',{'data':data})

def update2(request,name):
    # Check if record exists in add2
    book = Add.objects.get(name=name)
    if Add2.objects.filter(book=book).exists():
        data = Add2.objects.get(book=book)

        if request.method == 'POST':
            # Extract form data safely
            
            author = request.POST.get('author')
            description = request.POST.get('describe')
            publishdate = request.POST.get('date')
            edition = request.POST.get('edition')
            publisher = request.POST.get('publisher')
            pages = request.POST.get('pagenumber')
            isbn = request.POST.get('isbn')
            stock = request.POST.get('stock')  # Fixed: was request.POST.get['stock']
            binding = request.POST.get('binding')
            name=request.POST['name']
            book=Add.objects.get(name=name)
            

            # Update the existing record
            data.author = author
            data.description = description
            data.publishdate = publishdate
            data.edition = edition
            data.publisher = publisher
            data.pages = pages
            data.isbn = isbn
            data.stock = stock
            data.binding = binding
            data.book=book
            

            data.save()
           
            return redirect(adview)
           

        return render(request, 'ad_update2.html', {'data':data})

    else:
        # Get data from Add model 
        try:
            data1 = Add.objects.get(name=name)
        except Add.DoesNotExist:
            return HttpResponse("Original record not found.", status=404)
       
        # If the record doesn't exist in add2, create a new one using data from Add
        if request.method == 'POST':
            author = request.POST.get('author')
            description = request.POST.get('describe')
            publishdate = request.POST.get('date')
            edition = request.POST.get('edition')
            publisher = request.POST.get('publisher')
            pages = request.POST.get('pagenumber')
            isbn = request.POST.get('isbn')
            stock = request.POST.get('stock')
            binding = request.POST.get('binding')
            name = request.POST.get('name')

            data2=Add2.objects.create(
                author=author,
                description=description,
                publishdate=publishdate,
                edition=edition,
                publisher=publisher,
                pages=pages,
                isbn=isbn,
                stock=stock,
                binding=binding,
                book=name
                
            )
            data2.save()
            return redirect(adview)
         

        return render(request, 'ad_update2.html', {'data1': data1})

 
# search and book view admin
def adview(request):
    if request.user.is_authenticated:
       query = request.GET.get('q')
    if query:
        products = Add.objects.filter(name__icontains=query)
    else:
        products = Add.objects.all()
    return render(request,'admin_bookview.html',{'data':products})

 # malayalam book category:-

def mlmchildbook(request):
        data=Add.objects.filter(cname__cname="Children's Books",lname__lname="Malayalam")
        print(data)

        return render(request,'mlm_childbook.html',{'data':data})
    
def mlmdetective(request):

    data=Add.objects.filter(cname__cname="Detective Novels",lname__lname="Malayalam")
    return render(request,'mlm_detective.html',{'data':data})

def mlmfiction(request):
    data=Add.objects.filter(cname__cname="Fiction",lname__lname="Malayalam")
    return render(request,'mlm_fiction.html',{'data':data})

def mlmbiography(request):
    data=Add.objects.filter(cname__cname="Biography",lname__lname="Malayalam")
    return render(request,'mlm_biography.html',{'data':data})

def mlmebook(request):
    data=Add.objects.filter(cname__cname="EBooks",lname__lname="Malayalam")
    return render(request,'mlm_ebook.html',{'data':data})

# english book category:-

def engchildbook(request):
        data=Add.objects.filter(cname__cname="Children's Books",lname__lname="English")

        return render(request,'eng_childbook.html',{'data':data})
    
def engdetective(request):

    data=Add.objects.filter(cname__cname="Detective Novels",lname__lname="English")
    return render(request,'eng_detective.html',{'data':data})

def engfiction(request):
    data=Add.objects.filter(cname__cname="Fiction",lname__lname="English")
    return render(request,'eng_detective.html',{'data':data})

def engbiography(request):
    data=Add.objects.filter(cname__cname="Biography",lname__lname="English")
    return render(request,'eng_biography.html',{'data':data})

def engebook(request):
    data=Add.objects.filter(cname__cname="EBooks",lname__lname="English")
    return render(request,'eng_ebook.html',{'data':data})

def order(request):
    return render(request,'order.html')

# -----cart -------

def AddCart(request,item_id):
    if not request.user.is_authenticated:
        return redirect(login)
    
    try:
         item=Add.objects.get(id=item_id)
    except Add.DoesNotExist:
        return HttpResponse("Item not found")
    cart_item, created = Cartitem.objects.get_or_create(user=request.user, item=item)   
    if not created:
        cart_item.quantity += 1
    cart_item.save()
    return redirect(viewcart)

def viewcart(request):
   
    if not request.user.is_authenticated:
        return redirect(login)
    try:
        cart_items = Cartitem.objects.filter(user=request.user)
        total_price = sum(item.Total_price() for item in cart_items)

    except Cartitem.DoesNotExist:
        return HttpResponse("Cart is empty")
    # Pass the cart items and total price to the template
    # You can also handle the case where the cart is empty here if needed
    return render(request, 'viewcart.html', {'cart_items': cart_items, 'total_price': total_price})

def RemoveCart(request, item_id):
    if not request.user.is_authenticated:
        return redirect(login)
    
    try:
        cart_item = Cartitem.objects.get(user=request.user, item__id=item_id)
        cart_item.delete()

    except Cartitem.DoesNotExist:
        return HttpResponse("Item not found in cart")
    
    return redirect(viewcart)  # Redirect to the cart view after removing the item


def update_cart_quantity(request, item_id):
    if not request.user.is_authenticated:
        return redirect(login)  # redirect unauthenticated users

    try:
        item = Cartitem.objects.get(id=item_id, user=request.user)
    except Cartitem.DoesNotExist:
        return HttpResponse("Item not found in your cart.")

    action = request.POST.get('action')

    if action == 'increment':
        item.quantity += 1
    elif action == 'decrement' and item.quantity > 1:
        item.quantity -= 1

    item.save()
    return redirect(viewcart)

# book details page

def bookdetails(request, pk):
    product = get_object_or_404(Add, pk=pk)
    product_details = Add2.objects.get(book=product)

    reviews = product.reviews.all()
    average_rating = reviews.aggregate(avg=Avg('rating'))['avg']

    context = {
        'product': product,
        'product_details': product_details,
        'reviews': reviews,
        'average_rating': average_rating,
        'user_authenticated': request.user.is_authenticated,
    }

    if Review.objects.filter(book_basic=product, user=request.user).exists():
        context['error'] = 'You have already submitted a review for this product.'

    return render(request, 'bookdetails.html', context)  # <--- ALWAYS return a response!

def book_review(request, product_id):
    product = get_object_or_404(Add, id=product_id)

    reviews = product.reviews.all()  # thanks to related_name='reviews'
    average_rating = reviews.aggregate(avg=Avg('rating'))['avg']

    book_detail = product.add2_set.first()  # your existing logic

    if request.method == 'POST':
        if request.user.is_authenticated:
            rating = int(request.POST.get('stars', 0))
            comment = request.POST.get('comment', '').strip()

            if rating < 1 or rating > 5:
                return render(request, 'bookdetails.html', {
                    'product': product,
                    'reviews': reviews,
                    'average_rating': average_rating,
                    'error': 'Invalid rating. Please select a star.',
                    'user_authenticated': True,
                })

            if Review.objects.filter(book_basic=product, user=request.user).exists():
                return render(request, 'bookdetails.html', {
                    'product': product,
                    'reviews': reviews,
                    'average_rating': average_rating,
                    'error': 'You have already submitted a review for this product.',
                    'user_authenticated': True,
                })

            try:
                Review.objects.create(
                    book_basic=product,
                    book_detail=book_detail,
                    user=request.user,
                    rating=rating,
                    comment=comment,
                )
                return redirect('bookdetails', product_id=product.id)
            except Exception as e:
                return render(request, 'bookdetails.html', {
                    'product': product,
                    'reviews': reviews,
                    'average_rating': average_rating,
                    'error': 'An error occurred while saving your review.',
                    'user_authenticated': True,
                })
        else:
            return redirect('login')
    # product = Add.objects.first
    # reviews = product.reviews.all()
    # print("Review count:", reviews.count())
    # print("Ratings:", list(reviews.values_list('rating', flat=True)))
    
    # avg = reviews.aggregate(avg=Avg('rating'))['avg']
    # print("Average rating:", avg)

    return render(request, 'bookdetails.html', {
        'product': product,
        'reviews': reviews,
        'average_rating': average_rating,
        'user_authenticated': request.user.is_authenticated,
    })




# adress page

def adress(request):
    user=request.user
    if not user.is_authenticated:
        return redirect(login)
    if user.is_authenticated:
        if request.method=='POST':
            name=request.POST['name']
            email=request.POST['email']
            phone=request.POST['phone']
            address=request.POST['address']
            city=request.POST['city']
            state=request.POST['state']
            country=request.POST['country']
            pincode=request.POST['pincode']
            wp=request.POST['wp']
            data=adress.objects.create(user=request.user,name=name,email=email,phone=phone,address=address,city=city,state=state,country=country,pincode=pincode,wp=wp)
            data.save()
            return redirect(order)
    return render(request,'adress.html')
