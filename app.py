from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import dotenv_values
import os, io, requests, re
import pg8000.dbapi
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# 🔐 Load .env values manually and override OS environment
config = dotenv_values(".env")
os.environ["DATABASE_URL"] = config.get("DATABASE_URL", "")
app = Flask(__name__)
CORS(app, origins="*")

# 📁 Config values
SERVICE_ACCOUNT_FILE = "credentials.json"
FOLDER_ID = "1I9o0mzb_BbX5kHNm5npao7e96bdj67q-"
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
DATABASE_URL = os.getenv("DATABASE_URL")

# 🔍 Parse DATABASE_URL for pg8000.dbapi
def parse_db_url(url):
    match = re.match(r"postgresql://(.*?):(.*?)@(.*?):(\d+)/(.*)", url)
    if not match:
        raise ValueError("Invalid DATABASE_URL format")
    return {
        "user": match.group(1),
        "password": match.group(2),
        "host": match.group(3),
        "port": int(match.group(4)),
        "database": match.group(5)
    }

# ⚙️ Run SQL with safe parameter binding
def run_sql(query, params=None):
    cfg = parse_db_url(DATABASE_URL)
    conn = pg8000.dbapi.connect(**cfg)
    cursor = conn.cursor()
    cursor.execute(query, params or [])
    try:
        result = cursor.fetchall()
    except pg8000.dbapi.ProgrammingError:
        result = []
    conn.commit()
    cursor.close()
    conn.close()
    return result

# 🔁 Raw SQL route
@app.route("/raw-sql", methods=["POST"])
def raw_sql():
    body = request.get_json()
    query = body.get("sql")
    params = body.get("params", [])
    if not query:
        return jsonify({ "error": "Missing SQL query" }), 400
    try:
        print("🧠 SQL:", query)
        print("📦 Params:", params)
        result = run_sql(query, params)
        return jsonify({ "result": result })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({ "error": str(e) }), 500

# 📁 Google Drive upload
def create_drive_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    return build("drive", "v3", credentials=creds)

@app.route("/upload-image", methods=["POST"])
def upload_image():
    file = request.files.get("file")
    if not file:
        return jsonify({ "error": "No file received" }), 400

    drive = create_drive_service()
    media = MediaIoBaseUpload(io.BytesIO(file.read()), mimetype=file.mimetype)
    metadata = { "name": file.filename, "parents": [FOLDER_ID] }
    uploaded = drive.files().create(body=metadata, media_body=media, fields="id").execute()

    file_id = uploaded.get("id")
    drive.permissions().create(fileId=file_id, body={"role": "reader", "type": "anyone"}).execute()
    redirect_url = f"https://drive.google.com/uc?export=view&id={file_id}"
    try:
        r = requests.get(redirect_url, allow_redirects=True, timeout=10)
        final_url = r.url if r.ok else redirect_url
    except:
        final_url = redirect_url

    return jsonify({ "file_id": file_id, "url": final_url })

@app.route("/")
def index():
    return render_template("index.html", GOOGLE_CLIENT_ID=GOOGLE_CLIENT_ID)

if __name__ == "__main__":
    app.run(debug=True)