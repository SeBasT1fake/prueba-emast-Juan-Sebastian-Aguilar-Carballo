# Sustentación — Sección 1

## 1.1 Dígito de verificación
Limpio únicamente puntos y espacios, valido longitud/contenido y recorro el NIT de derecha a izquierda con los pesos dados. `validar_nit` encapsula cualquier error y devuelve `False`, como exige el enunciado.

**Casos probados:** los cinco ejemplos, entrada vacía y formato inválido.

**Complejidad:** O(n) tiempo y O(n) espacio por la cadena limpia, con n <= 15.

## 1.2 Agenda
Convierto las horas a minutos desde medianoche. Recorto reuniones a la jornada, agrego el almuerzo, ordeno y fusiono intervalos que se solapan o se tocan. Luego recorro los bloques fusionados para obtener huecos con duración suficiente.

**Supuesto:** una reunión con formato inválido o con inicio >= fin es error. Una reunión totalmente fuera de jornada se ignora.

**Casos probados:** ejemplo completo, agenda vacía, una reunión que cubre toda la jornada y un intervalo invertido.

**Complejidad:** O(n log n) por ordenar; la fusión y búsqueda de huecos son O(n).

## 1.3 Duplicados
Normalizo email/teléfono y uso Union-Find (Disjoint Set Union). Cuando un email o teléfono ya apareció, uno ambos IDs. Esto representa naturalmente la transitividad pedida sin comparar todos contra todos.

**Supuestos:** los IDs deben ser únicos; email/teléfono vacíos no generan vínculos. Solo se elimina `57` cuando el teléfono normalizado tiene exactamente 12 dígitos y empieza por `57`.

**Casos probados:** ejemplo, registros sin datos de contacto y encadenamiento transitivo implícito del ejemplo.

**Complejidad:** O(n α(n)) amortizado, aproximadamente lineal; memoria O(n).
