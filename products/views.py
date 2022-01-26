from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Product, Category


def all_products(request):
    """view to show all products, and sorting and searching """
    # all products - these are displayed if there is no search or filter
    products = Product.objects.all()
    # search query - set to None initially
    query = None
    # category filter - set to None initially
    categories = None

    if request.GET:
        # if category is in the get request (contained in url)
        if 'category' in request.GET:
            # split into a list at the commas
            categories = request.GET['category'].split(',')
            # filter the products by the category name from the list above
            products = products.filter(category__name__in=categories)
            # get the category objects from above list, so can access their fields in the context
            categories = Category.objects.filter(name__in=categories)

        # if q is in the get request (contained in url)
        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse('products'))
            # using Q object to search either in product name or description
            queries = Q(name__icontains=query) | Q(description__icontains=query)
            # filter the products to the ones matching the search
            products = products.filter(queries)

    context = {
        'products': products,
        'search_term': query,
        'current_categories': categories,
    }
    return render(request, 'products/products.html', context)


def product_detail(request, product_id):
    """view to show product details """

    product = get_object_or_404(Product, pk=product_id)
    context = {
        'product': product,
    }
    return render(request, 'products/product_detail.html', context)
