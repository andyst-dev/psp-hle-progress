"""Synthetic inputs and public report data only; no game files required."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'tools' / (name + '.py'))
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class CoverageTests(unittest.TestCase):
    def generate(self, extra=()):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        path = Path(temp.name)
        (path/'imports.c').write_text('/* sceCtrl :: NID 0xAAAAAAAA */\n/* sceCtrl :: NID 0xBBBBBBBB */\n/* sceRtc :: NID 0xCCCCCCCC */\n')
        (path/'hle.tsv').write_text('AAAAAAAA\tsceCtrl\tsyntheticHandler\n')
        result = subprocess.run([sys.executable, str(ROOT/'tools/hle_coverage.py'), str(path/'imports.c'), str(path/'hle.tsv'), '--outdir', str(path), '--reached', 'AAAAAAAA,BBBBBBBB'] + list(extra), capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return path, json.loads((path/'data/locoroco-hle-cov.json').read_text())

    def test_reached_only_marks_missing_imports(self):
        _, data = self.generate()
        self.assertEqual(data['atteints'], [['sceCtrl', 'BBBBBBBB']])

    def test_report_does_not_claim_registration_is_implementation(self):
        path, data = self.generate()
        self.assertEqual(data.get('metric'), 'registered_hle_handler_availability')
        report = (path/'docs/progress/hle-missing.md').read_text()
        self.assertIn('registered handler', report)
        self.assertNotIn('are implemented', report)

    def test_source_revision_is_recorded(self):
        _, data = self.generate(['--source-ref', '1'*40, '--source-label', 'Synthetic checkout'])
        self.assertEqual(data['source'], {'revision': '1'*40, 'label': 'Synthetic checkout'})

    def test_invalid_measurements_fail_loudly(self):
        fixtures = [
            ('duplicate', '/* sceCtrl :: NID 0xAAAAAAAA */\n'*2, [], 'duplicate'),
            ('unclassified', '/* UnknownLibrary :: NID 0xAAAAAAAA */\n', [], 'family'),
            ('empty revision', '/* sceCtrl :: NID 0xAAAAAAAA */\n', ['--source-ref', ''], 'Git revision'),
        ]
        for name, imports, extra, reason in fixtures:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                path = Path(temp)
                (path/'imports.c').write_text(imports)
                (path/'hle.tsv').write_text('AAAAAAAA\tsceCtrl\tsyntheticHandler\n')
                result = subprocess.run([sys.executable, str(ROOT/'tools/hle_coverage.py'), str(path/'imports.c'), str(path/'hle.tsv'), '--outdir', str(path)] + extra, capture_output=True, text=True)
                self.assertEqual(result.returncode, 2)
                self.assertIn(reason, result.stderr)

    def test_treemap_legend_uses_data_not_old_run(self):
        module = load('hle_treemap')
        _, data = self.generate()
        data['atteints'] = [['sceCtrl', 'BBBBBBBB']]
        svg, _ = module.build(data, 1200, 820)
        text = ''.join(ET.fromstring(svg).itertext())
        self.assertNotIn('sceUmdUser x4', text)
        self.assertIn('registered', text)
        self.assertIn('1 observed missing import', text)

class ArtifactTests(unittest.TestCase):
    def test_snapshot_totals_and_reached_sets(self):
        for path in (ROOT/'data').glob('*-hle-cov.json'):
            data = json.loads(path.read_text())
            self.assertEqual(sum(sum(v) for v in data['cov'].values()), data['imports'])
            self.assertEqual(sum(v[0] for v in data['cov'].values()), data['covered'])
            self.assertEqual(len(data['registered']), data['covered'])
            missing = {(lib, nid) for lib, nids in data['missing'].items() for nid in nids}
            self.assertEqual(len(missing), data['imports'] - data['covered'])
            self.assertTrue({tuple(x) for x in data['atteints']} <= missing)
            families = [lib for _, libs in data['familles'] for lib in libs]
            self.assertTrue(set(data['cov']) <= set(families))
            self.assertEqual(len(families), len(set(families)))

    def test_diagram_geometry_and_labels(self):
        module = load('hle_treemap')
        data = json.loads((ROOT/'data/locoroco-hle-cov.json').read_text())
        for theme in ['light', 'dark']:
            svg, _ = module.build(data, 1200, 820, theme=theme)
            tree = ET.fromstring(svg)
            families, libraries, labels, rings = [], [], [], []
            current = None
            for el in tree:
                tag = el.tag.rsplit('}', 1)[-1]
                if tag == 'line': current = None
                if tag == 'rect' and el.get('stroke-width') in ['1.2', '0.7']:
                    box = tuple(float(el.attrib[k]) for k in ['x', 'y', 'width', 'height'])
                    if el.get('stroke-width') == '1.2':
                        families.append(box); current = None
                    else:
                        libraries.append(box); current = box
                if tag == 'text' and current:
                    labels.append((current, el))
                if tag == 'circle' and el.get('r') == '4.2':
                    rings.append((current, float(el.attrib['cx']), float(el.attrib['cy'])))
            self.assertEqual(len(libraries), len(data['cov']))
            self.assertEqual(len(rings), len({lib for lib, _ in data['atteints']}))
            expected_area = (1200 - 52) * (820 - 118 - 166)
            self.assertAlmostEqual(sum(w*h for x, y, w, h in families), expected_area, delta=expected_area*0.0001)
            for boxes in [families, libraries]:
                for i, (x, y, w, h) in enumerate(boxes):
                    for a, b, c, d in boxes[i+1:]:
                        overlap_x = min(x+w, a+c) - max(x, a)
                        overlap_y = min(y+h, b+d) - max(y, b)
                        self.assertTrue(overlap_x <= 0.02 or overlap_y <= 0.02)
            for (x, y, w, h), el in labels:
                text = ''.join(el.itertext()); size = float(el.attrib['font-size'])
                width = len(text)*module.CHAR_W*size
                if el.get('transform'):
                    self.assertLessEqual(width, h - 2*module.PAD + 0.2)
                    continue
                left = float(el.attrib['x'])
                if el.get('text-anchor') == 'middle': left -= width/2
                right = left + width
                self.assertGreaterEqual(left, x - 0.2)
                self.assertLessEqual(right, x+w + 0.2)
                for box, cx, cy in rings:
                    if box == (x, y, w, h):self.assertLessEqual(right, cx - 4.2 - 0.5)
            for el in tree:
                if el.tag.endswith('text'):
                    self.assertLessEqual(float(el.attrib['y']), 812)

    def test_readme_matches_data_and_cached_images(self):
        import hashlib
        import re
        data = json.loads((ROOT/'data/locoroco-hle-cov.json').read_text())
        text = (ROOT/'README.md').read_text()
        self.assertIn(str(data['covered'])+'/'+str(data['imports']), text)
        for name in re.findall(r'(docs/progress/hle-coverage(?:-dark)?\.([0-9a-f]{12})\.png)', text):
            self.assertEqual(hashlib.sha256((ROOT/name[0]).read_bytes()).hexdigest()[:12], name[1])
        self.assertEqual(len(re.findall(r'docs/progress/hle-coverage(?:-dark)?\.[0-9a-f]{12}\.png', text)), 2)
        import shutil
        with tempfile.TemporaryDirectory() as temp:
            copy = Path(temp)
            (copy/'data').mkdir()
            (copy/'docs/progress').mkdir(parents=True)
            for path in (ROOT/'data').glob('*-hle-cov.json'):
                shutil.copyfile(path, copy/'data'/path.name)
            for name in ['hle-coverage.png', 'hle-coverage-dark.png']:
                shutil.copyfile(ROOT/'docs/progress'/name, copy/'docs/progress'/name)
            self.assertEqual(load('update_readme').render(copy), text)

if __name__ == '__main__':
    unittest.main()
