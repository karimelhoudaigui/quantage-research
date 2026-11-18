"""Regression for actual source corruption reported by the user."""
import importlib.util
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('paper_builder', ROOT/'scripts/build_paper.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class MathematicalRendering(unittest.TestCase):
    def test_control_characters_are_rejected_before_line_splitting(self):
        with self.assertRaises(ValueError):
            builder.latex('# Test\n\n$$C=\x0crac{1}{2}$$\n')

    def test_mathematical_bodies_survive_conversion(self):
        text = builder.TEMPLATE
        expected = re.findall(r'\$\$(.*?)\$\$', text, re.S)
        rendered = builder.latex(text)
        observed = re.findall(r'\\\[(.*?)\\\]', rendered, re.S)
        self.assertEqual(len(expected), 5)
        self.assertEqual(expected, observed)
        self.assertNotIn(r'\$\$', rendered)
        self.assertIn(r'd_i\geq1', rendered)

    def test_operators_and_complete_hamiltonian_are_present(self):
        text = builder.TEMPLATE
        self.assertFalse(any(ord(c)<32 and c not in '\t\n' for c in text))
        bodies = re.findall(r'\$\$(.*?)\$\$',text,re.S)
        requirements = [
            [r'\frac', r'\sum_i', r'\qquad'],
            [r'\sum_i', r'\in E', r'\max_i'],
            [r'\begin{pmatrix}', r'\cos', r'\sin', r'\end{pmatrix}'],
            [r'\frac', r'\prod_k'],
            [r'\Omega', r'\sum', r'\phi', r'\rangle\langle', r'\delta', r'\frac{C_6}{r^6}n_0n_1']
        ]
        for body,tokens in zip(bodies,requirements):
            for token in tokens:
                self.assertIn(token,body)

    def test_multiline_display_preserves_every_body_character(self):
        body = r'''
\begin{aligned}
H &= \frac{\Omega}{2}\sum_j |r_j\rangle\langle g_j|\\
  &\quad-\delta\sum_j n_j+\frac{C_6}{r^6}n_0n_1.
\end{aligned}
'''
        text = '# Multiligne\n\n$$' + body + '$$\n\nSuite du texte.\n'
        rendered = builder.latex(text)
        observed = re.findall(r'\\\[(.*?)\\\]', rendered, re.S)
        self.assertEqual(observed, [body])
        self.assertNotIn(r'\$\$', rendered)
        self.assertNotIn(r'\textbackslash{}frac', rendered)
        self.assertIn('Suite du texte.', rendered)

    def test_displays_can_start_or_end_on_body_lines_without_losing_newlines(self):
        text = '# Test\n\n$$a=1+\n2\nb=3$$\n\n$$c=4$$\n'
        rendered = builder.latex(text)
        self.assertEqual(re.findall(r'\\\[(.*?)\\\]', rendered, re.S),
                         ['a=1+\n2\nb=3', 'c=4'])

    def test_incomplete_display_is_rejected_instead_of_escaped_as_prose(self):
        for text in ('# Test\n\n$$\na=1\n', '# Test\n\n$$a=1$$ followed by prose\n',
                     '# Test\n\nBefore $$a=1$$\n', '# Test\n\n- Before $$a=1$$\n'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                builder.latex(text)

    def test_display_like_code_is_literal_and_adjacent_inline_math_is_valid(self):
        tick = chr(96)
        rendered = builder.latex('# Test\n\nCode ' + tick + '$$a=1$$' + tick + ' and $a$$b$.\n')
        self.assertIn(r'\texttt{\$\$a=1\$\$}', rendered)
        self.assertIn('$a$$b$', rendered)
        self.assertNotIn(r'\[', rendered)

    def test_all_unsupported_c0_characters_are_rejected(self):
        for code in range(32):
            if code in (9, 10):
                continue
            with self.subTest(code=code), self.assertRaises(ValueError):
                builder.latex('# Test\n\n$$a=' + chr(code) + '1$$\n')

    def test_table_pipes_in_math_code_and_escaped_text_are_not_columns(self):
        tick = chr(96)
        text = ('# Table\n\n| Norme | Code | Texte |\n|---|---|---|\n'
                + '| $|x|$ | ' + tick + 'a|b' + tick + r' | a\|b |' + '\n')
        rendered = builder.latex(text)
        row = next(line for line in rendered.split('\n') if '$|x|$' in line)
        self.assertEqual(row, r'$|x|$ & \texttt{a|b} & a|b\\')
        self.assertEqual(row.count(' & '), 2)
        self.assertIn(r'\begin{longtable}', rendered)
        self.assertEqual(rendered.count(r'p{\QAcolumnwidth}'), 3)

    def test_math_commands_and_backslashes_in_code_keep_their_distinct_meanings(self):
        tick = chr(96)
        text = ('# Table\n\n| Math | Code |\n|---|---|\n'
                + r'| $\|x\|$ | ' + tick + r'a\|b' + tick + ' |\n')
        rendered = builder.latex(text)
        row = next(line for line in rendered.split('\n') if r'$\|x\|$' in line)
        self.assertIn(r'$\|x\|$', row)
        self.assertIn(r'\texttt{a\textbackslash{}|b}', row)
        self.assertEqual(row.count(' & '), 1)

    def test_multiple_backtick_code_delimiters_protect_internal_backtick_and_pipe(self):
        tick = chr(96)
        text = ('# Table\n\n| Code | Valeur |\n|---|---|\n| '
                + tick * 2 + 'a' + tick + '|b' + tick * 2 + ' | 1 |\n')
        rendered = builder.latex(text)
        row = next(line for line in rendered.split('\n') if r'\texttt{' in line)
        self.assertEqual(row.count(' & '), 1)
        self.assertIn('a' + tick + '|', row)
        self.assertNotIn(tick * 2, row)

    def test_long_table_uses_wrapping_columns_and_repeatable_page_heads(self):
        tick = chr(96)
        literal = 'quantage/' + 'long_identifier_' * 8 + 'module.py'
        lines = ['# Longue table', '', '| Fichier | Description | Nombre |',
                 '|---|---|---:|']
        lines.extend('| ' + tick + literal + tick
                     + ' | Texte descriptif avec plusieurs mots. | ' + str(i) + ' |'
                     for i in range(120))
        rendered = builder.latex('\n'.join(lines) + '\n')
        self.assertEqual(rendered.count(r'\begin{longtable}'), 1)
        self.assertEqual(rendered.count(r'\end{longtable}'), 1)
        self.assertIn(r'\endfirsthead', rendered)
        self.assertIn(r'\endhead', rendered)
        self.assertIn(r'\endfoot', rendered)
        self.assertIn(r'\endlastfoot', rendered)
        self.assertEqual(rendered.count('Fichier & Description & Nombre'), 2)
        self.assertNotIn(r'\begin{center}', rendered)
        self.assertNotIn(r'\begin{tabularx}', rendered)
        self.assertIn(r'\allowbreak{}', rendered)
        self.assertIn(r'\dimexpr\linewidth-4\tabcolsep\relax', rendered)
        without_optional_breaks = rendered.replace(r'\allowbreak{}', '')
        self.assertIn(r'\texttt{' + builder.escape(literal) + '}', without_optional_breaks)
        self.assertIn(' & 119' + r'\\', rendered)

    def test_table_alignment_is_preserved_and_bad_column_counts_are_rejected(self):
        rendered = builder.latex('# Test\n\n| A | B | C |\n|---|---:|:---:|\n| a | b | c |\n')
        self.assertIn(r'>{\raggedright\arraybackslash}p{\QAcolumnwidth}', rendered)
        self.assertIn(r'>{\raggedleft\arraybackslash}p{\QAcolumnwidth}', rendered)
        self.assertIn(r'>{\centering\arraybackslash}p{\QAcolumnwidth}', rendered)
        for text in ('# Test\n\n| A | B |\n|---|---|\n| one |\n',
                     '# Test\n\n| A | B |\n|---|\n| one | two |\n',
                     '# Test\n\n| A | B |\n|---|---|\n| $unclosed | two |\n'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                builder.latex(text)


if __name__ == '__main__':
    unittest.main()
