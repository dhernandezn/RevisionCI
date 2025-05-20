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
    except Exception as e:
        print("Error al evaluar PEP:", e)

    return es_pep, coincidencias_pep, cargo
