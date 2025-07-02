const supa = "https://troop89qm.koyeb.app";
const local = "http://127.0.0.1:5000";
const API = local;

// Run any SQL statement via your Flask backend
function runSQL(sql, params = [], onSuccess = () => {}, onError = () => {}) {
  fetch(`${API}/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sql, params })
  })
    .then(res => res.json())
    .then(data => {
      if (data.error) throw new Error(data.error);
      onSuccess(data.result);
    })
    .catch(err => {
      console.error("❌ SQL Error:", err);
      onError(err);
    });
}

// Upload image via Google Drive → returns URL
function uploadImage(inp, onSuccess = () => {}, onError = () => {}) {
  const fileInput = document.getElementById(inp);
  const file = fileInput?.files?.[0];
  if (!file) return alert("Please select a file");

  const form = new FormData();
  form.append("file", file);

  fetch(`${API}/upload-image`, {
    method: "POST",
    body: form
  })
    .then(res => res.json())
    .then(data => {
      if (data.error) throw new Error(data.error);
      console.log("✅ Uploaded:", data);
      onSuccess(data);
    })
    .catch(err => {
      console.error("❌ Upload failed", err);
      alert("Upload failed. Check console.");
      onError(err);
    });
}

// 🔐 Handle Google Sign-In callback
function onGoogleLogin(response) {
  const credential = response.credential;
  console.log("🔑 Google Credential:", credential);

  // Send token to backend or decode for user info:
  const payload = JSON.parse(atob(credential.split(".")[1]));
  console.log("👤 User Info:", payload);
}