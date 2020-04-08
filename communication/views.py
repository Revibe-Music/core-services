from django.shortcuts import render

# Create your views here.

# all temp stuff...

def index(request):
    return render(request, "communication/index.html")

def room(request, room_name="hello"):
    return render(request, 'communication/room.html', {
        "room_name": room_name
    })
