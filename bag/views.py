from django.shortcuts import render

def view_bag(request):
    """view to return bag contents page """
    return render(request, 'bag/bag.html')
