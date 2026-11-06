"""
Convierte un KML de polígonos de bloque al formato de MONIPLAG.

El nombre de cada polígono se interpreta como lote (2), bloque (2) y año (2):
    021626  ->  lote 02, bloque 16, año 2026

Produce:
  · la hoja 1.Bloques con lote, área calculada del polígono, población estimada
    y el centroide como latitud y longitud
  · la hoja 9.Poligonos con un vértice por fila

Uso:  python3 kml_a_formato.py archivo.kml [densidad_plantas_ha]
"""
import sys, re, unicodedata
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd

NS = {'k': 'http://www.opengis.net/kml/2.2'}
DENSIDAD = 62500          # plantas por hectárea, mediana observada en La Fe


def _num(x):
    try:
        return float(x)
    except Exception:
        return None


def leer_kml(ruta):
    """devuelve una lista de polígonos con su nombre y sus vértices"""
    raiz = ET.parse(ruta).getroot()
    salida = []
    for pm in raiz.findall('.//k:Placemark', NS):
        nodo = pm.find('k:name', NS)
        nombre = (nodo.text or '').strip() if nodo is not None else ''
        coord = pm.find('.//k:coordinates', NS)
        if coord is None:
            continue
        pts = []
        for tok in (coord.text or '').split():
            partes = tok.split(',')
            if len(partes) < 2:
                continue
            lo, la = _num(partes[0]), _num(partes[1])
            if lo is None or la is None:
                continue
            pts.append((la, lo))
        # el KML repite el primer vértice al cerrar el anillo
        if len(pts) > 3 and abs(pts[0][0] - pts[-1][0]) < 1e-9 and abs(pts[0][1] - pts[-1][1]) < 1e-9:
            pts = pts[:-1]
        if len(pts) >= 3 and nombre:
            salida.append({'nombre': nombre, 'pts': pts})
    return salida


def metricas_poligono(pts):
    """área en hectáreas, perímetro en metros y centroide"""
    la0 = float(np.mean([p[0] for p in pts]))
    m_lat = 110574.0
    m_lon = 111320.0 * np.cos(np.radians(la0))
    x = np.array([(p[1] - pts[0][1]) * m_lon for p in pts])
    y = np.array([(p[0] - pts[0][0]) * m_lat for p in pts])
    n = len(pts)
    cruz = x * np.roll(y, -1) - np.roll(x, -1) * y
    area_m2 = abs(cruz.sum()) / 2.0
    peri = float(np.sum(np.sqrt((np.roll(x, -1) - x) ** 2 + (np.roll(y, -1) - y) ** 2)))
    if abs(cruz.sum()) > 1e-9:
        cx = float((((x + np.roll(x, -1)) * cruz).sum()) / (3 * cruz.sum()))
        cy = float((((y + np.roll(y, -1)) * cruz).sum()) / (3 * cruz.sum()))
    else:
        cx, cy = float(x.mean()), float(y.mean())
    return {'area_ha': area_m2 / 10000.0, 'perimetro_m': peri,
            'lat': pts[0][0] + cy / m_lat, 'lon': pts[0][1] + cx / m_lon,
            'vertices': n}


def descomponer(nombre):
    """lote, bloque y año a partir del código de seis dígitos"""
    d = re.sub(r'\D', '', nombre)
    if len(d) == 6:
        lote, blq, anio = d[0:2], d[2:4], d[4:6]
        return int(lote), int(blq), 2000 + int(anio)
    return None, None, None


def convertir(ruta, densidad=DENSIDAD):
    """Si el KML repite un código, cada parcela recibe un sufijo (B, C...)
    para que sean bloques distintos y no se dibujen unidas."""
    polis = leer_kml(ruta)
    vistos, filas, vert = {}, [], []
    for p in polis:
        base = p['nombre']
        vistos[base] = vistos.get(base, 0) + 1
        code = base if vistos[base] == 1 else base + chr(63 + vistos[base])   # B, C, D...
        m = metricas_poligono(p['pts'])
        lote, blq, anio = descomponer(base)
        filas.append({
            'bloque': code,
            'lote': ('L%02d' % lote) if lote else '',
            'numero_bloque': blq, 'anio': anio,
            'area_ha': round(m['area_ha'], 4),
            'perimetro_m': round(m['perimetro_m'], 1),
            'poblacion': int(round(m['area_ha'] * densidad)),
            'latitud': round(m['lat'], 6), 'longitud': round(m['lon'], 6),
            'vertices': m['vertices']})
        for k, (la, lo) in enumerate(p['pts'], 1):
            vert.append({'bloque': code, 'orden': k,
                         'latitud': round(la, 6), 'longitud': round(lo, 6)})
    bl = pd.DataFrame(filas).sort_values('bloque').reset_index(drop=True)
    return bl, pd.DataFrame(vert)


if __name__ == '__main__':
    ruta = sys.argv[1] if len(sys.argv) > 1 else '/mnt/user-data/uploads/lafe2026__1_.kml'
    dens = float(sys.argv[2]) if len(sys.argv) > 2 else DENSIDAD
    bl, vt = convertir(ruta, dens)
    print(f'polígonos leídos: {len(bl)} · vértices: {len(vt)}')
    print(f'área total: {bl.area_ha.sum():.2f} ha · población estimada: {bl.poblacion.sum():,}')
    print(f'lotes: {sorted(bl.lote.unique())}')
    dup = [c for c in bl.bloque if not c[-1].isdigit()]
    if dup:
        print('códigos repetidos en el KML, separados como bloques distintos: ' + ', '.join(dup))
    print(bl.head(8).to_string(index=False))
