from django.shortcuts import render


def profile(request):
    """profile page - display user profile"""
    template = 'profiles/profile.html'
    context = {}

    return render(request, template, context)