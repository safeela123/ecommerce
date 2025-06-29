from django.shortcuts import get_object_or_404, render,redirect
from .models import *
from django.contrib.auth.models import User,auth
from django.db.models import Avg
from django.http import HttpResponse
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.timezone import now
import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.paginator import Paginator
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
    if request.method == 'POST':
        username = request.POST['name']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)

        if user is not None:
            auth_login(request, user)

            if user.is_superuser:
                return redirect('stock_dashboard')  # Use name if it's defined in urls.py
            else:
                return redirect(index)    # Use name if it's defined in urls.py
        else:
            messages.error(request, 'Invalid username or password')
            return redirect(login)  # Use string name, not the function itself

    return render(request, 'user_login.html')
def logout(request):
 
        if request.user.is_authenticated:
            auth.logout(request)
            return redirect(login)
        else:
            return redirect(login)


def get_rule_based_recommendations(user, top_n=5):
    viewed_books = ViewHistory.objects.filter(user=user).values_list('product__book', flat=True)
    ordered_books = Order.objects.filter(user=user).values_list('book', flat=True)
    interacted_books = set(viewed_books) | set(ordered_books)

    if not interacted_books:
        return []

    categories = set()
    languages = set()
    authors = set()

    for book_id in interacted_books:
        try:
            book = Add.objects.get(id=book_id)
            categories.add(book.cname)
            languages.add(book.lname)

            # Get related Add2
            add2 = Add2.objects.filter(book=book).first()
            if add2:
                authors.add(add2.author)
        except Exception as e:
            print(f"Error loading book details: {e}")
            continue

    similar_books = Add.objects.filter(
        cname__in=categories,
        lname__in=languages
    ).exclude(id__in=interacted_books)

    book_scores = []
    for book in similar_books:
        try:
            score = 0
            add2 = Add2.objects.filter(book=book).first()

            if add2 and add2.author in authors:
                score += 2
            if book.cname in categories:
                score += 1
            if book.lname in languages:
                score += 1

            book_scores.append((book, score))
        except Exception as e:
            print(f"Error scoring book: {e}")
            continue

    sorted_books = sorted(book_scores, key=lambda x: x[1], reverse=True)
    top_books = [book for book, score in sorted_books[:top_n]]

    return top_books


def index(request):
    query = request.GET.get('q')
    category_id = request.GET.get('category')
    language_id = request.GET.get('language')

    # Start with all books
    books = Add.objects.all()

    # Apply search
    if query:
        books = books.filter(name__icontains=query)
        if request.user.is_authenticated:
            SearchHistory.objects.create(user=request.user, query=query)

    # Apply category filter
    if category_id:
        books = books.filter(cname_id=category_id)

    # Apply language filter
    if language_id:
        books = books.filter(lname_id=language_id)

    # Extra data for dropdowns and recommendations
    categories = Category.objects.all()
    languages = Language.objects.all()

    search_history = []
    view_history = []
    recommendations = []

    if request.user.is_authenticated:
        search_history = SearchHistory.objects.filter(user=request.user).order_by('-searched_at')[:10]
        ViewHistory.objects.filter(product__isnull=True).delete()
        view_history = ViewHistory.objects.filter(user=request.user, product__isnull=False).select_related('product').order_by('-viewed_at')[:10]
        recommendations = get_rule_based_recommendations(request.user)

    context = {
        'books': books,
        'categories': categories,
        'languages': languages,
        'selected_category': int(category_id) if category_id else None,
        'selected_language': int(language_id) if language_id else None,
        'history': search_history,
        'view_history': view_history,
        'recommendations': recommendations,
        'search_query': query,
    }

    return render(request, 'user_index.html', context)


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
    if   Add2.objects.filter(name=name):
        Add2.objects.filter(name=name).delete()
    return redirect(adview)

# book add second page :add2 page


def ad_add2(request,name):  
    data=Add.objects.get(name=name)    
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

# ------------order ---------------

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
 # adjust import if needed
