from flask import Flask, render_template, request, jsonify
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

# Thư mục lưu ảnh kết quả
RESULTS_FOLDER = os.path.join('static', 'results')
if not os.path.exists(RESULTS_FOLDER):
    os.makedirs(RESULTS_FOLDER)

# Cấu hình tỷ lệ thắng
settings = {
    "lo_ratio": 3.6,  # Lô ăn 3.6 lần
    "de_ratio": 70,   # Đề ăn 70 lần
    "currency": "VNĐ" # Đơn vị tiền tệ
}

@app.route('/')
def index():
    return render_template('index.html', settings=settings)

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    bets = data.get('bets', {})
    results = data.get('results', {})

    total_bet_lo = sum(bets.get('lo', {}).values())
    total_bet_de = sum(bets.get('de', {}).values())
    total_bet_xien = sum(bets.get('xien', {}).values())
    total_bet_bacang = sum(bets.get('bacang', {}).values())

    total_win_lo = sum(amount for num, amount in bets.get('lo', {}).items() if num in results.get('lo', []))
    total_win_de = sum(amount for num, amount in bets.get('de', {}).items() if num in results.get('de', []))
    total_win_xien = sum(amount for num, amount in bets.get('xien', {}).items() if all(n in results.get('lo', []) for n in num.split('-')))
    total_win_bacang = sum(amount for num, amount in bets.get('bacang', {}).items() if num in results.get('bacang', []))

    response = {
        'total_bet_lo': total_bet_lo,
        'total_win_lo': total_win_lo,
        'total_bet_de': total_bet_de,
        'total_win_de': total_win_de,
        'total_bet_xien': total_bet_xien,
        'total_win_xien': total_win_xien,
        'total_bet_bacang': total_bet_bacang,
        'total_win_bacang': total_win_bacang,
    }
    return jsonify(response)

@app.route('/generate_image', methods=['POST'])
def generate_image():
    data = request.json
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.axis('off')

    text = (
        f"Tổng điểm Lô đã ghi: {data['total_bet_lo']} - Trúng: {data['total_win_lo']}
"
        f"Tổng tiền Đề đã ghi: {data['total_bet_de']}k - Trúng: {data['total_win_de']}k
"
        f"Tổng điểm Xiên đã ghi: {data['total_bet_xien']} - Trúng: {data['total_win_xien']}
"
        f"Tổng điểm Ba Càng đã ghi: {data['total_bet_bacang']} - Trúng: {data['total_win_bacang']}"
    )
    ax.text(0.5, 0.5, text, ha='center', va='center', fontsize=12, wrap=True)

    image_path = os.path.join(RESULTS_FOLDER, 'result.png')
    plt.savefig(image_path, bbox_inches='tight')
    plt.close()

    return jsonify({'image_url': '/' + image_path})

@app.route('/update_settings', methods=['POST'])
def update_settings():
    data = request.json
    settings["lo_ratio"] = float(data.get("lo_ratio", settings["lo_ratio"]))
    settings["de_ratio"] = float(data.get("de_ratio", settings["de_ratio"]))
    settings["currency"] = data.get("currency", settings["currency"])
    return jsonify({"success": True, "settings": settings})

if __name__ == '__main__':
    app.run(debug=True)
