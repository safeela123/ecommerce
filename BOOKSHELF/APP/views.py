from django.shortcuts import render,redirect
from .models import *
from django.contrib.auth.models import User,auth
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
        
def update(request,pk):
    cnames=Category.objects.all()
    lnames=Language.objects.all()
    data=Add.objects.get(pk=pk) #first pk is pk of database,other is of fn
    if request.method=='POST':
        doc = request.FILES.get('file', None)  # Get file safely
        name = request.POST['name']
        price = request.POST['price']
        oldprice = request.POST['old_price']
        discount = request.POST['discount']
        cpk = request.POST['cname']
        lpk = request.POST['lname']
        
        # Fetch the related category and language
        cname = Category.objects.get(pk=cpk)
        lname = Language.objects.get(pk=lpk)
        
        # Update fields and save object
        data.name = name
        data.price = price
        data.oldprice = oldprice
        data.discount = discount
        data.cname = cname
        data.lname = lname
        
        # Update the file only if it's new
        if doc:
            # Optional: remove the old file if it exists and is replaced
            if data.doc:
                data.doc.delete()  # Delete the old file
            
            data.doc = doc  # Assign the new file
        
        data.save() 
        return redirect(adview)

    return render(request,'ad_update.html',{'data':data,'lnames':lnames,'cnames':cnames})

def delete(request,pk):
    Add.objects.filter(pk=pk).delete()
    return redirect(adview)


def index(request):
        
        data=Add.objects.all()
     
        return render(request,'user_index.html',{'data':data})
    
def adindex(request):
    if request.user.is_authenticated:
            cnames=Category.objects.all()
            lnames=Language.objects.all()
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
                return redirect(adview)
    return render(request,'admin_index.html',{'cnames':cnames,'lnames':lnames})

def adview(request):
    if request.user.is_authenticated:
        data=Add.objects.all()
    return render(request,'admin_bookview.html',{'data':data})

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

def adress(request):
    return render(request,'adress.html')


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
