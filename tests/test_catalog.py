import ast,json,re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/'wusel'

class CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source=(ROOT/'static'/'i18n.js').read_text(encoding='utf-8')
        cls.catalog=json.JSONDecoder().raw_decode(source.split('=',1)[1].lstrip())[0]
    def test_catalogs_cover_same_keys_and_interpolation_fields(self):
        self.assertEqual(set(self.catalog['en']),set(self.catalog['de']))
        for key,en in self.catalog['en'].items():
            de=self.catalog['de'][key]
            self.assertTrue(de,key)
            self.assertEqual(sorted(re.findall(r'\{(\w+)\}',en)),sorted(re.findall(r'\{(\w+)\}',de)),key)
    def test_every_static_backend_error_is_translated(self):
        tree=ast.parse((ROOT/'app.py').read_text(encoding='utf-8'))
        for node in ast.walk(tree):
            if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='Problem' and node.args and isinstance(node.args[0],ast.Constant):
                self.assertIn(node.args[0].value,self.catalog['de'])
    def test_ui_direct_lookup_keys_exist(self):
        source=(ROOT/'static'/'app.js').read_text(encoding='utf-8')
        for quote,key in re.findall(r'\b(?:t|tx)\(([\"\'])(.*?)\1',source):
            self.assertIn(key,self.catalog['en'])

if __name__=='__main__':unittest.main()
