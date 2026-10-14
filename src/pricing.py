import sys
sys.path.insert(0, ".")

TARIFA_TRADICIONAL_POR_KG_KM = 0.08
TARIFA_ENRUTA_POR_KG_KM = 0.025
TARIFA_FIJA_POR_ENVIO = 3.00
COMPENSACION_TRANSPORTISTA_POR_KM_EXTRA = 0.50


def coste_tradicional(kg: float, km: float) -> dict:
    total = kg * km * TARIFA_TRADICIONAL_POR_KG_KM + TARIFA_FIJA_POR_ENVIO
    return {"total_eur": round(total, 2), "tarifa": f"{TARIFA_TRADICIONAL_POR_KG_KM} €/kg·km"}


def coste_enruta(kg: float, km: float) -> dict:
    total = kg * km * TARIFA_ENRUTA_POR_KG_KM + TARIFA_FIJA_POR_ENVIO
    return {"total_eur": round(total, 2), "tarifa": f"{TARIFA_ENRUTA_POR_KG_KM} €/kg·km"}


def ingreso_transportista(extra_km: float, kg: float) -> dict:
    total = extra_km * COMPENSACION_TRANSPORTISTA_POR_KM_EXTRA + kg * 0.10
    return {"total_eur": round(total, 2), "concepto": "compensación por desvío + carga"}


def calcular_ahorro(kg: float, km_ruta: float, extra_km: float) -> dict:
    trad = coste_tradicional(kg, km_ruta + extra_km)
    enruta = coste_enruta(kg, km_ruta + extra_km)
    ingreso = ingreso_transportista(extra_km, kg)
    return {
        "coste_tradicional_eur": trad["total_eur"],
        "coste_enruta_eur": enruta["total_eur"],
        "ahorro_eur": round(trad["total_eur"] - enruta["total_eur"], 2),
        "ahorro_pct": round((1 - enruta["total_eur"] / trad["total_eur"]) * 100, 1) if trad["total_eur"] > 0 else 0,
        "ingreso_transportista_eur": ingreso["total_eur"],
    }


def precio_sugerido_oferta(capacidad_kg: float, km_estimados: float) -> float:
    return round(capacidad_kg * km_estimados * TARIFA_ENRUTA_POR_KG_KM + TARIFA_FIJA_POR_ENVIO, 2)


def coste_estimado_demanda(kg: float, km_estimados: float) -> dict:
    enruta = coste_enruta(kg, km_estimados)
    trad = coste_tradicional(kg, km_estimados)
    return {
        "coste_enruta_eur": enruta["total_eur"],
        "coste_tradicional_eur": trad["total_eur"],
        "ahorro_eur": round(trad["total_eur"] - enruta["total_eur"], 2),
        "ahorro_pct": round((1 - enruta["total_eur"] / trad["total_eur"]) * 100, 1) if trad["total_eur"] > 0 else 0,
    }
