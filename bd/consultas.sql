-- Dialecto: PostgreSQL

-- B1. Empresas sin ninguna oportunidad abierta.
SELECT c.id, c.nombre
FROM cliente AS c
WHERE c.tipo = 'E'
  AND NOT EXISTS (
      SELECT 1
      FROM oportunidad AS o
      WHERE o.cliente_id = c.id
        AND o.etapa NOT IN ('GANADA', 'PERDIDA')
  )
ORDER BY c.nombre;

-- B2. Indicadores de cierres 2026 por asesor activo.
SELECT
    a.id,
    a.nombre,
    COUNT(o.id) FILTER (WHERE o.etapa = 'GANADA') AS ganadas,
    COUNT(o.id) FILTER (WHERE o.etapa = 'PERDIDA') AS perdidas,
    COALESCE(SUM(o.valor) FILTER (WHERE o.etapa = 'GANADA'), 0) AS valor_total_ganado,
    COALESCE(
        ROUND(
            100.0 * COUNT(o.id) FILTER (WHERE o.etapa = 'GANADA')
            / NULLIF(COUNT(o.id), 0),
            1
        ),
        0.0
    ) AS tasa_conversion
FROM asesor AS a
LEFT JOIN oportunidad AS o
       ON o.asesor_id = a.id
      AND o.etapa IN ('GANADA', 'PERDIDA')
      AND o.fecha_cierre >= DATE '2026-01-01'
      AND o.fecha_cierre <  DATE '2027-01-01'
WHERE a.activo = TRUE
GROUP BY a.id, a.nombre
ORDER BY valor_total_ganado DESC, a.nombre;

-- B3. Oportunidades abiertas estancadas más de 15 días.
-- LATERAL + ORDER BY/LIMIT permite aprovechar el índice (oportunidad_id, fecha DESC)
-- para obtener la última actividad sin agrupar los 2 millones de registros completos.
SELECT
    o.id,
    o.titulo,
    a.nombre AS asesor,
    ua.ultima_fecha,
    CURRENT_DATE - COALESCE(ua.ultima_fecha::date, o.fecha_creacion) AS dias_sin_actividad
FROM oportunidad AS o
JOIN asesor AS a ON a.id = o.asesor_id
LEFT JOIN LATERAL (
    SELECT act.fecha AS ultima_fecha
    FROM actividad AS act
    WHERE act.oportunidad_id = o.id
    ORDER BY act.fecha DESC
    LIMIT 1
) AS ua ON TRUE
WHERE o.etapa NOT IN ('GANADA', 'PERDIDA')
  AND COALESCE(ua.ultima_fecha::date, o.fecha_creacion) < CURRENT_DATE - 15
ORDER BY dias_sin_actividad DESC, o.id;

-- B4. Cliente(s) con mayor valor ganado acumulado por ciudad, incluyendo empates.
WITH ganado_cliente AS (
    SELECT
        c.id AS cliente_id,
        c.ciudad,
        c.nombre,
        SUM(o.valor) AS total_ganado
    FROM cliente AS c
    JOIN oportunidad AS o
      ON o.cliente_id = c.id
     AND o.etapa = 'GANADA'
    GROUP BY c.id, c.ciudad, c.nombre
),
ranked AS (
    SELECT
        ciudad,
        nombre,
        total_ganado,
        DENSE_RANK() OVER (PARTITION BY ciudad ORDER BY total_ganado DESC) AS posicion
    FROM ganado_cliente
)
SELECT ciudad, nombre AS cliente, total_ganado
FROM ranked
WHERE posicion = 1
ORDER BY ciudad, cliente;

-- B5. Índices para acelerar B3.
CREATE INDEX idx_actividad_oportunidad_fecha_desc
    ON actividad (oportunidad_id, fecha DESC);

CREATE INDEX idx_oportunidad_abierta_fecha
    ON oportunidad (fecha_creacion, id)
    WHERE etapa NOT IN ('GANADA', 'PERDIDA');

-- Justificación B5:
-- El primer índice agrupa físicamente las actividades por oportunidad y fecha, facilitando obtener MAX(fecha).
-- El índice parcial evita recorrer oportunidades cerradas y ayuda a localizar las abiertas por fecha de creación.
-- Con 2M de actividades, el mayor beneficio viene del índice compuesto sobre actividad.
