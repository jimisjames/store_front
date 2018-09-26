from django.db import models
from django.contrib import messages
import re
import bcrypt


class Manager(models.Manager):

    def validate_reg(self, data):

        errors = {}
        emailRegEx = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

        if len(data["email"]) < 1:
            errors["email"] = "Please enter an Email Address"
        elif not emailRegEx.match(data["email"]):
            errors["email"] = "You must enter a valid Email Address"

        already_reg = User.objects.filter(email=data["email"])
        if already_reg:
            errors["email"] = "You are already registered with this Email Address"

        if len(data["password"]) < 1:
            errors["password"] = "Please enter a password"
        elif len(data["password"]) < 8:
            errors["password"] = "Password must be at least 8 characters"

        if len(data["confirm_password"]) < 1:
            errors["confirm_password"] = "Please confirm your password"
        elif data["confirm_password"] != data["password"]:
            errors["password"] = "Your passwords must match"
            errors["confirm_password"] = "Your passwords must match"

        if len(data["first_name"]) < 1:
            errors["first_name"] = "Please enter a first name"
        elif not data["first_name"].isalpha():
            errors["first_name"] = "Names may only contain letters"

        if len(data["last_name"]) < 1:
            errors["last_name"] = "Please enter a last name"
        elif not data["last_name"].isalpha():
            errors["last_name"] = "Names may only contain letters"

        if len(data["address"]) < 1:
            errors["address"] = "Please enter an address"

        if len(data["city"]) < 1:
            errors["address3"] = "Please enter an city"
        elif len(data["state"]) != 2:
            errors["address3"] = "Please enter a valid state abbreviation"
        elif len(data["zip"]) < 5:
            errors["address3"] = "Please enter a zip code"

        return errors

    def validate_login(self, data):

        errors = []
        emailRegEx = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

        if len(data["email"]) < 1:
            errors.append("Please enter an Email Address")
        elif not emailRegEx.match(data["email"]):
            errors.append("You must enter a valid Email Address")

        if len(data["password"]) < 2:
            errors.append("Please enter a password")

        if errors: 
            return [errors, 0]

        user = User.objects.filter(email=data["email"])
        
        if user: 
            user = user[0]
            if not bcrypt.checkpw(data["password"].encode(), user.password.encode()):
                errors.append("Failed to log in, check your email and password")
        else:
            errors.append("Failed to log in, check your email and password")

        return [errors, user]



class User(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    level = models.IntegerField()
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = Manager()


class Address(models.Model):
    user = models.OneToOneField(User, related_name="address", on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    in_stock = models.BooleanField()
    price = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Photo(models.Model):
    product = models.ForeignKey(Product, related_name="photos", on_delete=models.CASCADE)
    image = models.ImageField(upload_to='media')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CartItem(models.Model):
    user = models.ForeignKey(User, related_name="cart_items", on_delete=models.CASCADE)
    product_id = models.CharField(max_length=255)
    quantity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
