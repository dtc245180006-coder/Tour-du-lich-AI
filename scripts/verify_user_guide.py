from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as E
from pypdf import PdfReader
import json, hashlib, re

root=Path(__file__).resolve().parents[1]
qa=root/'artifacts/user-guide'
report=json.loads((qa/'build.json').read_text(encoding='utf-8'))
out=Path(report['output'])
pdf=PdfReader(qa/'render-v2'/f'{out.stem}.pdf')
texts=[' '.join(p.extract_text().split()) for p in pdf.pages]
mapping={}
for heading,level,anchor in report['headings']:
    matches=[i for i,text in enumerate(texts[2:],2) if ' '.join(heading.split()) in text]
    assert matches,heading
    mapping[anchor]=matches[0]  # PDF zero-based index equals the retained footer number.
with ZipFile(out) as z: parts={n:z.read(n) for n in z.namelist()}
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
doc=E.fromstring(parts['word/document.xml'])
for field in doc.xpath('//w:fldSimple',namespaces=ns):
    instruction=field.get('{'+ns['w']+'}instr','')
    match=re.search(r'PAGEREF (UserGuide\d+)',instruction)
    if match:
        field.find('.//w:t',ns).text=str(mapping[match[1]])
parts['word/document.xml']=E.tostring(doc,encoding='UTF-8',xml_declaration=True,standalone=True)
with ZipFile(out,'w',ZIP_DEFLATED) as z:
    for name,data in parts.items():z.writestr(name,data)
text=' '.join(doc.xpath('//w:t/text()',namespaces=ns))
assert '<Tên Actor' not in text and 'nên chia theo' not in text
assert 'quản lý bán hàng' not in text
assert len(doc.xpath('//*[local-name()="blip"]'))==17
assert hashlib.sha256(Path(report['reference']).read_bytes()).hexdigest()==report['reference_sha256']
with ZipFile(report['reference']) as original:
    for name in ['word/styles.xml','word/numbering.xml','word/header1.xml','word/header2.xml','word/header3.xml','word/footer1.xml','word/footer2.xml','word/footer3.xml']:
        assert original.read(name)==parts[name],name
report['rendered_pages']=len(pdf.pages)
report['toc_cached_pages']=mapping
report['source_sha256']={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [root/'frontend/js/app.js',root/'frontend/js/ai_hub.js',root/'backend/app/routers/booking_router.py',root/'backend/app/routers/departure_router.py']}
(qa/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'pages':len(pdf.pages),'figures':17,'toc':mapping,'reference_unchanged':True},ensure_ascii=False))
