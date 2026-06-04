from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import sqlite3, re, base64

try:
    import pytesseract
    from PIL import Image
    import numpy as np
    from io import BytesIO
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

app = Flask(__name__, static_folder="static")
CORS(app)
DB = "eventsec.db"

VALID_CODES = {
    "A7K9X2P": {"name": "Attendee", "tier": "Regular", "seat": "G-001"},
    "Q4M8Z1L": {"name": "Attendee", "tier": "Regular", "seat": "G-002"},
    "T9B3V6R": {"name": "Attendee", "tier": "Regular", "seat": "G-003"},
    "X2N7C5W": {"name": "Attendee", "tier": "Regular", "seat": "G-004"},
    "H8J4K9D": {"name": "Attendee", "tier": "Regular", "seat": "G-005"},
    "P6L3F2Q": {"name": "Attendee", "tier": "Regular", "seat": "G-006"},
    "Z1X7V8M": {"name": "Attendee", "tier": "Regular", "seat": "G-007"},
    "R5T2B9N": {"name": "Attendee", "tier": "Regular", "seat": "G-008"},
    "U3C8Y6A": {"name": "Attendee", "tier": "Regular", "seat": "G-009"},
    "D7E4P1K": {"name": "Attendee", "tier": "Regular", "seat": "G-010"},
    "M9Q2H5S": {"name": "Attendee", "tier": "Regular", "seat": "G-011"},
    "K6W3T8X": {"name": "Attendee", "tier": "Regular", "seat": "G-012"},
    "J4Z9L2C": {"name": "Attendee", "tier": "Regular", "seat": "G-013"},
    "V8P7R1F": {"name": "Attendee", "tier": "Regular", "seat": "G-014"},
    "S2D6N9Y": {"name": "Attendee", "tier": "Regular", "seat": "G-015"},
    "Y5A3K7M": {"name": "Attendee", "tier": "Regular", "seat": "G-016"},
    "B9H4U1Q": {"name": "Attendee", "tier": "Regular", "seat": "G-017"},
    "L2X8C6T": {"name": "Attendee", "tier": "Regular", "seat": "G-018"},
    "F3R7P9Z": {"name": "Attendee", "tier": "Regular", "seat": "G-019"},
    "C8M1D5J": {"name": "Attendee", "tier": "Regular", "seat": "G-020"},
    "N4K6Q2H": {"name": "Attendee", "tier": "VIP", "seat": "VIP-001"},
    "W7T3A8Y": {"name": "Attendee", "tier": "VIP", "seat": "VIP-002"},
    "E1P9V4R": {"name": "Attendee", "tier": "VIP", "seat": "VIP-003"},
    "G6S2L7X": {"name": "Attendee", "tier": "VIP", "seat": "VIP-004"},
    "O5Y8J3M": {"name": "Attendee", "tier": "VIP", "seat": "VIP-005"},
    "I9D4C7K": {"name": "Attendee", "tier": "VIP", "seat": "VIP-006"},
    "U2B6T1Z": {"name": "Attendee", "tier": "VIP", "seat": "VIP-007"},
    "Q7F3N8P": {"name": "Attendee", "tier": "VIP", "seat": "VIP-008"},
    "Z4H9X2L": {"name": "Attendee", "tier": "VIP", "seat": "VIP-009"},
    "A6R1V5C": {"name": "Attendee", "tier": "VIP", "seat": "VIP-010"},
    "M8T2W7D": {"name": "Attendee", "tier": "Ultimate Table", "seat": "ULT-001"},
    "P3K9Y6H": {"name": "Attendee", "tier": "Ultimate Table", "seat": "ULT-002"},
    "T5Z4Q1B": {"name": "Attendee", "tier": "Ultimate Table", "seat": "ULT-003"},
    "X9L7F2R": {"name": "Attendee", "tier": "Ultimate Table", "seat": "ULT-004"},
    "H3C8N6A": {"name": "Attendee", "tier": "Ultimate Table", "seat": "ULT-005"},
    "D1J5P7M": {"name": "Attendee", "tier": "Hall of Fame", "seat": "HOF-001"},
    "S9B2K4T": {"name": "Attendee", "tier": "Hall of Fame", "seat": "HOF-002"},
    "Y6R8L3Q": {"name": "Attendee", "tier": "Hall of Fame", "seat": "HOF-003"},
    "B5U7X1F": {"name": "Attendee", "tier": "Regular", "seat": "G-021"},
    "L8C9H4N": {"name": "Attendee", "tier": "Regular", "seat": "G-022"},
    "F2M6D3Z": {"name": "Attendee", "tier": "Regular", "seat": "G-023"},
    "C7A1P8K": {"name": "Attendee", "tier": "Regular", "seat": "G-024"},
    "N9Q5J2T": {"name": "Attendee", "tier": "Regular", "seat": "G-025"},
    "W4Y3R6H": {"name": "Attendee", "tier": "Regular", "seat": "G-026"},
    "E8X2L7S": {"name": "Attendee", "tier": "Regular", "seat": "G-027"},
    "G1T9V4P": {"name": "Attendee", "tier": "Regular", "seat": "G-028"},
    "O6D3B8M": {"name": "Attendee", "tier": "Regular", "seat": "G-029"},
    "I7K2Q5Z": {"name": "Attendee", "tier": "Regular", "seat": "G-030"},
    "U4N1C9A": {"name": "Attendee", "tier": "Regular", "seat": "G-031"},
    "Q8F6R2X": {"name": "Attendee", "tier": "Regular", "seat": "G-032"},
    "Z3H5T7L": {"name": "Attendee", "tier": "Regular", "seat": "G-033"},
    "A9J4M1P": {"name": "Attendee", "tier": "Regular", "seat": "G-034"},
    "M2W7D6K": {"name": "Attendee", "tier": "Regular", "seat": "G-035"},
    "P5Y8H3C": {"name": "Attendee", "tier": "Regular", "seat": "G-036"},
    "T1B9Q4F": {"name": "Attendee", "tier": "Regular", "seat": "G-037"},
    "X6L2R7N": {"name": "Attendee", "tier": "Regular", "seat": "G-038"},
    "H4C3A8Z": {"name": "Attendee", "tier": "Regular", "seat": "G-039"},
    "D9P7M5T": {"name": "Attendee", "tier": "Regular", "seat": "G-040"},
    "S6K2F1Y": {"name": "Attendee", "tier": "Regular", "seat": "G-041"},
    "Y8R4Q3J": {"name": "Attendee", "tier": "Regular", "seat": "G-042"},
    "B1U9X6L": {"name": "Attendee", "tier": "Regular", "seat": "G-043"},
    "L3C5H7P": {"name": "Attendee", "tier": "Regular", "seat": "G-044"},
    "F9M2D8K": {"name": "Attendee", "tier": "Regular", "seat": "G-045"},
    "C6A4P1T": {"name": "Attendee", "tier": "Regular", "seat": "G-046"},
    "N7Q3J5R": {"name": "Attendee", "tier": "Regular", "seat": "G-047"},
    "W2Y8H6X": {"name": "Attendee", "tier": "Regular", "seat": "G-048"},
    "E5X1L9S": {"name": "Attendee", "tier": "Regular", "seat": "G-049"},
    "G9T4P7B": {"name": "Attendee", "tier": "Regular", "seat": "G-050"},
    "O3D6M2K": {"name": "Attendee", "tier": "Regular", "seat": "G-051"},
    "I8K7Z5A": {"name": "Attendee", "tier": "Regular", "seat": "G-052"},
    "U1N4C9F": {"name": "Attendee", "tier": "Regular", "seat": "G-053"},
    "Q6F8R2T": {"name": "Attendee", "tier": "Regular", "seat": "G-054"},
    "Z9H3L1P": {"name": "Attendee", "tier": "Regular", "seat": "G-055"},
    "A4J7M5D": {"name": "Attendee", "tier": "Regular", "seat": "G-056"},
    "M6W2K9X": {"name": "Attendee", "tier": "Regular", "seat": "G-057"},
    "P8Y3C7R": {"name": "Attendee", "tier": "Regular", "seat": "G-058"},
    "T2B5F1L": {"name": "Attendee", "tier": "Regular", "seat": "G-059"},
    "X7L4N6H": {"name": "Attendee", "tier": "Regular", "seat": "G-060"},
    "H9C1A3Z": {"name": "Attendee", "tier": "Regular", "seat": "G-061"},
    "D5P8T7M": {"name": "Attendee", "tier": "Regular", "seat": "G-062"},
    "S4K6Y2Q": {"name": "Attendee", "tier": "Regular", "seat": "G-063"},
    "Y1R9J3F": {"name": "Attendee", "tier": "Regular", "seat": "G-064"},
    "B7U5L2X": {"name": "Attendee", "tier": "Regular", "seat": "G-065"},
    "L6C8H9P": {"name": "Attendee", "tier": "Regular", "seat": "G-066"},
    "F1M3D4K": {"name": "Attendee", "tier": "Regular", "seat": "G-067"},
    "C9A7P2T": {"name": "Attendee", "tier": "Regular", "seat": "G-068"},
    "N5Q8J6R": {"name": "Attendee", "tier": "Regular", "seat": "G-069"},
    "W3Y2H4X": {"name": "Attendee", "tier": "Regular", "seat": "G-070"},
    "E7X6L1S": {"name": "Attendee", "tier": "Regular", "seat": "G-071"},
    "G2T5P9B": {"name": "Attendee", "tier": "Regular", "seat": "G-072"},
    "O8D4M3K": {"name": "Attendee", "tier": "Regular", "seat": "G-073"},
    "I6K9Z7A": {"name": "Attendee", "tier": "Regular", "seat": "G-074"},
    "U3N1C2F": {"name": "Attendee", "tier": "Regular", "seat": "G-075"},
    "Q9F7R4T": {"name": "Attendee", "tier": "Regular", "seat": "G-076"},
    "Z2H6L5P": {"name": "Attendee", "tier": "Regular", "seat": "G-077"},
    "A8J3M7D": {"name": "Attendee", "tier": "Regular", "seat": "G-078"},
    "M1W9K4X": {"name": "Attendee", "tier": "Regular", "seat": "G-079"},
    "P7Y2C5R": {"name": "Attendee", "tier": "Regular", "seat": "G-080"},
    "T6B8F3L": {"name": "Attendee", "tier": "Regular", "seat": "G-081"},
    "X4L1N9H": {"name": "Attendee", "tier": "Regular", "seat": "G-082"},
    "H2C7A5Z": {"name": "Attendee", "tier": "Regular", "seat": "G-083"},
    "D8P6T3M": {"name": "Attendee", "tier": "Regular", "seat": "G-084"},
    "S1K4Y9Q": {"name": "Attendee", "tier": "Regular", "seat": "G-085"},
    "Y7R2J8F": {"name": "Attendee", "tier": "Regular", "seat": "G-086"},
    "B3U6L5X": {"name": "Attendee", "tier": "Regular", "seat": "G-087"},
    "L9C1H4P": {"name": "Attendee", "tier": "Regular", "seat": "G-088"},
    "F4M7D2K": {"name": "Attendee", "tier": "Regular", "seat": "G-089"},
    "C5A8P3T": {"name": "Attendee", "tier": "Regular", "seat": "G-090"},
    "N2Q6J9R": {"name": "Attendee", "tier": "Regular", "seat": "G-091"},
    "W8Y1H7X": {"name": "Attendee", "tier": "Regular", "seat": "G-092"},
    "E4X3L5S": {"name": "Attendee", "tier": "Regular", "seat": "G-093"},
    "G7T2P6B": {"name": "Attendee", "tier": "Regular", "seat": "G-094"},
    "O1D9M4K": {"name": "Attendee", "tier": "Regular", "seat": "G-095"},
    "I5K3Z8A": {"name": "Attendee", "tier": "Regular", "seat": "G-096"},
    "U9N6C7F": {"name": "Attendee", "tier": "Regular", "seat": "G-097"},
    "Q3F1R8T": {"name": "Attendee", "tier": "Regular", "seat": "G-098"},
    "Z5H4L2P": {"name": "Attendee", "tier": "Regular", "seat": "G-099"},
    "A7J6M9D": {"name": "Attendee", "tier": "Regular", "seat": "G-100"},
    "M3W8K1X": {"name": "Attendee", "tier": "Regular", "seat": "G-101"},
    "P2Y4C6R": {"name": "Attendee", "tier": "Regular", "seat": "G-102"},
    "T9B7F5L": {"name": "Attendee", "tier": "Regular", "seat": "G-103"},
    "X1L6N3H": {"name": "Attendee", "tier": "Regular", "seat": "G-104"},
    "H5C2A4Z": {"name": "Attendee", "tier": "Regular", "seat": "G-105"},
    "D3P9T1M": {"name": "Attendee", "tier": "Regular", "seat": "G-106"},
    "S8K7Y6Q": {"name": "Attendee", "tier": "Regular", "seat": "G-107"},
    "Y2R5J4F": {"name": "Attendee", "tier": "Regular", "seat": "G-108"},
    "B6U1L9X": {"name": "Attendee", "tier": "Regular", "seat": "G-109"},
    "L5C7H2P": {"name": "Attendee", "tier": "Regular", "seat": "G-110"},
    "F8M4D6K": {"name": "Attendee", "tier": "Regular", "seat": "G-111"},
    "C1A3P9T": {"name": "Attendee", "tier": "Regular", "seat": "G-112"},
    "N8Q2J7R": {"name": "Attendee", "tier": "Regular", "seat": "G-113"},
    "W6Y5H1X": {"name": "Attendee", "tier": "Regular", "seat": "G-114"},
    "E9X7L4S": {"name": "Attendee", "tier": "Regular", "seat": "G-115"},
    "G3T8P2B": {"name": "Attendee", "tier": "Regular", "seat": "G-116"},
    "O4D1M7K": {"name": "Attendee", "tier": "Regular", "seat": "G-117"},
    "I2K5Z6A": {"name": "Attendee", "tier": "Regular", "seat": "G-118"},
    "U7N8C3F": {"name": "Attendee", "tier": "Regular", "seat": "G-119"},
    "Q5F9R6T": {"name": "Attendee", "tier": "Regular", "seat": "G-120"},
    "Z1H7L3P": {"name": "Attendee", "tier": "Regular", "seat": "G-121"},
    "A6J2M8D": {"name": "Attendee", "tier": "Regular", "seat": "G-122"},
    "M9W5K3X": {"name": "Attendee", "tier": "Regular", "seat": "G-123"},
    "P4Y7C1R": {"name": "Attendee", "tier": "Regular", "seat": "G-124"},
    "T8B2F6L": {"name": "Attendee", "tier": "Regular", "seat": "G-125"},
    "X3L9N5H": {"name": "Attendee", "tier": "Regular", "seat": "G-126"},
    "H7C4A1Z": {"name": "Attendee", "tier": "Regular", "seat": "G-127"},
    "D2P5T8M": {"name": "Attendee", "tier": "Regular", "seat": "G-128"},
    "S3K1Y7Q": {"name": "Attendee", "tier": "Regular", "seat": "G-129"},
    "Y9R6J2F": {"name": "Attendee", "tier": "Regular", "seat": "G-130"},
    "B8U4L7X": {"name": "Attendee", "tier": "Regular", "seat": "G-131"},
    "L1C9H3P": {"name": "Attendee", "tier": "Regular", "seat": "G-132"},
    "F7M5D8K": {"name": "Attendee", "tier": "Regular", "seat": "G-133"},
    "C2A6P4T": {"name": "Attendee", "tier": "Regular", "seat": "G-134"},
    "N3Q1J8R": {"name": "Attendee", "tier": "Regular", "seat": "G-135"},
    "W9Y7H2X": {"name": "Attendee", "tier": "Regular", "seat": "G-136"},
    "E6X8L3S": {"name": "Attendee", "tier": "Regular", "seat": "G-137"},
    "G4T1P5B": {"name": "Attendee", "tier": "Regular", "seat": "G-138"},
    "O2D7M9K": {"name": "Attendee", "tier": "Regular", "seat": "G-139"},
    "I1K8Z4A": {"name": "Attendee", "tier": "Regular", "seat": "G-140"},
    "U5N3C6F": {"name": "Attendee", "tier": "Regular", "seat": "G-141"},
    "Q2F4R7T": {"name": "Attendee", "tier": "Regular", "seat": "G-142"},
    "Z7H9L8P": {"name": "Attendee", "tier": "Regular", "seat": "G-143"},
    "A3J1M2D": {"name": "Attendee", "tier": "Regular", "seat": "G-144"},
    "M5W6K7X": {"name": "Attendee", "tier": "Regular", "seat": "G-145"},
    "P9Y8C2R": {"name": "Attendee", "tier": "Regular", "seat": "G-146"},
    "T7B4F9L": {"name": "Attendee", "tier": "Regular", "seat": "G-147"},
    "X8L5N1H": {"name": "Attendee", "tier": "Regular", "seat": "G-148"},
    "H1C6A9Z": {"name": "Attendee", "tier": "Regular", "seat": "G-149"},
    "D4P3T2M": {"name": "Attendee", "tier": "Regular", "seat": "G-150"},
    "S7K8Y5Q": {"name": "Attendee", "tier": "Regular", "seat": "G-151"},
    "Y4R1J9F": {"name": "Attendee", "tier": "Regular", "seat": "G-152"},
    "B2U3L8X": {"name": "Attendee", "tier": "Regular", "seat": "G-153"},
}

