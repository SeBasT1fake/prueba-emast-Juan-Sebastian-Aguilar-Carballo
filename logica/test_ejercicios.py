import unittest

from logica.ejercicios import calcular_dv, validar_nit, bloques_ocupados, espacios_libres, agrupar_duplicados


class LogicaTests(unittest.TestCase):
    def test_dv_ejemplos(self):
        self.assertEqual(calcular_dv("900373913"), 4)
        self.assertEqual(calcular_dv("890.903.938"), 8)
        self.assertEqual(calcular_dv("800197268"), 4)
        self.assertTrue(validar_nit("900373913-4"))
        self.assertFalse(validar_nit("900.373.913-5"))

    def test_dv_bordes(self):
        with self.assertRaises(ValueError):
            calcular_dv("90037A913")
        with self.assertRaises(ValueError):
            calcular_dv("   ")
        self.assertFalse(validar_nit("texto"))

    def test_agenda_ejemplo(self):
        reuniones = ["09:00-10:00", "09:30-10:30", "10:30-11:00", "14:00-15:15",
                     "07:00-08:30", "16:45-17:30", "11:50-12:20"]
        self.assertEqual(bloques_ocupados(reuniones), [
            "08:00-08:30", "09:00-11:00", "11:50-13:00", "14:00-15:15", "16:45-17:30"
        ])
        self.assertEqual(espacios_libres(reuniones, 30), [
            "08:30-09:00", "11:00-11:50", "13:00-14:00", "15:15-16:45", "17:30-18:00"
        ])
        self.assertEqual(espacios_libres(reuniones, 60), ["13:00-14:00", "15:15-16:45"])
        self.assertEqual(espacios_libres([], 60), ["08:00-12:00", "13:00-18:00"])

    def test_agenda_bordes(self):
        self.assertEqual(bloques_ocupados(["00:00-23:59"]), ["08:00-18:00"])
        with self.assertRaises(ValueError):
            espacios_libres(["10:00-09:00"], 30)

    def test_duplicados_ejemplo_y_bordes(self):
        registros = [
            (1, "Ana Gómez", "ana.gomez@acme.co", "+57 300 123 4567"),
            (2, "Ana M. Gómez", " ANA.GOMEZ@acme.co ", "3001234567"),
            (3, "Carlos Ruiz", "cruiz@beta.com", "(604) 444-5566"),
            (4, "Distribuciones Beta", "compras@beta.com", "604 444 5566"),
            (5, "A. Gómez", "agomez@gmail.com", "573001234567"),
            (6, "Luisa Pérez", "", ""),
            (7, "Luisa Perez", "", None),
            (8, "Compras Beta", "COMPRAS@BETA.COM", ""),
            (9, "Pedro Díaz", "pdiaz@gamma.co", "310 999 8877"),
            (10, "Pedro A. Díaz", "pedro.diaz@gamma.co", "57 310 999 88 77"),
        ]
        self.assertEqual(agrupar_duplicados(registros), [[1, 2, 5], [3, 4, 8], [9, 10]])
        self.assertEqual(agrupar_duplicados([(1, "A", "", ""), (2, "A", None, None)]), [])


if __name__ == "__main__":
    unittest.main()
