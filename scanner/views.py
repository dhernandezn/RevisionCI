from django.shortcuts import render
from django.http import HttpResponse
from .forms import RutForm

def home(request):
    mensaje = None
    if request.method == "POST":
        form = RutForm(request.POST)
        if form.is_valid():
            rut = form.cleaned_data['rut']
            mensaje = f"RUT recibido y válido: {rut}"
        else:
            mensaje = "RUT inválido."
    else:
        form = RutForm()
    return render(request, 'scanner/home.html',{'form': form, 'mensaje': mensaje})

# Create your views here.