def init_db():
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL,
        event_type TEXT NOT NULL,
        checkpoint TEXT,
        timestamp TEXT,
        is_valid INTEGER DEFAULT 1
    )""")
    con.commit()
    con.close()

def get_last_scan(code):
    con = sqlite3.connect(DB)
    row = con.execute("SELECT event_type FROM scans WHERE code=? AND is_valid=1 ORDER BY id DESC LIMIT 1", (code,)).fetchone()
    con.close()
    return row[0] if row else None

def get_history(code):
    con = sqlite3.connect(DB)
    rows = con.execute("SELECT event_type, checkpoint, timestamp FROM scans WHERE code=? AND is_valid=1 ORDER BY id", (code,)).fetchall()
    con.close()
    return [{"event_type": r[0], "checkpoint": r[1], "time": r[2]} for r in rows]

def log_scan(code, event_type, checkpoint, timestamp, is_valid=True):
    con = sqlite3.connect(DB)
    con.execute("INSERT INTO scans (code, event_type, checkpoint, timestamp, is_valid) VALUES (?,?,?,?,?)",
        (code, event_type, checkpoint, timestamp, int(is_valid)))
    con.commit()
    con.close()

def process_code(code, checkpoint, now):
    if not code:
        return jsonify({"status": "ERROR", "message": "Empty code"}), 400
    if code not in VALID_CODES:
        log_scan(code, "FAKE", checkpoint, now, is_valid=False)
        return jsonify({"status": "FAKE", "code": code})
    last = get_last_scan(code)
    direction = "IN" if (not last or last == "OUT") else "OUT"
    log_scan(code, direction, checkpoint, now, is_valid=True)
    history = get_history(code)
    return jsonify({
        "status": "VALID", "direction": direction, "code": code,
        "meta": VALID_CODES[code],
        "entries": sum(1 for h in history if h["event_type"] == "IN"),
        "exits": sum(1 for h in history if h["event_type"] == "OUT"),
        "history": history,
    })

def extract_code_from_image(image_data_b64):
    if not OCR_AVAILABLE:
        return None, "OCR not installed"
    try:
        image_bytes = base64.b64decode(image_data_b64)
        image = Image.open(BytesIO(image_bytes)).convert("L")
        w, h = image.size
        image = image.resize((w * 2, h * 2), Image.LANCZOS)
        text = pytesseract.image_to_string(image, config='--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
        text = re.sub(r'[^A-Z0-9]', ' ', text.upper())
        candidates = re.findall(r'[A-Z0-9]{7}', text)
        for c in candidates:
            if c in VALID_CODES:
                return c, None
        return (candidates[0] if candidates else None), None
    except Exception as e:
        return None, str(e)

@app.route("/verify", methods=["POST"])
def verify():
    data = request.json or {}
    return process_code(data.get("code", "").strip().upper(), data.get("checkpoint", "Main Entrance"), datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

@app.route("/scan-image", methods=["POST"])
def scan_image():
    data = request.json or {}
    image_data = data.get("image", "")
    checkpoint = data.get("checkpoint", "Main Entrance")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not image_data:
        return jsonify({"status": "ERROR", "message": "No image"}), 400
    if "," in image_data:
        image_data = image_data.split(",")[1]
    code, err = extract_code_from_image(image_data)
    if not code:
        return jsonify({"status": "UNREADABLE", "message": err or "Could not read code. Try better lighting."})
    return process_code(code, checkpoint, now)

@app.route("/dashboard")
def dashboard():
    con = sqlite3.connect(DB)
    rows = con.execute("SELECT code, event_type, checkpoint, timestamp FROM scans WHERE is_valid=1 ORDER BY id").fetchall()
    fakes = con.execute("SELECT code, COUNT(*) FROM scans WHERE is_valid=0 GROUP BY code").fetchall()
    con.close()
    states = {}
    for code, event_type, checkpoint, timestamp in rows:
        if code not in states:
            states[code] = {"code": code, "meta": VALID_CODES.get(code, {}), "events": []}
        states[code]["events"].append({"type": event_type, "checkpoint": checkpoint, "time": timestamp})
    return jsonify({
        "tickets": list(states.values()),
        "fakes": [{"code": f[0], "attempts": f[1]} for f in fakes],
        "total_inside": sum(1 for s in states.values() if s["events"] and s["events"][-1]["type"] == "IN"),
    })

@app.route("/logs")
def activity_logs():
    con = sqlite3.connect(DB)
    rows = con.execute("SELECT code, event_type, checkpoint, timestamp, is_valid FROM scans ORDER BY id DESC LIMIT 200").fetchall()
    con.close()
    return jsonify([{"code": r[0], "type": r[1], "checkpoint": r[2], "time": r[3], "valid": bool(r[4]), "meta": VALID_CODES.get(r[0], {})} for r in rows])

@app.route("/stats")
def stats():
    con = sqlite3.connect(DB)
    total_scans = con.execute("SELECT COUNT(*) FROM scans WHERE is_valid=1").fetchone()[0]
    total_fakes = con.execute("SELECT COUNT(*) FROM scans WHERE is_valid=0").fetchone()[0]
    con.close()
    inside = sum(1 for code in VALID_CODES if get_last_scan(code) == "IN")
    return jsonify({"total_codes": len(VALID_CODES), "total_scans": total_scans, "total_fakes": total_fakes, "inside_now": inside})

@app.route("/reset", methods=["POST"])
def reset():
    con = sqlite3.connect(DB)
    con.execute("DELETE FROM scans")
    con.commit()
    con.close()
    return jsonify({"status": "ok"})

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    return send_from_directory("static", "index.html")

if __name__ == "__main__":
    init_db()
    print("\n==========================================")
    print("  UPSTAGING SEC - Ticket Verification")
    print("==========================================")
    print(f"  Codes loaded : {len(VALID_CODES)}")
    print(f"  OCR ready    : {OCR_AVAILABLE}")
    print("\n  Open on computer : http://localhost:5000")
    print("  Open on phone    : http://YOUR-IP:5000")
    print("==========================================\n")
    app.run(host="0.0.0.0", port=5000, debug=False)