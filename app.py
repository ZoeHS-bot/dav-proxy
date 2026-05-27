from flask import Flask, request, jsonify, send_from_directory
import requests, os

app = Flask(__name__, static_folder='static')
DAV = "https://dichvucong.dav.gov.vn/api/services/app/soDangKy/GetAllPublicServerPaging"

@app.route("/")
def index():
    return send_from_directory('static', 'index.html')

@app.route("/search", methods=["POST"])
def search():
    kw = request.json.get("keyword", "").strip()
    if not kw:
        return jsonify({"error": "Thiếu từ khóa"}), 400
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
        return jsonify({"error": str(e)}), 502

    items = data.get("result", {}).get("items", [])
    total = data.get("result", {}).get("totalCount", 0)
    if not items:
        return jsonify({"hoatChat": kw, "tongSoDangKy": 0, "nhom": []})

    from collections import defaultdict
    groups = defaultdict(lambda: defaultdict(list))
    hoat_chat = kw
    for item in items:
        if item.get("hoatChat"): hoat_chat = item["hoatChat"].strip()
        dbc = (item.get("daBaoChe") or "Không xác định").strip()
        hl  = (item.get("hamLuong") or "Không xác định").strip()
        sdk = (item.get("soDangKy") or "").strip()
        groups[dbc][hl].append(sdk)

    nhom = []
    for dbc in sorted(groups):
        hl_list = [{"hamLuong": hl, "soSDK": len(sdks), "sdk": sdks[:3]}
                   for hl, sdks in sorted(groups[dbc].items())]
        nhom.append({"daBaoChe": dbc, "hamLuongs": hl_list})

    return jsonify({"hoatChat": hoat_chat, "tongSoDangKy": total, "nhom": nhom})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