# ----------------single buy --------------------
def book_order_view(request, pk):
    if not request.user.is_authenticated:
        return redirect(login)

    book = get_object_or_404(Add, pk=pk)
    book_detail = get_object_or_404(Add2, book=book)
    quantity = int(request.GET.get('quantity', 1))

    addresses = adress.objects.filter(user=request.user)

    # Stock check on GET
    if book_detail.stock < quantity:
        messages.error(request, f"Only {book_detail.stock} copies available.")
        return redirect('bookdetails', pk=pk)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', quantity))

        # Stock check on POST
        if book_detail.stock < quantity:
            messages.error(request, f"Only {book_detail.stock} copies available.")
            return redirect('book_detail', pk=pk)

        selected_address_id = request.POST.get('selected_address')
        if selected_address_id:
            selected_address = adress.objects.get(id=selected_address_id, user=request.user)
            address_data = {
                'name': selected_address.name,
                'email': selected_address.email,
                'phone': selected_address.phone,
                'wp': selected_address.wp,
                'address': selected_address.address,
                'city': selected_address.city,
                'district': selected_address.district,
                'state': selected_address.state,
                'country': selected_address.country,
                'pincode': selected_address.pincode,
            }
        else:
            # fallback if manual entry
            address_data = {
                'name': request.POST['name'],
                'email': request.POST['email'],
                'phone': request.POST['phone'],
                'wp': request.POST['wp'],
                'address': request.POST['address'],
                'city': request.POST['city'],
                'district': request.POST['district'],
                'state': request.POST['state'],
                'country': request.POST['country'],
                'pincode': request.POST['pincode'],
            }

        request.session['order_data'] = {
            'book_id': book.id,
            'quantity': quantity,
            **address_data,
        }

        amount = int(book.price * quantity * 100)
        display_amount = book.price * quantity

        razorpay_order = razorpay_client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": "1"
        })

        request.session['razorpay_order_id'] = razorpay_order['id']

        return render(request, 'payment.html', {
            'book': book,
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'razorpay_order_id': razorpay_order['id'],
            'display_amount': display_amount,
            'amount': amount,
            'name': address_data['name'],
            'email': address_data['email'],
            'quantity': quantity
        })

    return render(request, 'order_form.html', {
        'book': book,
        'quantity': quantity,
        'addresses': addresses
    })
# -------------- cart all buy -------------------
def order_all_view(request):
    if not request.user.is_authenticated:
        return redirect(login)

    cart_items = Cartitem.objects.filter(user=request.user)
    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('cart')

    if request.method == 'POST':
        # --- Handle Address ---
        selected_address_id = request.POST.get('selected_address')
        if selected_address_id:
            selected_address = adress.objects.get(id=selected_address_id, user=request.user)
            address_data = {
                'name': selected_address.name,
                'email': selected_address.email,
                'phone': selected_address.phone,
                'wp': selected_address.wp,
                'address': selected_address.address,
                'city': selected_address.city,
                'district': selected_address.district,
                'state': selected_address.state,
                'country': selected_address.country,
                'pincode': selected_address.pincode,
            }
        else:
            address_data = {
                'name': request.POST['name'],
                'email': request.POST['email'],
                'phone': request.POST['phone'],
                'wp': request.POST['wp'],
                'address': request.POST['address'],
                'city': request.POST['city'],
                'district': request.POST['district'],
                'state': request.POST['state'],
                'country': request.POST['country'],
                'pincode': request.POST['pincode'],
            }

        # --- Prepare Cart Items ---
        order_items = []
        total_amount = 0
        for item in cart_items:
            order_items.append({'book_id': item.item.id, 'quantity': item.quantity})
            total_amount += item.Total_price()

        # --- Create Razorpay Order ---
        amount_in_paise = int(total_amount * 100)
        razorpay_order = razorpay_client.order.create({
            "amount": amount_in_paise,
            "currency": "INR",
            "payment_capture": "1"
        })

        # --- Save to session for post-payment processing ---
        request.session['pending_order'] = {
            'mode': 'cart',
            'order_id': razorpay_order['id'],
            'items': order_items,
            'amount': total_amount,
            **address_data
        }

        return render(request, 'payment.html', {
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'razorpay_order_id': razorpay_order['id'],
            'amount': amount_in_paise,
            'display_amount': total_amount,
            'user': request.user
        })

    # GET request — show address form
    addresses = adress.objects.filter(user=request.user)
    return render(request, 'order_form_all.html', {
        'addresses': addresses,
        'cart_items': cart_items
    }
    )

