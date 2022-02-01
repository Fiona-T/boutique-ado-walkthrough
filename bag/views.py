from django.shortcuts import render, redirect


def view_bag(request):
    """view to return bag contents page """
    return render(request, 'bag/bag.html')


def add_to_bag(request, item_id):
    """Add a quantity of the specified product to the shopping bag"""
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
            else:
                # item already exists but a different size, so adding a new size for that item
                bag[item_id]['items_by_size'][size] = quantity
        else:
            # if it doesn't have sizes, then just add to bag
            # add it as a dictionary with a key of items by size
            # so can have multiple of same item_id but with different sizes
            bag[item_id] = {'items_by_size': {size: quantity}}
    else:
        # the original code - check if item in bag
        # if item already in bag, increase quantity
        if item_id in list(bag.keys()):
            bag[item_id] += quantity
        else:
            # otherwise create key of the item id, set it equal to the quantity
            bag[item_id] = quantity   
    # put bag variable into session dictionary, (overwrite the variable in session
    # with updated version, if it existed before this)
    request.session['bag'] = bag
    # return user to the url that came from the 'redirect_url' form input(hidden)
    return redirect(redirect_url)
