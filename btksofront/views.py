from django.shortcuts import render

def main(request,id=0):
    return render(request, 'index.html')
