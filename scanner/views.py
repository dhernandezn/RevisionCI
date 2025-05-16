from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from .forms import RutForm
from django.conf import settings
import requests
from .utils import evaluar_pep

def home(request):
    mensaje = None
    resultado = None
    es_pep = False
    coincidencias = []

    if request.method == "POST":
        form = RutForm(request.POST)
        if form.is_valid():
            rut = form.cleaned_data['rut']
            mensaje = f"RUT recibido y válido: {rut}"

            #Consultamos a API Regcheq
            rut_sin_guion = modular_rut_api(rut)
            print("RUT A REVISAR: ",rut_sin_guion)
            resultado = consultar_rut_api(rut_sin_guion)
            
            es_pep, coincidencias = evaluar_pep(resultado)
        else:
            mensaje = "RUT inválido."
    else:
        form = RutForm()
    return render(request, 'scanner/home.html',{
       'form': form,
    'mensaje': mensaje,
    'resultado': resultado,
    'es_pep': es_pep,
    'coincidencias': coincidencias,
    # 'es_autoexcluido': es_autoexcluido,
    # 'es_prohibido': es_prohibido,
    # 'es_sospechoso': es_sospechoso,
        })
def modular_rut_api(dni):
    dni_api_reg = dni[:-2] + dni[-1]
    print("EL RUT PARA LA API ES: ",dni_api_reg)
    
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
    print("🔑 API Key:", settings.API_KEY_REGCHEQ)
    print("URL:", url)
    print("Headers:", headers)
    print("Data: ", data)
    print(f"Intentando conectar a API con clave: {settings.API_KEY_REGCHEQ}")  # Log parcial de API key
    
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
# Create your views here.
