from django.shortcuts import render, redirect
from .models import *
import datetime
import os




def practice(request):

    return render(request, "store/practice.html")


def home(request):

    return render(request, "store/jims_store_home.html")


def admin(request):

    products = Product.objects.all()
    for product in products:
        product.display = product.price/100.0
    users = User.objects.all()
    context = {
        "users" : users,
        "products" : products,
    }
    return render(request, "store/admin.html", context)


def view(request, id):

    product = Product.objects.get(id=id)
    product.display = product.price / 100.0
    photos = Photo.objects.filter(product_id=id)
    context = {
        "product" : product,
        "photos" : photos
    }

    return render(request, "store/gallery.html", context)


def cart(request):

    if not "user_id" in request.session.keys():
        if not "cart" in request.session.keys():
            return render(request, "store/jims_store_cart.html")

        total = 0
        print(request.session["cart"])
        users_cart = request.session["cart"]
        for item in users_cart:
            item["product"] = Product.objects.get(id=item["product_id"])
            item["product"].display = item["product"].price / 100.0
            item["total_in_dollars"] = item["product"].price * item["quantity"] / 100.0
            total += item["product"].price * item["quantity"]

        total_in_dollars = total / 100.0
        tax = round(total * 0.0925, 0)
        tax_in_dollars = tax / 100.0
        grand_total = total + tax
        grand_total_in_dollars = grand_total / 100.0

        context = {
            "users_cart" : users_cart,
            "total_in_dollars" : total_in_dollars,
            "grand_total_in_dollars" : grand_total_in_dollars,
            "tax_in_dollars" : tax_in_dollars,
        }
        
    else:
        users_cart = CartItem.objects.filter(user__id=request.session["user_id"])
        total = 0

        for item in users_cart:
            item.product = Product.objects.get(id=item.product_id)
            item.product.display = item.product.price / 100.0
            item.total_in_dollars = item.product.price * item.quantity / 100.0
            total += item.product.price * item.quantity

        total_in_dollars = total / 100.0
        tax = round(total * 0.0925, 0)
        tax_in_dollars = tax / 100.0
        grand_total = total + tax
        grand_total_in_dollars = grand_total / 100.0

        context = {
            "users_cart" : users_cart,
            "total_in_dollars" : total_in_dollars,
            "grand_total_in_dollars" : grand_total_in_dollars,
            "tax_in_dollars" : tax_in_dollars,
        }

    return render(request, "store/jims_store_cart.html", context)


def contact(request):

    return render(request, "store/jims_store_contact_form.html")


def products(request):

    products = Product.objects.all()

    for product in products:
        product.display = product.price/100.0
        if len(product.photos.all()):
            product.first_photo = product.photos.all()[0]

    context = {
        "products" : products
    }

    return render(request, "store/jims_store_products.html", context)


def login_page(request):

    return render(request, "store/jims_store_login.html")


def item_page(request, id):

    product = Product.objects.get(id=id)
    product.display = product.price/100.0
    if product.photos.all():
        product.first_photo = product.photos.all()[0]
        product.pics = product.photos.all()[1:]

    context = {
        "product" : product
    }

    return render(request, "store/jims_store_item_page.html", context)


def reg(request):
    
    errors = User.objects.validate_reg(request.POST)

    if errors:
        for key, val in errors.items():
            messages.info(request, val, extra_tags=key)
        request.session["email"] = request.POST["email"]
        request.session["first_name"] = request.POST["first_name"]
        request.session["last_name"] = request.POST["last_name"]
        request.session["address"] = request.POST["address"]
        request.session["address2"] = request.POST["address2"]
        request.session["city"] = request.POST["city"]
        request.session["state"] = request.POST["state"]
        request.session["zip"] = request.POST["zip"]
        request.session["show"] = "show"

        return redirect("/login_page")    # failure
    else:
        request.session.clear()
        hash_pw = bcrypt.hashpw(request.POST["password"].encode(), bcrypt.gensalt())
        new_user = User.objects.create(first_name=request.POST["first_name"], last_name=request.POST["last_name"], level=1, email=request.POST["email"], password=hash_pw)
        Address.objects.create(user=new_user, address=request.POST["address"], address2=request.POST["address2"], city=request.POST["city"], state=request.POST["state"], zip_code=request.POST["zip"])
        request.session["user_id"] = new_user.id
        request.session["user_name"] = new_user.first_name + " " + new_user.last_name
        request.session["cart_size"] = 0

        return redirect("/products")    # success


