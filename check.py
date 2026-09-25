#!/usr/bin/env python3
import json, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
targets = json.loads((ROOT / "targets.json").read_text())["targets"]
results = []
for t in targets:
    started = time.time()
    ok = False
    code = None
    err = None
    try:
        req = urllib.request.Request(t["url"], method="GET", headers={"User-Agent": "net-status-ir"})
        with urllib.request.urlopen(req, timeout=15) as r:
            code = r.status
            ok = 200 <= r.status < 400
    except Exception as e:
        err = str(e)
    results.append({
        "id": t["id"],
        "name": t["name"],
        "url": t["url"],
        "ok": ok,
        "status": code,
        "ms": int((time.time() - started) * 1000),
        "error": err,
    })

payload = {
    "checked_at": datetime.now(timezone.utc).isoformat(),
    "probe": "github-actions",
    "results": results,
}
(ROOT / "status.json").write_text(json.dumps(payload, indent=2))
rows = "".join(
    f"<tr><td>{r['name']}</td><td>{'ok' if r['ok'] else 'fail'}</td><td>{r['status']}</td><td>{r['ms']}ms</td></tr>"
    for r in results
)
html = f"""<!doctype html><html lang=fa dir=rtl><meta charset=utf-8>
<title>net-status-ir</title>
<body>
<h1>وضعیت سرویس‌های عمومی</h1>
<p>آخرین بررسی: {payload['checked_at']}</p>
<table border=1 cellpadding=6><tr><th>سرویس</th><th>وضعیت</th><th>HTTP</th><th>زمان</th></tr>{rows}</table>
<p>این پروب از رانر گیتهاب است، نه از داخل ایران.</p>
</body></html>
"""
(ROOT / "index.html").write_text(html)
print("wrote status.json and index.html")
