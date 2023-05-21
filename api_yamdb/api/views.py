from django.shortcuts import render


def redoc(request):
    return render(request, 'api/redoc.html')
