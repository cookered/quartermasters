from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from supabase import create_client
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import requests, os, io

load_dotenv()
app = Flask(__name__)
CORS(app, origins="*")

# 🔐 Config
SUPABASE_URL = str(os.getenv("SUPABASE_URL"))
SUPABASE_KEY = str(os.getenv("SUPABASE_KEY"))
GOOGLE_CLIENT_ID = str(os.getenv("GOOGLE_CLIENT_ID"))
SERVICE_ACCOUNT_FILE = "credentials.json"
FOLDER_ID = "1I9o0mzb_BbX5kHNm5npao7e96bdj67q-"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
TABLE = "things"

# 🧠 Supabase logic
def create_thing(record):
    clean = {k: v for k, v in record.items() if v not in [None, "", "null"]}
    return supabase.table(TABLE).insert([clean]).execute().data

def read_things():
    return supabase.table(TABLE).select("*").execute().data

def update_thing(id, column, value):
    return supabase.table(TABLE).update({column: value}).eq("id", id).execute().data

def delete_thing(id):
    return supabase.table(TABLE).delete().eq("id", id).execute().data

# 🔗 Google Drive uploader
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

    service = create_drive_service()

    media = MediaIoBaseUpload(io.BytesIO(file.read()), mimetype=file.mimetype)
    metadata = { "name": file.filename, "parents": [FOLDER_ID] }

    uploaded = service.files().create(
        body=metadata,
        media_body=media,
        fields="id, name"
    ).execute()

    file_id = uploaded.get("id")

    # 👁️ Make public
    service.permissions().create(
        fileId=file_id,
        body={"role": "reader", "type": "anyone"},
    ).execute()

    # 🔄 Attempt to resolve final Googleusercontent URL
    redirect_url = f"https://drive.google.com/uc?export=view&id={file_id}"
    try:
        resp = requests.get(redirect_url, allow_redirects=True, timeout=10)
        content_url = resp.url if resp.ok else redirect_url
    except Exception as e:
        print("Redirect resolution failed:", e)
        content_url = redirect_url

    return jsonify({
        "file_id": file_id,
        "url": content_url
    })
# 🧩 Supabase API Routes
@app.route("/")
def index():
    return render_template("index.html", GOOGLE_CLIENT_ID=GOOGLE_CLIENT_ID)

@app.route("/create", methods=["POST"])
def api_create():
    return jsonify(create_thing(request.json))

@app.route("/read", methods=["GET"])
def api_read():
    return jsonify(read_things())

@app.route("/update", methods=["POST"])
def api_update():
    d = request.json
    return jsonify(update_thing(d["id"], d["column"], d["value"]))

@app.route("/delete", methods=["POST"])
def api_delete():
    return jsonify(delete_thing(request.json["id"]))

if __name__ == "__main__":
    app.run(debug=True)