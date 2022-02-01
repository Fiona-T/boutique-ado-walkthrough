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
    # shopping bag to be held in session storage
    # get the bag variable if it exists, or create empty dictionary for it if not there
    bag = request.session.get('bag', {})
    # if item already in bag, increase quantity
    if item_id in list(bag.keys()):
        bag[item_id] += quantity
    else:
        bag[item_id] = quantity
        # otherwise create key of the item id, set it equal to the quantity
    # put bag variable into session dictionary, (overwrite the variable in session
    # with updated version, if it existed before this)
    request.session['bag'] = bag
    # print the bag from session - to test
    print(request.session['bag'])
    print('Test')
    # return user to the url that came from the 'redirect_url' form input(hidden)
    return redirect(redirect_url)
