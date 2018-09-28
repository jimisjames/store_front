from django.shortcuts import render, redirect
from .models import *
import datetime
import os
import copy

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def practice(request):

    return render(request, "store/practice.html")


def home(request):

    request.session["cart_size"] = 0

    products = Product.objects.exclude(in_stock=False)

    for product in products:
        product.display = product.price/100.0
        if len(product.photos.all()):
            product.first_photo = product.photos.all()[0]

    context = {
        "products" : products
    }

    return render(request, "store/jims_store_home.html", context)


def admin(request):

    if not "user_level" in request.session.keys() or request.session["user_level"] != 9:
        return redirect("/")

    users = User.objects.all().order_by("-level")

    products = Product.objects.all()
    for product in products:
        product.display = product.price/100.0

    orders = OrderLine.objects.raw("SELECT id, order_id, user_email, order_total, status, created_at FROM store_OrderLine GROUP BY order_id;")

    orders = list(reversed(list(orders)))

    for order in orders:
        order.order_total = order.order_total / 100.0

    context = {
        "users" : users,
        "products" : products,
        "orders" : orders
    }

    return render(request, "store/admin.html", context)


def delete_order(request, order_id):

    if "user_level" in request.session.keys() and request.session["user_level"] == 9:

        order = OrderLine.objects.filter(order_id=order_id)
        if len(order):
            for line in order:
                line.delete()

    return redirect("/admin")


def view(request, id):

    if not "user_level" in request.session.keys() or request.session["user_level"] != 9:
        return redirect("/")

    product = Product.objects.get(id=id)
    product.display = product.price / 100.0
    photos = Photo.objects.filter(product_id=id)
    context = {
        "product" : product,
        "photos" : photos
    }

    return render(request, "store/gallery.html", context)


def view_order(request, order_id):

    if not "user_level" in request.session.keys() or request.session["user_level"] != 9:
        return redirect("/")

    order_lines = OrderLine.objects.filter(order_id=order_id)

    order_info = order_lines[0]
    order_info.order_total = order_info.order_total / 100.0

    for line in order_lines:
        line.product_price = line.product_price / 100.0
        line.pre_tax_product_total = line.pre_tax_product_total / 100.0

    context = {
        "order_lines" : order_lines,
        "order_info" : order_info
    }

    return render(request, "store/order.html", context)


