from django.shortcuts import render, redirect, get_object_or_404
from .forms import RutForm, ProhibidoForm
from django.conf import settings
import requests
from .utils import evaluar_pep, actualizar_autoexcluidos
from .models import Autoexcluidos, Prohibidos
import logging

logger = logging.getLogger(__name__)

# Create your views here.
def home(request):
    mensaje = None
    resultado_pep = None
    es_pep = False
    nivel = None
    coincidencias = []
    cargo_pep = []
    resultado_scj = None
    resultado_proh = None

    if request.method == "POST":
        form = RutForm(request.POST)
        if form.is_valid():
            rut = form.cleaned_data['rut']
            mensaje = f"RUT recibido y válido: {rut}"

            # Consultamos a API Regcheq
            rut_sin_guion = modular_rut_api(rut)
            resultado_pep = consultar_rut_api(rut_sin_guion)

            # Consultamos a bases locales
            resultado_scj = Autoexcluidos.objects.filter(run=rut).exists()
            resultado_proh = Prohibidos.objects.filter(rut=rut).exists()

            # Evaluar PEP solo si no hubo error
            if "error" not in resultado_pep:
                es_pep, coincidencias, cargo_pep, nivel = evaluar_pep(resultado_pep)
            else:
                logger.warning(f"Error en resultado_pep: {resultado_pep['error']}")
                mensaje = f"Error al consultar PEP: {resultado_pep['error']}"

            print("¿Es PEP?:", es_pep)
            print("Coincidencias:", coincidencias)
            print("Cargo PEP:", cargo_pep)
            print("Nivel PEP:", nivel)
            print("Autoexcluido:", resultado_scj)
            print("Prohibido:", resultado_proh)
        else:
            mensaje = "RUT inválido."
    else:
        form = RutForm()

    return render(request, 'scanner/home.html', {
        'form': form,
        'mensaje': mensaje,
        'resultado': resultado_pep,
        'es_pep': es_pep,
        'coincidencias': coincidencias,
        'cargo_pep': cargo_pep,
        'nivel_pep': nivel,
        'autoexcluido': resultado_scj,
        'prohibido': resultado_proh,
    })

def modular_rut_api(dni):
    dni_api_reg = dni[:-2] + dni[-1]
    # print("EL RUT PARA LA REGCHEQ ES: ",dni_api_reg)
    return dni_api_reg
    
def consultar_rut_api(dni):
    
    url = f"https://external-api.regcheq.com/record/{settings.API_KEY_REGCHEQ}"
    headers = {
        "Content-Type": "application/json",
        #"Authorization": f"Bearer {settings.API_KEY_REGCHEQ}"
    }
    data = {
        "dni": dni,
        "personType": "natural"
    }
    # print("🔑 API Key:", settings.API_KEY_REGCHEQ)
    # print("URL:", url)
    # print("Headers:", headers)
    # print("Data: ", data)
    # print(f"Intentando conectar a API con clave: {settings.API_KEY_REGCHEQ}")  # Log parcial de API key
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        
        # Log detallado
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        if response.status_code != 200:
            print(f"Response Content: {response.text}")
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.HTTPError as http_err:
        print(f"Error HTTP: {http_err}")
        print(f"Respuesta del servidor: {response.text}")
        return {"error": f"Error HTTP: {http_err}"}
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Error de conexión: {conn_err}")
        return {"error": "No se pudo establecer conexión con la API"}
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout: {timeout_err}")
        return {"error": "Tiempo de espera agotado"}
    except requests.exceptions.RequestException as req_err:
        print(f"Error en la solicitud: {req_err}")
        return {"error": "Error al procesar la solicitud"}
    except Exception as e:
        print(f"Error inesperado: {e}")
        return {"error": "Error desconocido"}
    
autoexcluido, estado = actualizar_autoexcluidos(
    api_url='https://autoexclusion.scj.gob.cl/api/v1/exclusions',
    #bearer_token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOjgyLCJpYXQiOjE1NjU1MjQzMzR9.yMFcpG4qjQsc65YHk21C5qt5h5vwAQ9SuyPuLlJ6FWE'
    bearer_token=settings.TOKEN_API_SCJ
)

if estado == 'creado':
    print("Registro creado")
elif estado == 'actualizado':
    print("Registro Actualizado")
elif estado == 'local':
    print("Datos desde la BD Local")
else:
    print("No se pudo obtener el registro")

def listar_prohibidos(request):
    prohibidos = Prohibidos.objects.all()
    return render(request, 'scanner/prohibidos/listar.html',{'prohibidos': prohibidos})

def agregar_prohibido(request):
    if request.method == 'POST':
        form = ProhibidoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_prohibidos')
    else:
        form = ProhibidoForm()
    return render(request, 'scanner/prohibidos/formulario.html', {'form': form})

def editar_prohibido(request, pk):
    prohibido = get_object_or_404(Prohibidos, pk=pk)
    form = ProhibidoForm(request.POST or None, instance=prohibido)
    if form.is_valid():
        form.save()
        return redirect('listar_prohibidos')
    return render(request, 'scanner/prohibidos/formulario.html', {'form': form})

def eliminar_prohibido(request, pk):
    prohibido = get_object_or_404(Prohibidos, pk=pk)
    if request.method == 'POST':
        prohibido.delete()
        return redirect('listar_prohibidos')
    return render(request, 'scanner/prohibidos/confirmar_eliminar.html', {'prohibido': prohibido})