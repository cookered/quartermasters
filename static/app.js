const supa = "https://troop89qm.koyeb.app";
const local = "http://127.0.0.1:5000/";
const API = local;

// Supabase CRUD utilities
function createRecord(data, onSuccess = () => {}, onError = () => {}) {
  $.ajax({
    url: `${API}/create`,
    method: "POST",
    contentType: "application/json",
    data: JSON.stringify(data),
    success: onSuccess,
    error: onError
  });
}

function readRecords(onSuccess, onError = () => {}) {
  $.get(`${API}/read`, onSuccess).fail(onError);
}

function updateRecord(id, column, value, onSuccess = () => {}, onError = () => {}) {
  $.ajax({
    url: `${API}/update`,
    method: "POST",
    contentType: "application/json",
    data: JSON.stringify({ id, column, value }),
    success: onSuccess,
    error: onError
  });
}

function deleteRecord(id, onSuccess = () => {}, onError = () => {}) {
  $.ajax({
    url: `${API}/delete`,
    method: "POST",
    contentType: "application/json",
    data: JSON.stringify({ id }),
    success: onSuccess,
    error: onError
  });
}

// Upload image via Flask (no Google login required)
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
      console.log("✅ Uploaded:", data);
      onSuccess(data);
    })
    .catch(err => {
      console.error("❌ Upload failed", err);
      alert("Upload failed. Check console.");
      onError(err);
    });
}