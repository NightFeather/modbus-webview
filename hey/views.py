from django.http.response import HttpResponse
from django.shortcuts import render

def root(request, *args, **kwargs):
    return render(request, 'index.html')
