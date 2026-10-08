from datetime import datetime
from poo.crm import *

empresa = Empresa(1, "Logística Andina SAS", "contacto@andina.co", "900373913")
empresa.agregar_contacto(Contacto("Carlos Pérez", "Gerente", "carlos@andina.co", True))
mariana = PersonaNatural(2, "Mariana López", "mariana@example.com", "1144123456")

crm = Oportunidad(1, empresa, "Laura", "Implementación CRM", 30_000_000)
crm.agregar_actividad(Llamada(datetime.now(), "Laura", "Seguimiento", 20, True))
crm.agregar_actividad(Reunion(datetime.now(), "Laura", "Levantamiento", 60, ["Laura", "Carlos", "Ana"], True))
for _ in range(3):
    crm.avanzar()

cot = Cotizacion(DescuentoPorVolumen())
cot.agregar_linea(LineaCotizacion("Licencias (10 usuarios)", 10, 1_200_000))
cot.agregar_linea(LineaCotizacion("Implementación", 1, 18_000_000))
crm.agregar_cotizacion(cot)
cot.enviar(); cot.aceptar(); crm.ganar()

soporte = Oportunidad(2, mariana, "Laura", "Soporte anual", 8_000_000)
soporte.avanzar()
pipeline = PipelineService([crm, soporte])

print(empresa.identificacion())
print(f"Subtotal: {cot.subtotal}; descuento: {cot.descuento}; base: {cot.base}; IVA: {cot.iva}; total: {cot.total}")
print(f"Valor final oportunidad: {crm.valor}")
print("Historial:", [(h.anterior.etiqueta, h.nueva.etiqueta, h.fecha_hora.isoformat()) for h in crm.historial])
print("Minutos invertidos:", sum(a.minutos_invertidos() for a in crm.actividades))
print("Pronóstico ponderado Laura:", pipeline.pronostico_ponderado("Laura"))

try:
    crm.perder("Intento inválido")
except ErrorDominio as exc:
    print("Error esperado:", exc)
