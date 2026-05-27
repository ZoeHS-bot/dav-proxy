from flask import Flask, request, send_from_directory
from collections import defaultdict
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

    if not items:
        return app.response_class(
            response=json.dumps({"hoatChat": kw, "tongSoDangKy": 0, "nhom": []}, ensure_ascii=False),
            mimetype='application/json'
        )

    groups = defaultdict(lambda: defaultdict(list))
    hoat_chat = kw
    for item in items:
        ten_hoat_chat = item.get("hoatChatHamLuong") or ""
        if ten_hoat_chat:
            hoat_chat = ten_hoat_chat.strip()
        dbc = (item.get("dangBaoChe") or "Khong xac dinh").strip()
        hl = (item.get("hamLuong") or item.get("hoatChatChinh") or "Khong xac dinh").strip()
        sdk = (item.get("soDangKy") or "").strip()
        groups[dbc][hl].append(sdk)

    nhom = []
    for dbc in sorted(groups):
        hl_list = []
        for hl, sdks in sorted(groups[dbc].items()):
            hl_list.append({"hamLuong": hl, "soSDK": len(sdks), "sdk": sdks[:3]})
        nhom.append({"daBaoChe": dbc, "hamLuongs": hl_list})

    result = {"hoatChat": hoat_chat, "tongSoDangKy": total, "nhom": nhom}
    return app.response_class(
        response=json.dumps(result, ensure_ascii=False),
        mimetype='application/json'
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
