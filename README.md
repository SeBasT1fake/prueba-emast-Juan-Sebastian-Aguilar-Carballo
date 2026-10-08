# Prueba Técnica — Desarrollador Junior

## Información

- **Lenguaje:** Python 3.12+
- **Pruebas:** `unittest`
- **SQL:** PostgreSQL
- **Dependencias externas:** ninguna

## Estructura

```text
prueba-emast-Juan-Sebastian-Aguilar-Carballo/
├── README.md
├── logica/
│   ├── __init__.py
│   ├── ejercicios.py
│   ├── test_ejercicios.py
│   └── SUSTENTACION.md
├── poo/
│   ├── __init__.py
│   ├── crm.py
│   ├── demo.py
│   ├── test_crm.py
│   ├── DECISIONES.md
│   └── FLUJO_IA.md
├── bd/
│   └── consultas.sql
└── diseno/
    └── DISENO.md
```

## Ejecución

Requisito: Python 3.12 o superior.

Desde la raíz del repositorio:

```bash
python -m unittest logica.test_ejercicios -v
python -m unittest poo.test_crm -v
python -m poo.demo
```

También se pueden ejecutar todas las pruebas:

```bash
python -m unittest discover -v
```

No se requiere instalar dependencias externas ni configurar una base de datos para ejecutar el código de la prueba.

## Resultado del escenario R6

- Identificación empresa: `NIT 900373913-4`
- Subtotal: `$30.000.000,00`
- Descuento por volumen: `$1.500.000,00`
- Base antes de IVA: `$28.500.000,00`
- IVA: `$5.415.000,00`
- Total: `$33.915.000,00`
- Valor final de la oportunidad ganada: `$28.500.000,00`
- Minutos invertidos: `110`
- Pronóstico ponderado de Laura: `$2.000.000,00`

## Criterios principales de implementación

- Para el cálculo del NIT normalizo la entrada y recorro los dígitos de derecha a izquierda con los pesos indicados.
- Para la agenda convierto las horas a minutos, recorto a la jornada, ordeno los intervalos y fusiono los que se solapan o son contiguos.
- Para los duplicados utilizo Union-Find porque la relación es transitiva.
- En POO uso clases abstractas, herencia y composición para representar el dominio.
- Las actividades utilizan polimorfismo mediante `minutos_invertidos()`.
- Las políticas de descuento utilizan una abstracción intercambiable para que una nueva política no obligue a modificar `Cotizacion`.
- Uso `Decimal` para los valores monetarios.
- Las reglas inválidas generan errores de dominio explícitos.
- Las colecciones internas se exponen como tuplas para evitar modificación externa accidental.
