from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.db.models.functions import Lower
from .models import Product, Category


def all_products(request):
    """view to show all products, and sorting and searching """
    # all products - these are displayed if there is no search or filter
    products = Product.objects.all()
    # below are all set to None initially. To make sure they are defined when returned
    # to the template when there is no query/categories/sorting etc.
    # search query - set to None initially
    query = None
    # category filter - set to None initially
    categories = None
    # search query - set to None initially
    sort = None
    # category filter - set to None initially
    direction = None

    if request.GET:
        # if sort is in the get request (contained in url)
        if 'sort' in request.GET:
            # set this variable to sort in the get request
            sortkey = request.GET['sort']
            # preserve the orignal field we want to sort on, which is name
            sort = sortkey
            # to allow case insensitive sorting
            if sortkey == 'name':
                sortkey = 'lower_name'
                products = products.annotate(lower_name=Lower('name'))
            if sortkey == 'category':
                # add on the name of the category (from related field)
                # so that when sorted below, it is sorted by category name
                sortkey = 'category__name'
            # if direction is also in the get url
            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    # reverse the order if descending in get request
                    sortkey = f'-{sortkey}'
            # actually sort the products
            products = products.order_by(sortkey)

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
    # how the products are currently sorted - sorting by price/rating/category and asc/desc
    # this will be returned to the template so can use it in the template
    current_sorting = f'{sort}_{direction}'

    context = {
        'products': products,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
    }
    return render(request, 'products/products.html', context)


def product_detail(request, product_id):
    """view to show product details """

    product = get_object_or_404(Product, pk=product_id)
    context = {
        'product': product,
    }
    return render(request, 'products/product_detail.html', context)
