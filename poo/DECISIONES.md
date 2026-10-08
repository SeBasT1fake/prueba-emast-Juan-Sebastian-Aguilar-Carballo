# Decisiones de diseño

## 1. Herencia y composición
Usé herencia en `Cliente` → `PersonaNatural`/`Empresa` y `Actividad` → sus tipos porque comparten contrato y comportamiento polimórfico. Usé composición para Empresa–Contactos, Oportunidad–Actividades/Cotizaciones e inyección de `PoliticaDescuento`, porque son partes o estrategias que pueden variar independientemente.

## 2. Descuento de temporada
Crearía `DescuentoTemporada(PoliticaDescuento)` e implementaría `calcular(subtotal)` devolviendo 10% en diciembre y 0 en otro mes. Para evitar que dependa del reloj global, le inyectaría la fecha o un proveedor de fecha. `Cotizacion` no cambia: depende de la abstracción `PoliticaDescuento`.

## 3. Etapas configurables por cliente
Reemplazaría el `Enum Etapa` y el mapa `_SIGUIENTE` por objetos/configuración de pipeline asociados al cliente: etapa, orden, probabilidad y tipo de cierre. `Oportunidad` referenciaría una etapa configurada y delegaría la validez de transiciones a ese pipeline.