def cart(request):

    if not "user_id" in request.session.keys():
        if not "cart" in request.session.keys():
            return render(request, "store/jims_store_cart.html")

        total = 0
        
        users_cart = copy.deepcopy(request.session["cart"])
        for item in users_cart:
            item["product"] = Product.objects.get(id=item["product_id"])
            item["product"].display = item["product"].price / 100.0
            item["total_in_dollars"] = item["product"].price * item["quantity"] / 100.0
            total += item["product"].price * item["quantity"]

        tax = round(total * 0.0925, 0)
        tax_in_dollars = tax / 100.0
        grand_total = total + tax
        grand_total_in_dollars = grand_total / 100.0

        total = str(total)
        total_in_dollars = total[:-2] + "." + total[-2:]
        request.session["total"] = total_in_dollars

        context = {
            "total" : total,
            "total_in_dollars" : total_in_dollars,
            "users_cart" : users_cart,
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

        tax = round(total * 0.0925, 0)
        tax_in_dollars = tax / 100.0
        grand_total = total + tax
        grand_total_in_dollars = grand_total / 100.0

        total = str(total)
        total_in_dollars = total[:-2] + "." + total[-2:]

        if float(total_in_dollars) > 1:
            request.session["total"] = total_in_dollars

        context = {
            "total" : total,
            "total_in_dollars" : total_in_dollars,
            "users_cart" : users_cart,
            "grand_total_in_dollars" : grand_total_in_dollars,
            "tax_in_dollars" : tax_in_dollars,
        }

    if "user_id" in request.session.keys():
        user = User.objects.get(id=request.session["user_id"])
        request.session["email"] = user.email
        request.session["name"] = user.first_name + " " + user.last_name
        request.session["address"] = user.address.address
        request.session["address2"] = user.address.address2
        request.session["city"] = user.address.city
        request.session["state"] = user.address.state
        request.session["zip"] = user.address.zip_code
        request.session["show"] = "show"

    return render(request, "store/jims_store_cart.html", context)


def contact(request):

    return render(request, "store/jims_store_contact_form.html")


def products(request, search=None):

    if search:
        products = Product.objects.filter(name__contains=request.POST["search"])
    else:
        products = Product.objects.exclude(in_stock=False)

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

    products = Product.objects.exclude(in_stock=False)

    for item in products:
        item.display = item.price/100.0
        if len(item.photos.all()):
            item.first_photo = item.photos.all()[0]

    context = {
        "products" : products,
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
        hash_pw = bcrypt.hashpw(request.POST["password"].encode(), bcrypt.gensalt())
        new_user = User.objects.create(first_name=request.POST["first_name"], last_name=request.POST["last_name"], level=1, email=request.POST["email"], password=hash_pw)
        Address.objects.create(user=new_user, address=request.POST["address"], address2=request.POST["address2"], city=request.POST["city"], state=request.POST["state"], zip_code=request.POST["zip"])
    
        print(1)
        if "cart" in request.session.keys():
            print(2)
            for item in request.session["cart"]:
                print(3)
                cart_item = CartItem.objects.create(user=new_user, product_id=item["product_id"], quantity=int(item["quantity"]))

        request.session.clear()
        request.session["user_id"] = new_user.id
        request.session["user_level"] = new_user.level
        request.session["user_name"] = new_user.first_name + " " + new_user.last_name
        request.session["cart_size"] = len(CartItem.objects.filter(user__id=new_user.id))

        return redirect("/products")    # success


def login(request, checkout=False):
    
    result = User.objects.validate_login(request.POST)
    errors = result[0]
    user = result[1]
    if len(errors):
        for val in errors:
            messages.warning(request, val)
            request.session["email"] = request.POST["email"]
        if checkout:
            return redirect("/cart")
        else:
            return redirect("/login_page")    # failure
    else:
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

        request.session.clear()
        request.session["user_id"] = user.id
        request.session["user_name"] = user.first_name + " " + user.last_name
        request.session["user_level"] = user.level
        request.session["cart_size"] = len(CartItem.objects.filter(user__id=user.id))

        if user.level == 9:
            return redirect("/admin")
        else:
            if checkout:
                return redirect("/cart")
            else:
                return redirect("/products")    # success


def logout(request):

    request.session.clear()

    return redirect("/")


def remove(request, id):

    if not "user_level" in request.session.keys() or request.session["user_level"] != 9:
        return redirect("/")

    user = User.objects.get(id=id)
    user.delete()

    return redirect("/admin")


def delete_product(request, id):

    if not "user_level" in request.session.keys() or request.session["user_level"] != 9:
        return redirect("/")

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
                in_cart = True
                item["quantity"] += int(request.POST["quantity"])

        if not in_cart:
            context = {
                "product_id" : id,
                "quantity" : int(request.POST["quantity"])
            }
            request.session["cart"].append(context)
            request.session["cart_size"] += 1
    
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

    return redirect("/products")
    #return redirect("/item_page/%s" % id)


def remove_item(request, id):
    
    if "user_id" in request.session.keys():
        cart_item = CartItem.objects.get(user=User.objects.get(id=request.session["user_id"]), product_id = id)
        cart_item.delete()
    else:
        x = []
        for item in request.session["cart"]:
            if item["product_id"] != id:
                x.append(item)
        request.session["cart"] = x

    request.session["cart_size"] -= 1

    return redirect("/cart")


def level(request, id):

    if not "user_level" in request.session.keys() or request.session["user_level"] != 9:
        return redirect("/")

    user = User.objects.get(id=id)
    if user.level == 9:
        user.level = 1
    else:
        user.level = 9

    user.save()

    return redirect("/admin")


def in_stock(request, id):

    if not "user_level" in request.session.keys() or request.session["user_level"] != 9:
        return redirect("/")

    product = Product.objects.get(id=id)
    if product.in_stock == False:
        product.in_stock = True
    else:
        product.in_stock = False

    product.save()

    return redirect("/admin")



def edit(request, id):

    if not "user_level" in request.session.keys() or request.session["user_level"] != 9:
        return redirect("/")

    product = Product.objects.get(id=id)
    request.session["edit_name"] = product.name
    request.session["edit_description"] = product.description
    request.session["edit_price"] = float(product.price) /100
    request.session["edit_id"] = product.id

    return redirect("/admin")


def new_product(request, id=None):

    if not "user_level" in request.session.keys() or request.session["user_level"] != 9:
        return redirect("/")

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
                price = float(request.POST["price"])*100
                Product.objects.create(name=request.POST["name"], description=request.POST["description"], in_stock=False, price=price)

    return redirect("/admin")


def new_photo(request, id):

    if not "user_level" in request.session.keys() or request.session["user_level"] != 9:
        return redirect("/")

    if len(request.FILES):
        name = id + str(datetime.datetime.now().microsecond) + ".jpg"
        handle_uploaded_file(request.FILES['image'], name)

        Photo.objects.create(product=Product.objects.get(id=id), image=name)

    return redirect("/view/%s" % id)


def handle_uploaded_file(file, filename):
    with open('media/' + filename, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)


def _delete_file(path):
    if os.path.isfile(path):
        os.remove(path)


def delete_photo(request, id, product_id):

    if not "user_level" in request.session.keys() or request.session["user_level"] != 9:
        return redirect("/")

    photo = Photo.objects.get(id=id)
    _delete_file("media/"+str(photo.image))
    photo.delete()

    return redirect("/view/%s" % product_id)


def clear(request):
    request.session.pop("edit_name", None) 
    request.session.pop("edit_description", None) 
    request.session.pop("edit_price", None)  
    request.session.pop("edit_id", None) 
    return redirect("/admin")


def checkout(request):

    errors = User.objects.validate_checkout(request.POST)

    if len(errors):
        for key, val in errors.items():
            messages.info(request, val, extra_tags=key)
        request.session["email"] = request.POST["email"]
        request.session["name"] = request.POST["name"]
        request.session["address"] = request.POST["address"]
        request.session["address2"] = request.POST["address2"]
        request.session["city"] = request.POST["city"]
        request.session["state"] = request.POST["state"]
        request.session["zip"] = request.POST["zip"]
        request.session["show"] = "show"

        return redirect("/cart")    #failure
    
    if not "user_id" in request.session.keys():
        if not "cart" in request.session.keys():
            request.session["email"] = request.POST["email"]
            request.session["name"] = request.POST["name"]
            request.session["address"] = request.POST["address"]
            request.session["address2"] = request.POST["address2"]
            request.session["city"] = request.POST["city"]
            request.session["state"] = request.POST["state"]
            request.session["zip"] = request.POST["zip"]
            request.session["show"] = "show"
            messages.info(request, "There are no items in your cart!", extra_tags="address3")
            return redirect("/cart")    #failure
        else:
            order_number = datetime.datetime.now().strftime("%Y%m%d%S%f")
            for item in request.session["cart"]:
                price = Product.objects.get(id=item["product_id"]).price
                
                order_line = OrderLine.objects.create(
                    user=None, 
                    user_email=request.POST["email"],
                    order_id=order_number, 
                    product_id=item["product_id"], 
                    product_name=Product.objects.get(id=item["product_id"]).name,
                    product_price=price, 
                    quantity=item["quantity"], 
                    pre_tax_product_total=item["quantity"] * price, 
                    pre_tax_order_total=request.POST["order_total"],
                    order_total = int(int(request.POST["order_total"]) * 1.0925),
                    status="Placed",
                    ship_to=(request.POST["address"]+" "+request.POST["address2"]+" "+request.POST["city"]+" "+request.POST["state"]+" "+request.POST["zip"])
                    )
            order = OrderLine.objects.filter(order_id=order_number)
            
            request.session["order_number"] = order_number
            request.session["paypal"] = "paypal"
            request.session.pop("cart", None)
            request.session["cart_size"] = 0
            return redirect("/cart")    #Success

    else:
        cart = CartItem.objects.filter(user__id=request.session["user_id"])
        
        if not len(cart):
            messages.info(request, "There are no items in your cart!", extra_tags="address3")
            return redirect("/cart")    #failure
        else:

            order_number = datetime.datetime.now().strftime("%Y%m%d%S%f")
            for item in cart:
                price = Product.objects.get(id=item.product_id).price
                
                order_line = OrderLine.objects.create(
                    user=None, 
                    user_email=request.POST["email"],
                    order_id=order_number, 
                    product_id=item.product_id, 
                    product_name=Product.objects.get(id=item.product_id).name,
                    product_price=price, 
                    quantity=item.quantity, 
                    pre_tax_product_total=item.quantity * price, 
                    pre_tax_order_total=request.POST["order_total"],
                    order_total = int(int(request.POST["order_total"]) * 1.0925),
                    status="Placed",
                    ship_to=(request.POST["address"]+" "+request.POST["address2"]+" "+request.POST["city"]+" "+request.POST["state"]+" "+request.POST["zip"])
                    )
                item.delete()

            order = OrderLine.objects.filter(order_id=order_number)

            request.session["order_number"] = order_number
            request.session["paypal"] = "paypal"
            request.session["cart_size"] = 0

            return redirect("/cart")    #Success


def status(request, order_id):

    if "user_level" in request.session.keys():

        if request.session["user_level"] == 9 and len(request.POST["status"]):

            order = OrderLine.objects.filter(order_id=order_id)
            if len(order):
                for line in order:
                    line.status = request.POST["status"]
                    line.save()

    return redirect("/view/order/%s" % order_id)


def email(request):

    server = smtplib.SMTP(host='smtp.gmail.com', port=587)
    server.starttls()
    server.login("James.Lambert11111@gmail.com", "jimiscool3")
    context = {
        "subject" : request.POST["reason"],
        "message" : request.POST["message"]+" FROM "+request.POST["email"]
    }
    msg = MIMEMultipart()
    msg['From'] = "James.Lambert11111@gmail.com"
    msg['To'] = "james.lambert1@hotmail.com"
    msg['Subject'] = context["subject"]
    msg.attach(MIMEText(context["message"], 'plain'))

    server.send_message(msg)
    del msg
    server.quit()

    messages.info(request, "Thank you for contacting us! We will reply ASAP!")

    return redirect("/contact")