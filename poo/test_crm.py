import unittest
from datetime import datetime
from decimal import Decimal

from poo.crm import (
    Empresa, PersonaNatural, Contacto, Oportunidad, Llamada, Reunion,
    Cotizacion, LineaCotizacion, DescuentoPorVolumen, DescuentoPorcentual,
    PipelineService, Etapa, ErrorDominio, ValidacionError, TransicionInvalidaError,
    OportunidadCerradaError,
)


class CRMTests(unittest.TestCase):
    def escenario(self):
        empresa = Empresa(1, "Logística Andina SAS", "contacto@andina.co", "900373913")
        empresa.agregar_contacto(Contacto("Carlos Pérez", "Gerente", "carlos@andina.co", True))
        mariana = PersonaNatural(2, "Mariana López", "mariana@example.com", "1144123456")

        oportunidad = Oportunidad(1, empresa, "Laura", "Implementación CRM", 30_000_000)
        oportunidad.agregar_actividad(Llamada(datetime(2026, 10, 1, 9), "Laura", "Seguimiento", 20, True))
        oportunidad.agregar_actividad(Reunion(datetime(2026, 10, 2, 10), "Laura", "Levantamiento", 60,
                                             ["Laura", "Carlos", "Ana"], True))
        oportunidad.avanzar(); oportunidad.avanzar(); oportunidad.avanzar()

        cot = Cotizacion(DescuentoPorVolumen())
        cot.agregar_linea(LineaCotizacion("Licencias (10 usuarios)", 10, 1_200_000))
        cot.agregar_linea(LineaCotizacion("Implementación", 1, 18_000_000))
        oportunidad.agregar_cotizacion(cot)
        cot.enviar(); cot.aceptar(); oportunidad.ganar()

        soporte = Oportunidad(2, mariana, "Laura", "Soporte anual", 8_000_000)
        soporte.avanzar()
        pipeline = PipelineService([oportunidad, soporte])
        return empresa, oportunidad, cot, soporte, pipeline

    def test_escenario_obligatorio(self):
        empresa, oportunidad, cot, soporte, pipeline = self.escenario()
        self.assertEqual(empresa.identificacion(), "NIT 900373913-4")
        self.assertEqual(cot.subtotal, Decimal("30000000.00"))
        self.assertEqual(cot.descuento, Decimal("1500000.00"))
        self.assertEqual(cot.base, Decimal("28500000.00"))
        self.assertEqual(cot.iva, Decimal("5415000.00"))
        self.assertEqual(cot.total, Decimal("33915000.00"))
        self.assertEqual(oportunidad.valor, Decimal("28500000.00"))
        self.assertEqual(oportunidad.etapa, Etapa.GANADA)
        self.assertEqual(len(oportunidad.historial), 4)
        self.assertEqual(sum(a.minutos_invertidos() for a in oportunidad.actividades), 110)
        self.assertEqual(pipeline.pronostico_ponderado("Laura"), Decimal("2000000.00"))

    def test_reglas_invalidas_producen_error_dominio(self):
        empresa = Empresa(1, "Empresa", "a@b.co", "900373913")
        op = Oportunidad(1, empresa, "Laura", "Venta", 1_000_000)

        with self.assertRaises(ErrorDominio):
            op.ganar()  # no está en Negociación

        op.avanzar(); op.avanzar(); op.avanzar()
        with self.assertRaises(ErrorDominio):
            op.ganar()  # falta cotización aceptada

        cot = Cotizacion()
        with self.assertRaises(ErrorDominio):
            cot.enviar()  # sin líneas

        with self.assertRaises(ErrorDominio):
            DescuentoPorcentual(16)  # máximo 15%

    def test_cerrada_no_admite_cambios(self):
        _, op, _, _, _ = self.escenario()
        with self.assertRaises(OportunidadCerradaError):
            op.perder("Cambió de opinión")
        with self.assertRaises(OportunidadCerradaError):
            op.agregar_actividad(Llamada(datetime.now(), "Laura", "Intento", 5, False))
        with self.assertRaises(OportunidadCerradaError):
            op.agregar_cotizacion(Cotizacion())

    def test_contactos_encapsulados_y_un_principal(self):
        empresa = Empresa(1, "Empresa", "a@b.co", "900373913")
        empresa.agregar_contacto(Contacto("A", "Gerente", "a@empresa.co", True))
        self.assertIsInstance(empresa.contactos, tuple)
        with self.assertRaises(ValidacionError):
            empresa.agregar_contacto(Contacto("B", "Director", "b@empresa.co", True))


if __name__ == "__main__":
    unittest.main()
