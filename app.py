from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import os, io, requests
import psycopg2
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

load_dotenv()
app = Flask(__name__)
CORS(app, origins="*")

# 🔐 Config
SERVICE_ACCOUNT_FILE = "credentials.json"
FOLDER_ID = "1I9o0mzb_BbX5kHNm5npao7e96bdj67q-"  # Replace this with your actual Drive folder ID
GOOGLE_CLIENT_ID = str(os.getenv("GOOGLE_CLIENT_ID"))
DATABASE_URL = str(os.getenv("DATABASE_URL"))  # From Supabase -> Settings -> Database -> Connection URI

# ⚙️ DB helper
def run_sql(query, params=None):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            try:
                return cur.fetchall()
            except:
                return []

# 🔄 SQL API endpoint
@app.route("/query", methods=["POST"])
def exec_query():
    body = request.get_json()
    sql = body.get("sql")
    params = body.get("params", [])
    if not sql:
        return jsonify({ "error": "Missing SQL" }), 400
    try:
        result = run_sql(sql, params)
        return jsonify({ "result": result })
    except Exception as e:
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
    uploaded = drive.files().create(
        body=metadata,
        media_body=media,
        fields="id"
    ).execute()

    file_id = uploaded.get("id")

    # 🌍 Make file public
    drive.permissions().create(
        fileId=file_id,
        body={"role": "reader", "type": "anyone"},
    ).execute()

    # 🔁 Try resolving to Googleusercontent URL
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