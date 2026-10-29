"""Package the installed frontend dependencies, keeping licenses with assets."""
from pathlib import Path
import re
import shutil
ROOT=Path(__file__).resolve().parents[1]
vendor=ROOT/'frontend/vendor'
modules=ROOT/'.tools/node_modules'
shutil.copy2(modules/'chart.js/dist/chart.umd.js', vendor/'chart.umd.js')
shutil.copy2(modules/'chart.js/LICENSE.md', vendor/'Chart-LICENSE.md')
shutil.copy2(modules/'tailwindcss/LICENSE', vendor/'Tailwind-LICENSE.txt')
(vendor/'css').mkdir(exist_ok=True)
shutil.copy2(modules/'@fortawesome/fontawesome-free/css/all.min.css', vendor/'css/all.min.css')
shutil.copytree(modules/'@fortawesome/fontawesome-free/webfonts',vendor/'webfonts',dirs_exist_ok=True)
shutil.copy2(modules/'@fortawesome/fontawesome-free/LICENSE.txt',vendor/'FontAwesome-LICENSE.txt')
for path in (ROOT/'frontend').glob('*.html'):
    s=path.read_text(encoding='utf-8')
    s=s.replace('<script src="https://cdn.tailwindcss.com"></script>','<link rel="stylesheet" href="/static/vendor/tailwind.css">')
    s=re.sub(r'<script>\s*tailwind\.config\s*=.*?</script>', '',s, flags=re.S)
    s=s.replace('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css','/static/vendor/css/all.min.css')
    s=s.replace('https://cdn.jsdelivr.net/npm/chart.js','/static/vendor/chart.umd.js')
    path.write_text(s,encoding='utf-8')
p=ROOT/'frontend/css/custom.css'
s=p.read_text(encoding='utf-8')
s=re.sub(r"@import url\('https://fonts.googleapis.com/[^\n]*\n",'',s)
p.write_text(s,encoding='utf-8')
