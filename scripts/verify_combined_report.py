from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from collections import Counter
from lxml import etree as E
from pypdf import PdfReader
import json, re, hashlib, sys

ROOT=Path(__file__).resolve().parents[1]
QA=ROOT/'artifacts/combined-report'
meta=json.loads((QA/'manifest.json').read_text(encoding='utf-8'))
out=Path(meta['output'])
pdf=PdfReader(QA/(sys.argv[1] if len(sys.argv)>1 else 'render-v3')/f'{out.stem}.pdf')
texts=[' '.join((p.extract_text() or '').split()) for p in pdf.pages]
toc={}
for item in meta['headings']:
    if not item['toc'] or item['level']>2:continue
    needle=' '.join(item['text'].split())
    matches=[i+1 for i,t in enumerate(texts) if i>=3 and needle in t]
    assert matches,item['text']
    toc[item['anchor']]=matches[0]
with ZipFile(out) as z:parts={n:z.read(n) for n in z.namelist()}
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
doc=E.fromstring(parts['word/document.xml'])
for fld in doc.xpath('//w:fldSimple',namespaces=ns):
    instruction=fld.get('{'+ns['w']+'}instr','')
    m=re.search(r'PAGEREF (ReportHeading\d+)',instruction)
    if m:fld.find('.//w:t',ns).text=str(toc[m[1]])
parts['word/document.xml']=E.tostring(doc,encoding='UTF-8',xml_declaration=True,standalone=True)
with ZipFile(out,'w',ZIP_DEFLATED) as z:
    for name,blob in parts.items():z.writestr(name,blob)
actual_hashes=Counter(hashlib.sha256(blob).hexdigest() for name,blob in parts.items() if name.startswith('word/media/'))
expected_hashes=Counter(x['sha256'] for x in meta['figures'])
assert actual_hashes==expected_hashes
assert len(meta['cases'])==49
assert len(meta['schemas'])==10
assert len(meta['sources'])==7
for s in meta['sources']:
    assert hashlib.sha256((ROOT/'docs'/s['name']).read_bytes()).hexdigest()==s['sha256'],s['name']
alltext=' '.join(texts)
assert len(set(re.findall(r'G\d{2}-TC\d{2}',alltext)))==49
assert len(re.findall(r'Hình \d+\.',alltext))==38
assert '<Tên Actor' not in alltext
assert not any('Reference source not found' in t or 'Error!' in t for t in texts)
blank=[i+1 for i,t in enumerate(texts) if len(re.sub(r'VIETJOURNEY AI.*?NHÓM 17|\d|\s','',t))<3]
assert not blank,blank
audit={'output':str(out),'pages':len(pdf.pages),'sources_unchanged':True,'image_bytes_preserved':38,'historical_cases':49,'tables':len(meta['tables']),'cached_toc':toc,'schema_tables':10,'blank_pages':blank,'sha256':hashlib.sha256(out.read_bytes()).hexdigest()}
(QA/'verification.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:audit[k] for k in ['pages','image_bytes_preserved','historical_cases','schema_tables','sources_unchanged']},ensure_ascii=False))