@csrf_exempt
def payment_success(request):
    if request.method != "POST":
        return redirect('index')

    user = request.user
    razorpay_order_id = request.POST.get('razorpay_order_id')
    razorpay_payment_id = request.POST.get('razorpay_payment_id')
    razorpay_signature = request.POST.get('razorpay_signature')

    # --- SINGLE BOOK PURCHASE ---
    if 'order_data' in request.session:
        order_data = request.session.pop('order_data')

        book = get_object_or_404(Add, id=order_data['book_id'])
        book_detail = get_object_or_404(Add2, book=book)
        quantity = int(order_data['quantity'])

        if book_detail.stock < quantity:
            messages.error(request, "Insufficient stock.")
            return redirect('index')

        address, created = adress.objects.get_or_create(
            user=user,
            name=order_data['name'],
            email=order_data['email'],
            phone=order_data['phone'],
            wp=order_data['wp'],
            address=order_data['address'],
            city=order_data['city'],
            district=order_data['district'],
            state=order_data['state'],
            country=order_data['country'],
            pincode=order_data['pincode'],
)
        

        Order.objects.create(
            user=user,
            book=book,
            address=address,
            quantity=quantity,
            amount=book.price * quantity,
            is_paid=True,
            status='Paid',
            razorpay_order_id=razorpay_order_id,
            razorpay_payment_id=razorpay_payment_id,
            razorpay_signature=razorpay_signature
        )

        book_detail.stock -= quantity
        book_detail.save()

        request.session.pop('razorpay_order_id', None)

        return render(request, 'payment_success.html', {'book': book})

    # --- CART PURCHASE ---
    elif 'pending_order' in request.session:
        order_data = request.session.pop('pending_order')

        address,created = adress.objects.get_or_create(
            user=user,
            name=order_data['name'],
            email=order_data['email'],
            phone=order_data['phone'],
            wp=order_data['wp'],
            address=order_data['address'],
            city=order_data['city'],
            district=order_data['district'],
            state=order_data['state'],
            country=order_data['country'],
            pincode=order_data['pincode'],
)

        ordered_books = []

        for item in order_data['items']:
            book = get_object_or_404(Add, id=item['book_id'])
            book_detail = get_object_or_404(Add2, book=book)
            quantity = item['quantity']

            if book_detail.stock < quantity:
                continue  # Skip out-of-stock books

            Order.objects.create(
                user=user,
                book=book,
                address=address,
                quantity=quantity,
                amount=book.price * quantity,
                is_paid=True,
                status='Paid',
                razorpay_order_id=razorpay_order_id,
                razorpay_payment_id=razorpay_payment_id,
                razorpay_signature=razorpay_signature
            )

            book_detail.stock -= quantity
            book_detail.save()
            ordered_books.append(book)

        Cartitem.objects.filter(user=user).delete()

        return render(request, 'payment_success.html', {'ordered_books': ordered_books})

    # --- SESSION MISSING ---
    else:
        messages.error(request, "Order session missing or expired.")
        return redirect('cart')




def order_management_view(request):
    if not request.user.is_authenticated:
        return redirect(login)
    if not request.user.is_superuser:
        return redirect('/')
    orders = Order.objects.all().order_by('-id')
    return render(request, 'admin_order_management.html', {'orders': orders})


