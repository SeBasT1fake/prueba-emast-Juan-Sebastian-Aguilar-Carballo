# Flujo de uso de Inteligencia Artificial

En esta sección utilicé ChatGPT como apoyo para generar y revisar código, de acuerdo con la política de uso de IA de la prueba.

## Herramienta y modelo

- Herramienta: ChatGPT
- Modelo: GPT-5.6 Luna

## Flujo de trabajo

1. Primero revisé las reglas del dominio y definí las clases, responsabilidades, estados y relaciones que necesitaba.
2. Separé las responsabilidades entre clientes, oportunidades, actividades, cotizaciones, políticas de descuento y servicio de pipeline.
3. Utilicé IA para obtener una implementación inicial de algunas clases y métodos.
4. Revisé el código generado contra cada regla R1–R6 del enunciado.
5. Corregí validaciones, encapsulamiento, transiciones de estado y manejo de errores cuando era necesario.
6. Agregué pruebas para el escenario principal y para reglas que deben producir errores.
7. Ejecuté las pruebas y verifiqué manualmente los resultados del escenario obligatorio.

## Prompts utilizados

La implementación se construyó de forma iterativa. Los prompts principales utilizados fueron solicitudes equivalentes a:

1. "Ayúdame a implementar el modelo de dominio de un CRM en Python respetando estas reglas de clientes, oportunidades, actividades y cotizaciones."
2. "Revisa esta implementación contra las reglas del dominio e identifica errores o reglas que falten."
3. "Agrega pruebas unitarias para las reglas inválidas y para el escenario R6."

## Qué acepté y qué revisé

Acepté como base la estructura de clases y parte del código repetitivo generado, pero revisé y ajusté las reglas de negocio, las validaciones, las transiciones de estado, el encapsulamiento y los cálculos monetarios.

No considero que el código generado sea correcto únicamente por haber sido generado por IA: lo contrasté con el enunciado y con las pruebas.

## Verificación

Verifiqué especialmente:

- que una oportunidad nueva empiece en Prospecto;
- que no pueda avanzar desde Negociación;
- que solo pueda ganarse desde Negociación con una cotización Aceptada;
- que una oportunidad cerrada no admita nuevas actividades ni cotizaciones;
- que una cotización no pueda enviarse sin líneas;
- que las líneas y la política solo puedan modificarse en Borrador;
- que solo exista un contacto principal por empresa;
- que los cálculos de descuento, base, IVA y total sean correctos.
