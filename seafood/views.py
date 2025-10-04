from django.shortcuts import render

def home(request):
    return render(request, 'seafood/home.html')


def about_us(request):
    return render(request, 'seafood/about-us.html')


def contact(request):
    return render(request, 'seafood/contact.html')


def services(request):
    return render(request, 'seafood/services.html')


def privacy(request):
    return render(request, 'seafood/privacy.html')


def gallery(request):
    return render(request, 'seafood/gallery.html')


def faqs(request):
    return render(request, 'seafood/faqs.html')


def logistics(request):
    return render(request, 'seafood/logistics.html')


def blog(request):
    return render(request, 'seafood/blog.html')
