import requests
from .models import Autoexcluidos
from django.utils.timezone import now
import logging

logger = logging.getLogger(__name__)

def evaluar_pep(data):
    """
    Evalúa si hay coincidencias PEP y devuelve si es PEP, 
    las coincidencias, y el cargo si está disponible.

    :param data: dict completo del JSON
    :return: tuple (es_pep: bool, coincidencias: list[dict], cargo: str | None)
    """
    es_pep = False
    coincidencias_pep = []
    cargo = None
    nivel = None

    try:
        pep_data = data.get("listas", {}).get("pepChile", {})

        # Validamos si hay coincidencia PEP
        if isinstance(pep_data, dict) and pep_data.get("coincidence", False):
            es_pep = True
            coincidencias_pep.append(pep_data)  # Agregamos el dict a la lista

            # Intentamos obtener el cargo
            cargo = (
                pep_data.get("info", {}).get("position")
                or pep_data.get("data", {}).get("info", {}).get("position")
            )

            #Obtener el nivel PEP (Directo o Indirecto)
            nivel = (
                pep_data.get("info",{}).get("level")
                or pep_data.get("data", {}).get("info", {}).get("level")
            )
    except Exception as e:
        print("Error al evaluar PEP:", e)

    return es_pep, coincidencias_pep, cargo, nivel

def actualizar_autoexcluidos(api_url, bearer_token):
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Accept": "application/json"
    }

    resultados = []

    try:
        response = requests.get(api_url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, list):
            return None, "formato_incorrecto"

        for persona in data:
            run = persona.get("run")
            if not run:
                resultados.append((None, "sin_run"))
                continue

            assignee = persona.get("assignee", {})

            autoexcluido, creado = Autoexcluidos.objects.update_or_create(
                run=run,
                defaults={
                    "name": persona.get("name"),
                    "first_name": persona.get("first_name"),
                    "last_name": persona.get("last_name"),
                    "email": persona.get("email"),
                    "phone": persona.get("phone"),
                    "mobile_phone": persona.get("mobile_phone"),
                    "apo_name": assignee.get("name") if assignee else None,
                    "apo_first_name": assignee.get("first_name") if assignee else None,
                    "apo_last_name": assignee.get("last_name") if assignee else None,
                    "apo_email": assignee.get("email") if assignee else None,
                    "apo_phone": assignee.get("phone") if assignee else None,
                    "apo_mobile_phone": assignee.get("mobile_phone") if assignee else None,
                    "actualizado": now()
                }
            )

            estado = 'creado' if creado else 'actualizado'
            resultados.append((autoexcluido, estado))

        return resultados, "ok"

    except (requests.exceptions.RequestException, ValueError) as e:
        return None, "error_api"
    logger.info(f"Autoexcluidos sincronizados: {total} total — {creados} creados, {actualizados} actualizados, {sin_run} sin RUN")
