def evaluar_pep(data):
    es_pep = False
    coincidencias_pep = []

    if data.get('total') and data.get('data'):
        for coincidencia in data['data']:
            if coincidencia.get('match',{}).get('matchType') == 'Exact':
                es_pep = True
                coincidencias_pep.append(coincidencia)

    return es_pep, coincidencias_pep