def login(request):
    
    result = User.objects.validate_login(request.POST)
    errors = result[0]
    user = result[1]
    if len(errors):
        for val in errors:
            messages.warning(request, val)
            request.session["email"] = request.POST["email"]
        return redirect("/login_page")    # failure
    else:
        request.session["user_id"] = user.id
        request.session["user_name"] = user.first_name + " " + user.last_name
        request.session["secret_key"] = bcrypt.hashpw(str(user.created_at).encode(), bcrypt.gensalt()).decode('utf8')

        if "cart" in request.session.keys():
            users_cart = CartItem.objects.filter(user__id=user.id)

            for item in request.session["cart"]:
                in_cart = False
                for product in users_cart:
                    if item["product_id"] == product.product_id:
                        in_cart = True
                        product.quantity += item["quantity"]
                        product.save()
                if not in_cart:
                    cart_item = CartItem.objects.create(user=user, product_id=item["product_id"], quantity=int(item["quantity"]))

        request.session.pop("cart", None)
        request.session["cart_size"] = len(CartItem.objects.filter(user__id=user.id))
        if user.level == 9:
            return redirect("/admin")
        else:
            return redirect("/products")    # success


def logout(request):

    request.session.clear()

    return redirect("/")


def remove(request, id):

    user = User.objects.get(id=id)
    user.delete()

    return redirect("/admin")


def delete_product(request, id):

    product = Product.objects.get(id=id)
    product.delete()

    return redirect("/admin")


def add_to_cart(request, id):

    if not "user_id" in request.session.keys():

        if not "cart" in request.session.keys():
            request.session["cart"] = []
            request.session["cart_size"] = 0

        in_cart = False
        for item in request.session["cart"]:
            if item["product_id"] == id:
                print(item["product_id"])
                in_cart = True
                print(int(request.POST["quantity"]))
                item["quantity"] += int(request.POST["quantity"])

        if not in_cart:
            context = {
                "product_id" : id,
                "quantity" : int(request.POST["quantity"])
            }
            request.session["cart"].append(context)
            request.session["cart_size"] += 1
        print(request.session["cart"])
    
    else:
        in_cart = False
        user_cart = CartItem.objects.filter(user__id=request.session["user_id"])

        for product in user_cart:

            if product.product_id == id:
                
                in_cart = True
                product.quantity += int(request.POST["quantity"])
                product.save()

                #item = CartItem.objects.get(user=User.objects.get(id=request.session["user_id"]), product_id=id)

        if not in_cart:
            cart_item = CartItem.objects.create(user=User.objects.get(id=request.session["user_id"]), product_id=id, quantity=int(request.POST["quantity"]))
            request.session["cart_size"] += 1

    return redirect("/item_page/%s" % id)


def level(request, id):

    user = User.objects.get(id=id)
    if user.level == 9:
        user.level = 1
    else:
        user.level = 9

    user.save()

    return redirect("/admin")


def in_stock(request, id):

    product = Product.objects.get(id=id)
    if product.in_stock == False:
        product.in_stock = True
    else:
        product.in_stock = False

    product.save()

    return redirect("/admin")



def edit(request, id):

    product = Product.objects.get(id=id)
    request.session["edit_name"] = product.name
    request.session["edit_description"] = product.description
    request.session["edit_price"] = product.price
    request.session["edit_id"] = product.id

    return redirect("/admin")


def new_product(request, id=None):

    if len(request.POST["name"]) and len(request.POST["description"]) and len(request.POST["price"]):
        money = request.POST["price"].split('.')
        dollars = money[0]
        cents = money[1]
        if dollars.isnumeric() and cents.isnumeric() and len(cents) == 2:
            if id: 
                request.session.pop("edit_name", None) 
                request.session.pop("edit_description", None) 
                request.session.pop("edit_price", None)  
                request.session.pop("edit_id", None) 
                x = Product.objects.get(id=id)
                x.name = request.POST["name"]
                x.description = request.POST["description"]
                x.price = int(dollars + cents)
                x.save()
            else:
                Product.objects.create(name=request.POST["name"], description=request.POST["description"], in_stock=False, price=request.POST["price"])

    return redirect("/admin")


def new_photo(request, id):

    if len(request.FILES):
        name = id + str(datetime.datetime.now().microsecond) + ".jpg"
        handle_uploaded_file(request.FILES['image'], name)

        Photo.objects.create(product=Product.objects.get(id=id), image=name)

    return redirect("/view/%s" % id)


def delete_photo(request, id, product_id):

    photo = Photo.objects.get(id=id)
    _delete_file("media/"+str(photo.image))
    photo.delete()

    return redirect("/view/%s" % product_id)


def handle_uploaded_file(file, filename):
    with open('media/' + filename, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)


def _delete_file(path):
    if os.path.isfile(path):
        os.remove(path)


def clear(request):
    request.session.pop("edit_name", None) 
    request.session.pop("edit_description", None) 
    request.session.pop("edit_price", None)  
    request.session.pop("edit_id", None) 
    return redirect("/admin")