def update_order_status(request, order_id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect(login)

    if request.method == "POST":
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        if new_status:
            order.status = new_status
            order.save()
    return redirect(order_management_view)


def user_orders(request):
    if not request.user.is_authenticated:
        return redirect(login)

    orders = Order.objects.filter(user=request.user).order_by('-id')
    return render(request, 'user_order.html', {'orders': orders})


def cancel_order(request, order_id):
    if not request.user.is_authenticated:
        return redirect(login)

    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status in ['Pending', 'Paid', 'Processing'] and order.is_paid:
        try:
            refund = razorpay_client.payment.refund(order.razorpay_payment_id, {
                "amount": int(order.amount * 100)
            })

            order.status = 'Cancelled'
            order.refund_id = refund['id']
            order.save()

            # ✅ Restore stock
            book_detail = get_object_or_404(Add2, book=order.book)
            book_detail.stock += order.quantity
            book_detail.save()

            messages.success(request, "Order cancelled and refund initiated.")
        except razorpay.errors.BadRequestError as e:
            messages.error(request, f"Refund failed: {str(e)}")
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")
    else:
        messages.error(request, "This order cannot be cancelled or is already processed.")

    return redirect(user_orders)

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


def bookdetails(request, pk):
    # Get main book info
    product = get_object_or_404(Add, pk=pk)
    
    # Get detailed info from Add2 (assuming Add2 has a OneToOne or ForeignKey to Add)
    product_details = get_object_or_404(Add2, book=product)

    # Track view history
    if request.user.is_authenticated:
        ViewHistory.objects.update_or_create(
            user=request.user,
            product=product_details,  # assuming ViewHistory.product = models.ForeignKey(Add2)
            defaults={'viewed_at': now()}
        )

    # Get all reviews
    reviews = product.reviews.all()
    average_rating = reviews.aggregate(avg=Avg('rating'))['avg']

    context = {
        'product': product,
        'product_details': product_details,
        'reviews': reviews,
        'average_rating': average_rating,
        'user_authenticated': request.user.is_authenticated,
    }

    # Optional: prevent multiple reviews
    if Review.objects.filter(book_basic=product, user=request.user).exists():
        context['error'] = 'You have already submitted a review for this product.'

    return render(request, 'bookdetails.html', context)

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

#------- reset password----------

def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            users = User.objects.filter(email=email)
            for user in users:
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)

                # Build full reset URL
                reset_url = request.build_absolute_uri(
                    reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
                )

                # Send email
                subject = "Reset your password"
                message = render_to_string("password_reset_email.html", {
                    "user": user,
                    "reset_url": reset_url,
                })

                send_mail(subject, message, None, [user.email])

            messages.success(request, "Password reset email has been sent if the email exists.")
            return redirect("password_reset_done")
    else:
        form = PasswordResetForm()

    return render(request, "password_reset_form.html", {"form": form})

def password_reset_done(request):
    return render(request, "password_reset_done.html")

def password_reset_confirm(request, uidb64=None, token=None):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                return redirect("password_reset_complete")
        else:
            form = SetPasswordForm(user)
        return render(request, "password_reset_confirm.html", {"form": form, "validlink": True})
    else:
        return render(request, "password_reset_confirm.html", {"validlink": False})

def password_reset_complete(request):
    return render(request, "password_reset_complete.html")

# --------------    admin stock management dashboard--------------

def stock_dashboard(request):
    query = request.GET.get('q', '')
    selected_category = request.GET.get('category', '')
    selected_language = request.GET.get('language', '')

    books = Add2.objects.select_related('book', 'book__cname', 'book__lname').all()

    if query:
        books = books.filter(book__name__icontains=query)
    if selected_category:
        books = books.filter(book__cname__id=selected_category)
    if selected_language:
        books = books.filter(book__lname__id=selected_language)

    paginator = Paginator(books, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()
    languages = Language.objects.all()

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'languages': languages,
        'query': query,
        'selected_category': selected_category,
        'selected_language': selected_language,
    }
    return render(request, 'stock_dashboard.html', context)

# ---------------------profile ------------------

def profile_view(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Replace with your actual login route name
    addresses = adress.objects.filter(user=request.user)
    return render(request, 'profile.html', {'addresses': addresses})

def add_address(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        _, created = adress.objects.get_or_create(
            user=request.user,
            name=request.POST['name'],
            email=request.POST['email'],
            phone=request.POST['phone'],
            wp=request.POST['wp'],
            address=request.POST['address'],
            city=request.POST['city'],
            district=request.POST['district'],
            state=request.POST['state'],
            country=request.POST['country'],
            pincode=request.POST['pincode']
        )

    return redirect('profile')

def update_address(request, id):
    if not request.user.is_authenticated:
        return redirect('login')
    try:
        addr = adress.objects.get(id=id, user=request.user)
    except adress.DoesNotExist:
        return redirect('profile')
    
    if request.method == 'POST':
        addr.name = request.POST['name']
        addr.email = request.POST['email']
        addr.phone = request.POST['phone']
        addr.wp = request.POST['wp']
        addr.address = request.POST['address']
        addr.city = request.POST['city']
        addr.district = request.POST['district']
        addr.state = request.POST['state']
        addr.country = request.POST['country']
        addr.pincode = request.POST['pincode']
        addr.save()
    return redirect('profile')

def delete_address(request, id):
    if not request.user.is_authenticated:
        return redirect('login')
    adress.objects.filter(id=id, user=request.user).delete()
    return redirect('profile')



def set_default_address(request, id):
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)
    adress.objects.filter(user=request.user).update(is_default=False)
    adress.objects.filter(id=id, user=request.user).update(is_default=True)
    return HttpResponse("Updated")
