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
    users = User.objects.all()
    context = {
        "users" : users,
        "products" : products,
    }
    return render(request, "store/admin.html", context)


def view(request, id):

    product = Product.objects.get(id=id)
    photos = Photo.objects.filter(product_id=id)
    context = {
        "product" : product,
        "photos" : photos
    }

    return render(request, "store/gallery.html", context)


def cart(request):

    return render(request, "store/jims_store_cart.html")


def contact(request):

    return render(request, "store/jims_store_contact_form.html")


def products(request):

    products = Product.objects.all()

    for product in products:
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
        new_user = User.objects.create(first_name=request.POST["first_name"], last_name=request.POST["last_name"], level=9, email=request.POST["email"], password=hash_pw)
        Address.objects.create(user=new_user, address=request.POST["address"], address2=request.POST["address2"], city=request.POST["city"], state=request.POST["state"], zip_code=request.POST["zip"])
        request.session["user_id"] = new_user.id
        request.session["user_name"] = new_user.first_name + " " + new_user.last_name

        return redirect("/products")    # success


def login(request):
    
    result = User.objects.validate_login(request.POST)
    errors = result[0]

    if len(errors):
        for val in errors:
            messages.warning(request, val)
            request.session["email"] = request.POST["email"]
        return redirect("/login_page")    # failure
    else:
        request.session.clear()
        request.session["user_id"] = result[1].id
        request.session["user_name"] = result[1].first_name + " " + result[1].last_name
        request.session["secret_key"] = bcrypt.hashpw(str(result[1].created_at).encode(), bcrypt.gensalt()).decode('utf8')
        if result[1].level == 9:
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
        if id: 
            request.session.pop("edit_name", None) 
            request.session.pop("edit_description", None) 
            request.session.pop("edit_price", None)  
            request.session.pop("edit_id", None) 
            x = Product.objects.get(id=id)
            x.name = request.POST["name"]
            x.description = request.POST["description"]
            x.price = request.POST["price"]
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