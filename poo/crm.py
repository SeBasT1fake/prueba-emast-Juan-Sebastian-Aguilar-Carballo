from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Iterable

from logica.ejercicios import calcular_dv, validar_nit

CENTAVOS = Decimal("0.01")
IVA = Decimal("0.19")


def dinero(valor: Decimal | int | str) -> Decimal:
    return Decimal(str(valor)).quantize(CENTAVOS, rounding=ROUND_HALF_UP)


def _email_valido(email: str) -> bool:
    return bool(re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email or ""))


class ErrorDominio(Exception):
    pass


class ValidacionError(ErrorDominio):
    pass


class TransicionInvalidaError(ErrorDominio):
    pass


class OportunidadCerradaError(ErrorDominio):
    pass


class Cliente(ABC):
    def __init__(self, id: int, nombre: str, email: str, fecha_creacion: date | None = None):
        if not nombre or not nombre.strip():
            raise ValidacionError("El nombre del cliente es obligatorio")
        if not _email_valido(email):
            raise ValidacionError("El email del cliente no tiene un formato válido")
        self.id = id
        self.nombre = nombre.strip()
        self.email = email.strip().lower()
        self.fecha_creacion = fecha_creacion or date.today()

    @abstractmethod
    def identificacion(self) -> str:
        raise NotImplementedError


class PersonaNatural(Cliente):
    def __init__(self, id: int, nombre: str, email: str, documento: str, fecha_creacion: date | None = None):
        super().__init__(id, nombre, email, fecha_creacion)
        if not documento or not documento.isdigit():
            raise ValidacionError("El documento debe contener solo dígitos")
        self.documento = documento

    def identificacion(self) -> str:
        return f"CC {self.documento}"


@dataclass(frozen=True)
class Contacto:
    nombre: str
    cargo: str
    email: str
    principal: bool = False

    def __post_init__(self):
        if not self.nombre.strip() or not self.cargo.strip():
            raise ValidacionError("Nombre y cargo del contacto son obligatorios")
        if not _email_valido(self.email):
            raise ValidacionError("Email de contacto inválido")


class Empresa(Cliente):
    def __init__(self, id: int, nombre: str, email: str, nit: str, fecha_creacion: date | None = None):
        super().__init__(id, nombre, email, fecha_creacion)
        self._nit_base = self._procesar_nit(nit)
        self._contactos: list[Contacto] = []

    @staticmethod
    def _procesar_nit(nit: str) -> str:
        if not isinstance(nit, str) or not nit.strip():
            raise ValidacionError("El NIT es obligatorio")
        nit = nit.strip()
        if "-" in nit:
            if not validar_nit(nit):
                raise ValidacionError("El dígito de verificación del NIT no coincide")
            base = nit.rsplit("-", 1)[0]
        else:
            base = nit
        limpio = base.replace(".", "").replace(" ", "")
        try:
            calcular_dv(limpio)
        except ValueError as exc:
            raise ValidacionError(str(exc)) from exc
        return limpio

    @property
    def contactos(self) -> tuple[Contacto, ...]:
        return tuple(self._contactos)

    def agregar_contacto(self, contacto: Contacto) -> None:
        if contacto.principal and any(c.principal for c in self._contactos):
            raise ValidacionError("La empresa ya tiene un contacto principal")
        self._contactos.append(contacto)

    def identificacion(self) -> str:
        return f"NIT {self._nit_base}-{calcular_dv(self._nit_base)}"


class Etapa(Enum):
    PROSPECTO = ("Prospecto", Decimal("0.10"))
    CALIFICADA = ("Calificada", Decimal("0.25"))
    PROPUESTA = ("Propuesta", Decimal("0.50"))
    NEGOCIACION = ("Negociación", Decimal("0.75"))
    GANADA = ("Ganada", Decimal("1.00"))
    PERDIDA = ("Perdida", Decimal("0.00"))

    def __init__(self, etiqueta: str, probabilidad: Decimal):
        self.etiqueta = etiqueta
        self.probabilidad = probabilidad

    @property
    def abierta(self) -> bool:
        return self not in (Etapa.GANADA, Etapa.PERDIDA)


