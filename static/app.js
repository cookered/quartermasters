const supa = "https://troop89qm.koyeb.app";
const local = "http://127.0.0.1:5000";
const API = local;
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
function scan(onResult) {
  const html5QrCode = new Html5Qrcode("qr-reader");
  const config = { fps: 10, qrbox: 250 };
  $("#qr-cont").show();
  $("#qr-reader").show();
  $("#overlay").show();
  Html5Qrcode.getCameras().then(cameras => {
    if (cameras && cameras.length) {
      html5QrCode.start(
        cameras[0].id,
        config,
        (decodedText, decodedResult) => {
          console.log(`✅ QR Code detected: ${decodedText}`, decodedResult);
          html5QrCode.stop().then(() => {
            $("#qr-reader").hide();
            $("#qr-cont").hide();
            $("#overlay").hide();
            onResult(decodedText);
          }).catch(err => {
            console.error("Failed to stop scanner:", err);
          });
        },
        (errorMessage) => {
          if (
            typeof errorMessage === "string" &&
            !errorMessage.includes("No MultiFormat Readers")
          ) {
            console.warn("QR Code scan error:", errorMessage);
          }
        }
      );
    } else {
      alert("No cameras found");
    }
  }).catch(err => {
    console.warn("Camera error:", err);
    alert("Failed to scan QR code. Please check your camera permissions or try a different browser.");
  });
}