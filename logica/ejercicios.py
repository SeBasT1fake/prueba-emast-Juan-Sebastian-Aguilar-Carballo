from __future__ import annotations

import re
from collections import defaultdict

PESOS_DV = [3, 7, 13, 17, 19, 23, 29, 37, 41, 43, 47, 53, 59, 67, 71]
INICIO_JORNADA = 8 * 60
FIN_JORNADA = 18 * 60
ALMUERZO = (12 * 60, 13 * 60)


def calcular_dv(nit: str) -> int:
    if not isinstance(nit, str):
        raise ValueError("El NIT debe ser texto")
    limpio = nit.replace(".", "").replace(" ", "")
    if not limpio or not limpio.isdigit():
        raise ValueError("El NIT debe contener únicamente dígitos, puntos o espacios")
    if len(limpio) > len(PESOS_DV):
        raise ValueError("El NIT no puede tener más de 15 dígitos")

    total = sum(int(d) * PESOS_DV[i] for i, d in enumerate(reversed(limpio)))
    residuo = total % 11
    return residuo if residuo in (0, 1) else 11 - residuo


def validar_nit(nit_con_dv: str) -> bool:
    try:
        if not isinstance(nit_con_dv, str):
            return False
        partes = nit_con_dv.strip().split("-")
        if len(partes) != 2:
            return False
        base, dv = partes
        if len(dv) != 1 or not dv.isdigit():
            return False
        return calcular_dv(base) == int(dv)
    except (ValueError, TypeError):
        return False


def _a_minutos(hora: str) -> int:
    if not re.fullmatch(r"\d{2}:\d{2}", hora):
        raise ValueError(f"Hora inválida: {hora}")
    hh, mm = map(int, hora.split(":"))
    if hh > 23 or mm > 59:
        raise ValueError(f"Hora inválida: {hora}")
    return hh * 60 + mm


def _formatear(minutos: int) -> str:
    return f"{minutos // 60:02d}:{minutos % 60:02d}"


def _parsear_bloque(texto: str) -> tuple[int, int]:
    if not isinstance(texto, str):
        raise ValueError("Cada reunión debe ser texto")
    partes = texto.split("-")
    if len(partes) != 2:
        raise ValueError(f"Bloque inválido: {texto}")
    inicio, fin = map(_a_minutos, partes)
    if inicio >= fin:
        raise ValueError(f"El inicio debe ser anterior al fin: {texto}")
    return inicio, fin


def bloques_ocupados(reuniones: list[str]) -> list[str]:
    intervalos: list[tuple[int, int]] = [ALMUERZO]
    for reunion in reuniones:
        inicio, fin = _parsear_bloque(reunion)
        inicio = max(inicio, INICIO_JORNADA)
        fin = min(fin, FIN_JORNADA)
        if inicio < fin:
            intervalos.append((inicio, fin))

    intervalos.sort()
    fusionados: list[list[int]] = []
    for inicio, fin in intervalos:
        if not fusionados or inicio > fusionados[-1][1]:
            fusionados.append([inicio, fin])
        else:
            fusionados[-1][1] = max(fusionados[-1][1], fin)

    return [f"{_formatear(i)}-{_formatear(f)}" for i, f in fusionados]


def espacios_libres(reuniones: list[str], duracion_min: int) -> list[str]:
    if not isinstance(duracion_min, int) or duracion_min <= 0:
        raise ValueError("La duración mínima debe ser un entero positivo")

    ocupados = [_parsear_bloque(x) for x in bloques_ocupados(reuniones)]
    libres: list[str] = []
    cursor = INICIO_JORNADA
    for inicio, fin in ocupados:
        if inicio - cursor >= duracion_min:
            libres.append(f"{_formatear(cursor)}-{_formatear(inicio)}")
        cursor = max(cursor, fin)
    if FIN_JORNADA - cursor >= duracion_min:
        libres.append(f"{_formatear(cursor)}-{_formatear(FIN_JORNADA)}")
    return libres


def _normalizar_email(email: str | None) -> str | None:
    if email is None:
        return None
    valor = email.strip().lower()
    return valor or None


def _normalizar_telefono(telefono: str | None) -> str | None:
    if telefono is None:
        return None
    digitos = "".join(c for c in telefono if c.isdigit())
    if len(digitos) == 12 and digitos.startswith("57"):
        digitos = digitos[2:]
    return digitos or None


def agrupar_duplicados(registros: list[tuple[int, str, str | None, str | None]]) -> list[list[int]]:
    parent: dict[int, int] = {}
    rank: dict[int, int] = {}

    def find(x: int) -> int:
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra == rb:
            return
        if rank[ra] < rank[rb]:
            ra, rb = rb, ra
        parent[rb] = ra
        if rank[ra] == rank[rb]:
            rank[ra] += 1

    vistos_email: dict[str, int] = {}
    vistos_telefono: dict[str, int] = {}

    for id_, _nombre, email, telefono in registros:
        if id_ in parent:
            raise ValueError(f"ID duplicado en la entrada: {id_}")
        parent[id_] = id_
        rank[id_] = 0
        e = _normalizar_email(email)
        t = _normalizar_telefono(telefono)
        if e:
            if e in vistos_email:
                union(id_, vistos_email[e])
            else:
                vistos_email[e] = id_
        if t:
            if t in vistos_telefono:
                union(id_, vistos_telefono[t])
            else:
                vistos_telefono[t] = id_

    grupos: dict[int, list[int]] = defaultdict(list)
    for id_ in parent:
        grupos[find(id_)].append(id_)

    resultado = [sorted(ids) for ids in grupos.values() if len(ids) > 1]
    return sorted(resultado, key=lambda g: g[0])
