from flask import Flask, request, send_from_directory
import requests, os, json

app = Flask(__name__, static_folder='static')
DAV = "https://dichvucong.dav.gov.vn/api/services/app/soDangKy/GetAllPublicServerPaging"

@app.route("/")
def index():
    return send_from_directory('static', 'index.html')

@app.route("/search", methods=["POST"])
def search():
    kw = request.json.get("keyword", "").strip()
    if not kw:
        return app.response_class(
            response=json.dumps({"error": "Thieu tu khoa"}, ensure_ascii=False),
            mimetype='application/json'
        ), 400
    try:
        r = requests.post(DAV, json={
            "filterText": kw, "KichHoat": True,
            "SoDangKyThuoc": {}, "maxResultCount": 500,
            "skipCount": 0, "sorting": None
        }, headers={
            "Content-Type": "application/json",
            "Referer": "https://dichvucong.dav.gov.vn/congbothuoc/index",
            "Origin": "https://dichvucong.dav.gov.vn",
            "User-Agent": "Mozilla/5.0"
        }, timeout=15)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        return app.response_class(
            response=json.dumps({"error": str(e)}, ensure_ascii=False),
            mimetype='application/json'
        ), 502

    items = data.get("result", {}).get("items", [])
    total = data.get("result", {}).get("totalCount", 0)

    rows = []
    for item in items:
        tt = item.get("thongTinThuocCoBan") or {}
        rows.append({
            "tenThuoc": item.get("tenThuoc") or "",
            "soGPLH": item.get("soDangKy") or "",
            "hoatChat": tt.get("hoatChatChinh") or item.get("hoatChatChinh") or item.get("hoatChatHamLuong") or "",
            "hamLuong": tt.get("hamLuong") or item.get("hamLuong") or "",
            "dangBaoChe": tt.get("dangBaoChe") or item.get("dangBaoChe") or ""
        })

    result = {"total": total, "rows": rows}
    return app.response_class(
        response=json.dumps(result, ensure_ascii=False),
        mimetype='application/json'
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
