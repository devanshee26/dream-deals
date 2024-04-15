import stripe
from .models import Product, Category
from django.conf import settings

from elasticsearch_dsl import Search
from .store_indexes import ProductIndex

from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

stripe.api_key = settings.STRIPE_SECRET_KEY

# Category views
@login_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'categories/category_list.html', {'categories': categories})

@login_required
def category_detail(request, pk):
    try:
        category = Category.objects.get(pk=pk)
        return render(request, 'categories/category_detail.html', {'category': category})
    except Category.DoesNotExist:
        return redirect('category_list')

@login_required
def category_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        category = Category.objects.create(name=name,user=request.user)
        return redirect('category_list')  # Redirect to category list after creation
    else:
        return render(request, 'categories/category_form.html', {'type': 'New '})

@login_required
def category_update(request, pk):
    try:
        category = Category.objects.get(pk=pk)
        print(category)
        if request.method == 'POST':
            name = request.POST.get('name')
            category.name = name
            category.save()
            return redirect('category_list')  # Redirect to category list after update
        else:
            return render(request, 'categories/category_form.html', {'category': category, 'type': 'Edit '})
    except Category.DoesNotExist:
        return redirect('category_list')

@login_required
def category_delete(request, pk):
    try:
        category = Category.objects.get(pk=pk)
        if request.method == 'POST':
            category.delete()
            return redirect('category_list')  # Redirect to category list after deletion
        else:
            return render(request, 'categories/category_confirm_delete.html', {'category': category})
    except Category.DoesNotExist:
        return redirect('category_list')

# Product views
@login_required
def product_list(request):
    search = request.GET.get('q')
    if search:
        s = Search(index='product_index').query('multi_match', query=search, fields=['name', 'description'])
        response = s.execute()
        products = [hit.to_dict() for hit in response.hits]
    else:
        products = Product.objects.all()

    # Pagination
    paginator = Paginator(products, 10)  # Show 10 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'products/product_list.html', {'page_obj': page_obj})

@login_required
def product_detail(request, pk):
    try:
        product = Product.objects.get(pk=pk)
        return render(request, 'products/product_detail.html', {'product': product})
    except Product.DoesNotExist:
        return redirect('product_list')

@login_required
def product_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        # Process categories - assuming it comes as a list of category IDs in POST data
        category_ids = request.POST.getlist('categories')
        print(category_ids)
        categories = Category.objects.filter(pk__in=category_ids)
        product = Product.objects.create(name=name, description=description, price=price, user=request.user)
        product.categories.set(categories)
        return redirect('product_list')  # Redirect to product list after creation
    else:
        categories = Category.objects.all()
        return render(request, 'products/product_form.html', {'categories': categories})

@login_required
def product_update(request, pk):
    try:
        product = Product.objects.get(pk=pk)
        if request.method == 'POST':
            name = request.POST.get('name')
            description = request.POST.get('description')
            price = request.POST.get('price')
            category_ids = request.POST.getlist('categories')
            categories = Category.objects.filter(pk__in=category_ids)
            product.name = name
            product.description = description
            product.price = price
            product.user = request.user
            product.categories.set(categories)
            product.save()
            return redirect('product_list')  # Redirect to product list after update
        else:
            categories = Category.objects.all()
            return render(request, 'products/product_form.html', {'product': product, 'categories': categories})
    except Product.DoesNotExist:
        return redirect('product_list')
    
@login_required
def product_delete(request, pk):
    try:
        product = Product.objects.get(pk=pk)
        if request.method == 'POST':
            product.delete()
            return redirect('product_list')  # Redirect to product list after deletion
        else:
            return render(request, 'products/product_confirm_delete.html', {'product': product})
    except Product.DoesNotExist:
        return redirect('product_list')

# def product_list(request):
#     products = Product.objects.all()

#     # # Index products in Elasticsearch
#     # for product in products:
#     #     ProductIndex(meta={'id': product.id}, **product.__dict__).save()
    
#     # Filtering
#     category = request.GET.get('category')
#     if category:
#         products = products.filter(category=category)
    
#     # Pagination
#     paginator = Paginator(products, 10)  # Show 10 products per page
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)

#     return render(request, 'store/products/product_list.html', {'page_obj': page_obj})

#     # return render(request, 'store/product_list.html', {'products': products})

@login_required
def checkout(request):
    return render(request, 'store/checkout.html')

@login_required
def landing(request):
    return render(request, 'store/landing.html')

@login_required
@require_POST
def charge(request):
    token = request.POST.get('stripeToken')
    amount = 1000  # Amount in cents
    try:
        charge = stripe.Charge.create(
            amount=amount,
            currency='usd',
            description='Example charge',
            source=token,
        )
    except stripe.error.CardError as e:
        return redirect('/checkout/?error')
    return redirect('/checkout/success/')