@dataclass(frozen=True)
class CambioEtapa:
    anterior: Etapa
    nueva: Etapa
    fecha_hora: datetime


class Actividad(ABC):
    def __init__(self, fecha: datetime, asesor: str, descripcion: str):
        if not asesor.strip() or not descripcion.strip():
            raise ValidacionError("Asesor y descripción son obligatorios")
        self.fecha = fecha
        self.asesor = asesor.strip()
        self.descripcion = descripcion.strip()

    @abstractmethod
    def resumen(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def minutos_invertidos(self) -> int:
        raise NotImplementedError


class Llamada(Actividad):
    def __init__(self, fecha: datetime, asesor: str, descripcion: str, duracion: int, contesto: bool):
        super().__init__(fecha, asesor, descripcion)
        if duracion <= 0:
            raise ValidacionError("La duración de la llamada debe ser positiva")
        self.duracion = duracion
        self.contesto = contesto

    def resumen(self) -> str:
        estado = "contestó" if self.contesto else "no contestó"
        return f"Llamada ({self.duracion} min, {estado}): {self.descripcion}"

    def minutos_invertidos(self) -> int:
        return self.duracion


class Reunion(Actividad):
    def __init__(self, fecha: datetime, asesor: str, descripcion: str, duracion: int,
                 asistentes: Iterable[str], presencial: bool):
        super().__init__(fecha, asesor, descripcion)
        asistentes = tuple(a.strip() for a in asistentes if a and a.strip())
        if duracion <= 0:
            raise ValidacionError("La duración de la reunión debe ser positiva")
        if not asistentes:
            raise ValidacionError("La reunión debe tener al menos un asistente")
        self.duracion = duracion
        self.asistentes = asistentes
        self.presencial = presencial

    def resumen(self) -> str:
        modalidad = "presencial" if self.presencial else "virtual"
        return f"Reunión {modalidad} ({self.duracion} min, {len(self.asistentes)} asistentes): {self.descripcion}"

    def minutos_invertidos(self) -> int:
        return self.duracion + (30 if self.presencial else 0)


class Correo(Actividad):
    def __init__(self, fecha: datetime, asesor: str, descripcion: str, asunto: str, enviado: bool):
        super().__init__(fecha, asesor, descripcion)
        if not asunto.strip():
            raise ValidacionError("El asunto del correo es obligatorio")
        self.asunto = asunto.strip()
        self.enviado = enviado

    def resumen(self) -> str:
        sentido = "enviado" if self.enviado else "recibido"
        return f"Correo {sentido} '{self.asunto}': {self.descripcion}"

    def minutos_invertidos(self) -> int:
        return 5


class PoliticaDescuento(ABC):
    @abstractmethod
    def calcular(self, subtotal: Decimal) -> Decimal:
        raise NotImplementedError


class SinDescuento(PoliticaDescuento):
    def calcular(self, subtotal: Decimal) -> Decimal:
        return Decimal("0")


class DescuentoPorcentual(PoliticaDescuento):
    def __init__(self, porcentaje: Decimal | int | str):
        self.porcentaje = Decimal(str(porcentaje))
        if self.porcentaje <= 0 or self.porcentaje > 15:
            raise ValidacionError("El descuento porcentual debe ser > 0 y <= 15")

    def calcular(self, subtotal: Decimal) -> Decimal:
        return subtotal * self.porcentaje / Decimal("100")


class DescuentoPorVolumen(PoliticaDescuento):
    def calcular(self, subtotal: Decimal) -> Decimal:
        if subtotal >= Decimal("50000000"):
            return subtotal * Decimal("0.08")
        if subtotal >= Decimal("20000000"):
            return subtotal * Decimal("0.05")
        return Decimal("0")


@dataclass(frozen=True)
class LineaCotizacion:
    descripcion: str
    cantidad: Decimal
    precio_unitario: Decimal

    def __post_init__(self):
        if not self.descripcion.strip():
            raise ValidacionError("La descripción de la línea es obligatoria")
        if Decimal(str(self.cantidad)) <= 0:
            raise ValidacionError("La cantidad debe ser mayor que cero")
        if Decimal(str(self.precio_unitario)) < 0:
            raise ValidacionError("El precio unitario no puede ser negativo")
        object.__setattr__(self, "cantidad", Decimal(str(self.cantidad)))
        object.__setattr__(self, "precio_unitario", Decimal(str(self.precio_unitario)))

    @property
    def total(self) -> Decimal:
        return self.cantidad * self.precio_unitario


class EstadoCotizacion(Enum):
    BORRADOR = "Borrador"
    ENVIADA = "Enviada"
    ACEPTADA = "Aceptada"
    RECHAZADA = "Rechazada"


class Cotizacion:
    def __init__(self, politica: PoliticaDescuento | None = None):
        self._lineas: list[LineaCotizacion] = []
        self._politica = politica or SinDescuento()
        self.estado = EstadoCotizacion.BORRADOR

    @property
    def lineas(self) -> tuple[LineaCotizacion, ...]:
        return tuple(self._lineas)

    @property
    def politica(self) -> PoliticaDescuento:
        return self._politica

    def _exigir_borrador(self) -> None:
        if self.estado is not EstadoCotizacion.BORRADOR:
            raise TransicionInvalidaError("La cotización solo puede modificarse en Borrador")

    def agregar_linea(self, linea: LineaCotizacion) -> None:
        self._exigir_borrador()
        self._lineas.append(linea)

    def cambiar_politica(self, politica: PoliticaDescuento) -> None:
        self._exigir_borrador()
        self._politica = politica

    @property
    def subtotal(self) -> Decimal:
        return dinero(sum((l.total for l in self._lineas), Decimal("0")))

    @property
    def descuento(self) -> Decimal:
        return dinero(self._politica.calcular(self.subtotal))

    @property
    def base(self) -> Decimal:
        return dinero(self.subtotal - self.descuento)

    @property
    def iva(self) -> Decimal:
        return dinero(self.base * IVA)

    @property
    def total(self) -> Decimal:
        return dinero(self.base + self.iva)

    def enviar(self) -> None:
        if self.estado is not EstadoCotizacion.BORRADOR:
            raise TransicionInvalidaError("Solo una cotización en Borrador puede enviarse")
        if not self._lineas:
            raise TransicionInvalidaError("No se puede enviar una cotización sin líneas")
        self.estado = EstadoCotizacion.ENVIADA

    def aceptar(self) -> None:
        if self.estado is not EstadoCotizacion.ENVIADA:
            raise TransicionInvalidaError("Solo una cotización Enviada puede aceptarse")
        self.estado = EstadoCotizacion.ACEPTADA

    def rechazar(self) -> None:
        if self.estado is not EstadoCotizacion.ENVIADA:
            raise TransicionInvalidaError("Solo una cotización Enviada puede rechazarse")
        self.estado = EstadoCotizacion.RECHAZADA


class Oportunidad:
    _SIGUIENTE = {
        Etapa.PROSPECTO: Etapa.CALIFICADA,
        Etapa.CALIFICADA: Etapa.PROPUESTA,
        Etapa.PROPUESTA: Etapa.NEGOCIACION,
    }

    def __init__(self, id: int, cliente: Cliente, asesor: str, titulo: str,
                 valor_estimado: Decimal | int | str, fecha_creacion: date | None = None):
        valor = Decimal(str(valor_estimado))
        if valor <= 0:
            raise ValidacionError("El valor estimado debe ser mayor que cero")
        if not asesor.strip() or not titulo.strip():
            raise ValidacionError("Asesor y título son obligatorios")
        self.id = id
        self.cliente = cliente
        self.asesor = asesor.strip()
        self.titulo = titulo.strip()
        self.valor = dinero(valor)
        self.fecha_creacion = fecha_creacion or date.today()
        self.etapa = Etapa.PROSPECTO
        self.motivo_perdida: str | None = None
        self._historial: list[CambioEtapa] = []
        self._actividades: list[Actividad] = []
        self._cotizaciones: list[Cotizacion] = []

    @property
    def historial(self) -> tuple[CambioEtapa, ...]:
        return tuple(self._historial)

    @property
    def actividades(self) -> tuple[Actividad, ...]:
        return tuple(self._actividades)

    @property
    def cotizaciones(self) -> tuple[Cotizacion, ...]:
        return tuple(self._cotizaciones)

    def _exigir_abierta(self) -> None:
        if not self.etapa.abierta:
            raise OportunidadCerradaError(f"La oportunidad está cerrada en etapa {self.etapa.etiqueta}")

    def _cambiar_etapa(self, nueva: Etapa) -> None:
        anterior = self.etapa
        self.etapa = nueva
        self._historial.append(CambioEtapa(anterior, nueva, datetime.now()))

    def avanzar(self) -> None:
        self._exigir_abierta()
        if self.etapa not in self._SIGUIENTE:
            raise TransicionInvalidaError("Desde Negociación solo se puede ganar o perder")
        self._cambiar_etapa(self._SIGUIENTE[self.etapa])

    def agregar_actividad(self, actividad: Actividad) -> None:
        self._exigir_abierta()
        self._actividades.append(actividad)

    def agregar_cotizacion(self, cotizacion: Cotizacion) -> None:
        self._exigir_abierta()
        self._cotizaciones.append(cotizacion)

    def ganar(self) -> None:
        self._exigir_abierta()
        if self.etapa is not Etapa.NEGOCIACION:
            raise TransicionInvalidaError("Solo se puede ganar desde Negociación")
        aceptadas = [c for c in self._cotizaciones if c.estado is EstadoCotizacion.ACEPTADA]
        if not aceptadas:
            raise TransicionInvalidaError("Se requiere una cotización Aceptada para ganar")
        cotizacion = aceptadas[-1]
        self.valor = cotizacion.base
        self._cambiar_etapa(Etapa.GANADA)

    def perder(self, motivo: str) -> None:
        self._exigir_abierta()
        if not motivo or not motivo.strip():
            raise ValidacionError("El motivo de pérdida es obligatorio")
        self.motivo_perdida = motivo.strip()
        self._cambiar_etapa(Etapa.PERDIDA)


class PipelineService:
    def __init__(self, oportunidades: Iterable[Oportunidad] = ()): 
        self._oportunidades = list(oportunidades)

    def agregar(self, oportunidad: Oportunidad) -> None:
        self._oportunidades.append(oportunidad)

    def pronostico_ponderado(self, asesor: str) -> Decimal:
        total = sum(
            (o.valor * o.etapa.probabilidad for o in self._oportunidades
             if o.asesor == asesor and o.etapa.abierta),
            Decimal("0"),
        )
        return dinero(total)

    def oportunidades_estancadas(self, dias: int, hoy: date) -> list[Oportunidad]:
        if dias < 0:
            raise ValidacionError("Los días no pueden ser negativos")
        limite = hoy - timedelta(days=dias)
        resultado = []
        for o in self._oportunidades:
            if not o.etapa.abierta:
                continue
            ultima = max((a.fecha.date() for a in o.actividades), default=o.fecha_creacion)
            if ultima < limite:
                resultado.append(o)
        return resultado

    def resumen_por_etapa(self) -> dict[Etapa, dict[str, Decimal | int]]:
        resumen = {e: {"cantidad": 0, "valor_total": Decimal("0.00")} for e in Etapa}
        for o in self._oportunidades:
            resumen[o.etapa]["cantidad"] += 1
            resumen[o.etapa]["valor_total"] += o.valor
        for datos in resumen.values():
            datos["valor_total"] = dinero(datos["valor_total"])
        return resumen
