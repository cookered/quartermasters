const supa = "https://troop89qm.koyeb.app";
const local = "http://127.0.0.1:5000";
const API = supa;
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
  const config = {
    fps: 10,
    qrbox: { width: 250, height: 250 },
    aspectRatio: 1.0
  };

  $("#qr-cont").show();
  $("#qr-reader").show();
  $("#overlay").show();

  Html5Qrcode.getCameras().then(cameras => {
    if (!cameras || cameras.length === 0) {
      alert("No cameras found");
      return;
    }

    // Try to select a rear-facing camera on mobile
    let selectedCamera = cameras[0];
    for (const cam of cameras) {
      if (/back|rear|environment/i.test(cam.label)) {
        selectedCamera = cam;
        break;
      }
    }

    html5QrCode.start(
      selectedCamera.id,
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
      errorMessage => {
        if (
          typeof errorMessage === "string" &&
          !errorMessage.includes("No MultiFormat Readers")
        ) {
          console.warn("QR scan error:", errorMessage);
        }
      }
    );
  }).catch(err => {
    console.error("Camera access error:", err);
    alert("Unable to access camera. Please check permissions.");
  });
}
