from django.shortcuts import render, redirect, reverse, HttpResponse, get_object_or_404
from django.contrib import messages
from products.models import Product


def view_bag(request):
    """view to return bag contents page """
    return render(request, 'bag/bag.html')


def add_to_bag(request, item_id):
    """Add a quantity of the specified product to the shopping bag"""
    product = get_object_or_404(Product, pk=item_id)

    # quantity from the form, convert to integer as will come from template as string
    quantity = int(request.POST.get('quantity'))
    # get the redirect url from the hidden form input - so can redirect after
    redirect_url = request.POST.get('redirect_url')
    size = None
    # set size to size from the form, if it is there
    if 'product_size' in request.POST:
        size = request.POST['product_size']

    # shopping bag to be held in session storage
    # get the bag variable if it exists, or create empty dictionary for it if not there
    bag = request.session.get('bag', {})
    # if a product with sizes is being added
    if size:
        # if the item is already in the bag
        if item_id in list(bag.keys()):
            # if same item id and same size already in bag
            if size in bag[item_id]['items_by_size'].keys():
                # then increase the quantity
                bag[item_id]['items_by_size'][size] += quantity
                messages.success(
                    request,
                    f'Updated size {size.upper()} {product.name} quantity to {bag[item_id]["items_by_size"][size]}'
                    )
            else:
                # item already exists but a different size, so adding a new size for that item
                bag[item_id]['items_by_size'][size] = quantity
                messages.success(request, f'Added size {size.upper()} {product.name} to your bag')
        else:
            # if not already in bag
            # add it as a dictionary with a key of items by size
            # so can have multiple of same item_id but with different sizes
            bag[item_id] = {'items_by_size': {size: quantity}}
            messages.success(request, f'Added size {size.upper()} {product.name} to your bag')

    else:
        # the original code - check if item in bag
        # if item already in bag, increase quantity
        if item_id in list(bag.keys()):
            bag[item_id] += quantity
            messages.success(request, f'Updated {product.name} quantity to {bag[item_id]}')
        else:
            # otherwise create key of the item id, set it equal to the quantity
            bag[item_id] = quantity
            messages.success(request, f'Added {product.name} to your bag')
    # put bag variable into session dictionary, (overwrite the variable in session
    # with updated version, if it existed before this)
    request.session['bag'] = bag
    # return user to the url that came from the 'redirect_url' form input(hidden)
    return redirect(redirect_url)


def adjust_bag(request, item_id):
    """Adjust quantity of the specified product to the specified amount"""
    product = get_object_or_404(Product, pk=item_id)
    # quantity from the form, convert to integer as will come from template as string
    quantity = int(request.POST.get('quantity'))
    size = None
    # set size to size from the form, if it is there
    if 'product_size' in request.POST:
        size = request.POST['product_size']
    # shopping bag to be held in session storage
    # get the bag variable if it exists, or create empty dictionary for it if not there
    bag = request.session.get('bag', {})
    print(bag)

    # if a product with sizes is being adjusted (this is adjusting item already in bag)
    if size:
        # if quantity greater than 0, adjust it to the new quantity, otherwise remove item
        # drill into items_by_size dict, find the size and update that quantity/delete it
        if quantity > 0:
            bag[item_id]['items_by_size'][size] = quantity
            messages.success(
                    request,
                    f'Updated size {size.upper()} {product.name} quantity to {bag[item_id]["items_by_size"][size]}'
                    )
        else:
            del bag[item_id]['items_by_size'][size]
            # if that's the only size they had, i.e. items_by_size dict is now empty
            if not bag[item_id]['items_by_size']:
                # remove that item
                bag.pop(item_id)
                messages.success(request, f'Removed size {size.upper()} {product.name} from your bag')
    # if no sizes - adjust quantity to new quantity, or if qty is 0 then delete (pop) it
    else:
        if quantity > 0:
            bag[item_id] = quantity
            messages.success(request, f'Updated {product.name} quantity to {bag[item_id]}')
        else:
            bag.pop(item_id)
            messages.success(request, f'Removed {product.name} from your bag')

    # put bag variable into session dictionary, (overwrite the variable in session
    # with updated version, if it existed before this)
    request.session['bag'] = bag
    # return user to the url using reverse, to go back to the view_bag url
    return redirect(reverse('view_bag'))


def remove_from_bag(request, item_id):
    """Remove the item from the shopping bag"""
    try:
        product = get_object_or_404(Product, pk=item_id)
        size = None
        # set size to size from the form, if it is there
        if 'product_size' in request.POST:
            size = request.POST['product_size']
        # shopping bag to be held in session storage
        # get the bag variable if it exists, or create empty dictionary for it if not there
        bag = request.session.get('bag', {})

        # if a product with sizes is being removed
        if size:
            # delete the specific size of that item
            del bag[item_id]['items_by_size'][size]
            # if that's the only size they had, i.e. items_by_size dict is now empty
            if not bag[item_id]['items_by_size']:
                # remove that item
                bag.pop(item_id)
            messages.success(request, f'Removed size {size.upper()} {product.name} from your bag')
        # if no sizes - then delete (pop) the item
        else:
            bag.pop(item_id)
            messages.success(request, f'Removed {product.name} from your bag')

        # put bag variable into session dictionary, (overwrite the variable in session
        # with updated version, if it existed before this)
        request.session['bag'] = bag
        # return successful response
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request,f'Error removing item: {e}')
        return HttpResponse(status=500)
