const supa = "https://troop89qm.koyeb.app";
const local = "http://127.0.0.1:5000";
const API = supa;
// 🧠 Run raw SQL via Flask (pg8000-powered)
function execute(sql, params = []) {
  return fetch(`${API}/raw-sql`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sql, params })
  })
    .then(res => res.json())
    .then(data => {
      if (data.error) throw new Error(data.error);
      console.log("✅ SQL result:", data.result);
      return data.result;
    })
    .catch(err => {
      console.error("❌ SQL error:", err);
      return null;
    });
}

// 📁 Upload image via Flask → Google Drive
function uploadImage(inputId, onSuccess = () => {}, onError = () => {}) {
  const fileInput = document.getElementById(inputId);
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
      console.log("✅ Image uploaded:", data);
      onSuccess(data);
    })
    .catch(err => {
      console.error("❌ Upload error:", err);
      alert("Upload failed. See console.");
      onError(err);
    });
}