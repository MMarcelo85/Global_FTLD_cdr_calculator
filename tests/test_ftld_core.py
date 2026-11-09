"""Run with:  python -m unittest discover -s tests"""
import csv
import gzip
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import ftld_core  # noqa: E402

KEYS = [k for k, _ in ftld_core.DOMAINS]


class TestScoring(unittest.TestCase):
    def test_golden_all_combinations(self):
        """All 312,500 valid combinations (5^7 x 4, Personal care cannot be 0.5).
        Golden file generated from the original main.py (commit 58f0417, 25/02/26) with no changes:
        the original results already follow the rules in README.md in every combination."""
        with gzip.open(os.path.join(HERE, "golden_ftld_cdr.csv.gz"), "rt", newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 312500)
        for r in rows:
            scores = [float(r[k]) for k in KEYS]
            cdr, rule = ftld_core.calculate_ftld_cdr(scores)
            self.assertEqual((float(cdr), rule), (float(r["ftld_cdr_global"]), ftld_core.RULES[r["rule"]]),
                             msg=f"scores={scores}")

    def test_known_examples(self):
        cases = [([0] * 8, 0, "1"),
                 ([0.5, 0, 0, 0, 0, 0, 0.5, 0], 0.5, "2"),
                 ([0, 0, 0, 0, 0, 0, 1, 0], 0.5, "3a"),
                 ([0, 0, 0, 0, 0, 0, 0, 3], 1, "3b"),
                 ([3, 0.5, 0, 0, 0, 0, 0, 0], 2, "3c"),
                 ([0, 0, 0, 0, 0, 0, 2, 1], 1, "3c"),
                 ([0.5, 0, 0, 0, 0, 0, 1, 0], 0.5, "3c"),
                 ([1, 0, 0, 0, 0, 0, 1, 0], 1, "3d"),
                 ([2, 1, 1, 0, 0, 0, 2, 3], 2, "3c"),
                 ([3, 1, 1, 0, 0, 0, 2, 3], 3, "3d")]
        for scores, expected, rule in cases:
            self.assertEqual(ftld_core.calculate_ftld_cdr(scores), (expected, ftld_core.RULES[rule]),
                             msg=f"scores={scores}")

    def test_self_test(self):
        """The checks run on the packaged executable (desktop_app.py --self-test)."""
        self.assertEqual(ftld_core.self_test(), [])

    def test_invalid_input(self):
        for scores in ([0, 0, 0, 0, 0, 0.5, 0, 0],   # personal care cannot be 0.5
                       [4, 0, 0, 0, 0, 0, 0, 0],     # out of range
                       [9, 1, 0, 0, 0, 0, 0, 0],     # "unknown" code
                       [0] * 7):                     # wrong number of domains
            with self.assertRaises(ValueError):
                ftld_core.calculate_ftld_cdr(scores)


class TestCSV(unittest.TestCase):
    def test_positional_eight_columns(self):
        text = "Memory,box1,box2,box3,box4,box5,box6,box7\n3,0.5,0,0,0,0,0,0\n0,0,0,0,0,0,1,0\n"
        header, rows, out, _ = ftld_core.process_csv(text)
        self.assertEqual(header[-3:], ["FTLD_CDR_global", "Rule_applied", "FTLD_CDR_note"])
        self.assertEqual([r[-3] for r in rows], ["2", "0.5"])
        self.assertEqual(rows[0][-2], ftld_core.RULES["3c"])

    def test_positional_unknown_names(self):
        _, rows, _, _ = ftld_core.process_csv("a,b,c,d,e,f,g,h\n1,1,0,0,0,0,0,0\n")
        self.assertEqual(rows[0][-3:], ["1", ftld_core.RULES["3d"], ""])

    def test_id_column_semicolon_decimal_comma_and_errors(self):
        text = ("ID;Memoria;Orientación;Juicio;Comunidad;Hogar;Cuidado personal;Comportamiento;Lenguaje\n"
                "A01;0,5;1;1;0;0;0;0;0\n"
                "A02;1;0;0;;0;0;0;0\n"
                "A03;1;0;0;0;0;0,5;0;0\n"
                "A04;0;0;0;0;0;0;0,5;0\n")
        header, rows, out, summary = ftld_core.process_csv(text)
        self.assertEqual(rows[0][:1] + rows[0][-3:], ["A01", "1", ftld_core.RULES["3d"], ""])
        self.assertEqual(rows[1][-3:], ["", "", "missing score(s)"])
        self.assertIn("Personal Care", rows[2][-1])
        self.assertEqual(rows[3][-3], "0,5")  # decimal comma for semicolon files
        self.assertIn(";", out.splitlines()[0])
        self.assertIn("2 rows scored, 2 rows", summary)

    def test_nacc_names_tab_and_extra_columns(self):
        text = ("PTID\tVISIT\tMEMORY\tORIENT\tJUDGMENT\tCOMMUN\tHOMEHOBB\tPERSCARE\tCOMPORT\tCDRLANG\n"
                "X1\t1\t0\t0\t0\t0\t0\t0\t2\t0\n")
        header, rows, out, _ = ftld_core.process_csv(text)
        self.assertEqual(rows[0][-3], "1")  # Rule 3B
        self.assertIn("\t", out.splitlines()[0])

    def test_latin1_and_invalid_code(self):
        data = "ID,Memoria,Orientación,Juicio,Comunidad,Hogar,Cuidado,Conducta,Lenguaje\nñ,9,1,0,0,0,0,0,0\n"
        _, rows, _, _ = ftld_core.process_csv(ftld_core.decode(data.encode("latin-1")))
        self.assertEqual(rows[0][0], "ñ")
        self.assertIn("invalid Memory score: 9", rows[0][-1])

    def test_rerun_on_output_replaces_columns(self):
        _, _, out, _ = ftld_core.process_csv("Memory,box1,box2,box3,box4,box5,box6,box7\n0,0,0,0,0,0,0,0\n")
        header, rows, _, _ = ftld_core.process_csv(out)
        self.assertEqual(header.count("FTLD_CDR_global"), 1)
        self.assertEqual(rows[0][-3], "0")

    def test_old_app_output_is_accepted(self):
        """Files produced by the previous web app: 8 columns plus FTLD_CDR_global."""
        _, rows, _, _ = ftld_core.process_csv("Memory,box1,box2,box3,box4,box5,box6,box7,FTLD_CDR_global\n"
                                              "1,1,0,0,0,0,0,0,1.0\n")
        self.assertEqual(rows[0][-3], "1")

    def test_unidentifiable_columns(self):
        with self.assertRaises(ValueError):
            ftld_core.process_csv("ID,a,b,c,d,e,f,g,h\n1,0,0,0,0,0,0,0,0\n")


class TestAbout(unittest.TestCase):
    def test_license_text_matches_license_file(self):
        import desktop_app  # importing tkinter does not need a display
        with open(os.path.join(os.path.dirname(HERE), "LICENSE"), encoding="utf-8") as f:
            self.assertEqual(desktop_app.LICENSE_TEXT.strip(), f.read().strip())


if __name__ == "__main__":
    unittest.main()
