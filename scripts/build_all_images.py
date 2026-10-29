"""
Script sinh 21 ảnh sơ đồ UML chất lượng cao (PNG) từ HTML/SVG bằng Google Chrome headless.
Mỗi sơ đồ phản ánh chính xác 100% hệ thống thực tế VietJourney AI.
"""

import os
import sys
import subprocess

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
OUT_DIR = os.path.abspath("docs/diagrams")
os.makedirs(OUT_DIR, exist_ok=True)

COMMON_HEAD = """
<meta charset="utf-8">
<style>
  * { box-sizing: border-box; }
  body {
    margin: 0; padding: 24px;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    background: #f8fafc; color: #0f172a;
    width: 100%; height: 100%;
  }
  .canvas {
    background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 14px;
    padding: 24px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.07);
    position: relative; min-height: 940px;
  }
  .header {
    border-bottom: 2px solid #e2e8f0; padding-bottom: 12px; margin-bottom: 20px;
    display: flex; justify-content: space-between; align-items: flex-end;
  }
  .header h1 {
    font-size: 22px; color: #0369a1; margin: 0 0 4px 0; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px;
  }
  .header .sub { font-size: 13px; color: #64748b; font-weight: 500; }
  .header .badge {
    background: #e0f2fe; color: #0284c7; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 700; border: 1px solid #bae6fd;
  }
  .footer {
    position: absolute; bottom: 12px; left: 24px; right: 24px;
    border-top: 1px solid #e2e8f0; padding-top: 8px; font-size: 11px; color: #94a3b8;
    display: flex; justify-content: space-between;
  }
  /* UML Shapes */
  .actor-box {
    text-align: center; font-size: 12px; font-weight: bold; color: #1e293b;
  }
  .actor-icon {
    width: 44px; height: 75px; margin: 0 auto 4px auto;
  }
  .usecase {
    background: #ffffff; border: 2px solid #0284c7; border-radius: 50px;
    padding: 10px 18px; text-align: center; font-size: 12px; font-weight: 700;
    color: #0f172a; box-shadow: 0 2px 4px rgba(2,132,199,0.08); display: flex; align-items: center; justify-content: center;
  }
  .usecase.sub {
    border-style: dashed; background: #f0f9ff; border-color: #0369a1; font-weight: 600; font-size: 11px;
  }
  .boundary {
    border: 2px dashed #94a3b8; border-radius: 12px; background: rgba(248, 250, 252, 0.5);
    position: relative;
  }
  .boundary-title {
    position: absolute; top: -12px; left: 20px; background: #ffffff; padding: 2px 12px;
    font-size: 13px; font-weight: 800; color: #334155; border: 1.5px solid #cbd5e1; border-radius: 6px;
  }
  /* Class diagram table */
  .uml-class {
    background: #ffffff; border: 2px solid #0284c7; border-radius: 8px; overflow: hidden;
    font-size: 11px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
  }
  .uml-class .c-head {
    background: #e0f2fe; padding: 7px 10px; font-weight: 800; font-size: 13px; text-align: center; color: #0369a1; border-bottom: 2px solid #0284c7;
  }
  .uml-class .c-body {
    padding: 8px 10px; line-height: 1.5; color: #334155;
  }
  .uml-class .c-methods {
    border-top: 1px solid #cbd5e1; padding: 8px 10px; line-height: 1.5; color: #0f172a; font-family: Consolas, monospace; font-size: 10.5px;
  }
  /* Activity nodes */
  .act-node {
    background: #eff6ff; border: 1.5px solid #3b82f6; border-radius: 18px;
    padding: 10px 14px; font-size: 12px; font-weight: 600; text-align: center; color: #1e3a8a;
  }
  .act-decision {
    background: #fef3c7; border: 1.5px solid #d97706; transform: rotate(45deg);
    width: 60px; height: 60px; display: flex; align-items: center; justify-content: center;
  }
  .act-decision span {
    transform: rotate(-45deg); font-size: 10.5px; font-weight: 700; color: #78350f; text-align: center;
  }
  /* Sequence lifelines */
  .seq-head {
    background: #e0f2fe; border: 1.5px solid #0284c7; border-radius: 6px;
    padding: 8px; font-size: 12px; font-weight: 700; text-align: center; color: #0369a1;
  }
  .seq-line {
    border-left: 2px dashed #94a3b8; position: absolute; top: 40px; bottom: 0; left: 50%;
  }
  .seq-act {
    position: absolute; width: 14px; background: #cbd5e1; border: 1px solid #64748b; border-radius: 2px; left: -6px;
  }
</style>
"""

def render_png(name, html_body, width=1600, height=1050):
    output_png = os.path.join(OUT_DIR, f"{name}.png")
    tmp_html = os.path.join(OUT_DIR, f"{name}_tmp.html")
    full_html = f"<!DOCTYPE html><html><head>{COMMON_HEAD}</head><body><div class='canvas'>{html_body}</div></body></html>"
    with open(tmp_html, "w", encoding="utf-8") as f:
        f.write(full_html)
    
    cmd = [
        CHROME,
        "--headless",
        "--disable-gpu",
        f"--screenshot={output_png}",
        f"--window-size={width},{height}",
        "--hide-scrollbars",
        f"file:///{tmp_html.replace(chr(92), '/')}"
    ]
    subprocess.run(cmd, check=True)
    if os.path.exists(tmp_html):
        os.remove(tmp_html)
    print(f"✓ Xuất thành công: {os.path.basename(output_png)} ({os.path.getsize(output_png):,} bytes)")

print("Đang khởi tạo trình sinh ảnh sơ đồ UML bằng Chrome...")
