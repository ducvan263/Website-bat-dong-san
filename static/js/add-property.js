const API = 'https://provinces.open-api.vn/api/v1';

const province = document.getElementById('province');
const district = document.getElementById('district');
const ward = document.getElementById('ward');
const city = document.getElementById('city');

// ================= LOAD PROVINCES =================
fetch(`${API}/p/`)
    .then(res => res.json())
    .then(data => {
        data.forEach(p => {
            province.innerHTML += `<option value="${p.code}">${p.name}</option>`;
        });
    });

// ================= PROVINCE CHANGE =================
province.addEventListener('change', async () => {
    district.innerHTML = '<option value="">-- Chọn quận --</option>';
    ward.innerHTML = '<option value="">-- Chọn phường --</option>';
    detectCity();

    if (!province.value) return;

    const res = await fetch(`${API}/p/${province.value}?depth=2`);
    const data = await res.json();

    if (!data.districts) return;

    data.districts.forEach(d => {
        district.innerHTML += `<option value="${d.code}">${d.name}</option>`;
    });
});

// ================= DISTRICT CHANGE =================
district.addEventListener('change', async () => {
    ward.innerHTML = '<option value="">-- Chọn phường --</option>';

    if (!district.value) return;

    const res = await fetch(`${API}/d/${district.value}?depth=2`);
    const data = await res.json();

    if (!data.wards) return;

    data.wards.forEach(w => {
        ward.innerHTML += `<option value="${w.name}">${w.name}</option>`;
    });
});

// ================= DETECT CITY =================
function detectCity() {
    const text = province.options[province.selectedIndex]?.text || '';

}


function predictPrice() {
    const provinceSelect = document.getElementById("province");
    const districtSelect = document.getElementById("district");
    const wardSelect = document.getElementById("ward");

    const provinceName =
        provinceSelect.options[provinceSelect.selectedIndex]?.text || "";

    const districtName =
        districtSelect.options[districtSelect.selectedIndex]?.text || "";

    const wardName =
        wardSelect.options[wardSelect.selectedIndex]?.text || null;

    const data = {
        "Tỉnh/Thành phố": provinceName,
        "Quận": districtName,
        "Phường": wardName,

        "Loại hình nhà ở": document.getElementById("house_type").value,
        "Giấy tờ pháp lý": document.querySelector('[name="Giấy tờ pháp lý"]').value,

        "Số tầng": Number(document.getElementById("floors").value || 0),
        "Số phòng ngủ": Number(document.getElementById("bedrooms").value || 0),
        "Diện tích": Number(document.getElementById("area").value || 0)
    };

    // TP.HCM có chiều ngang/dài
    if (provinceName.includes("Hồ Chí Minh")) {
        data["Chiều ngang"] = Number(document.getElementById("width").value || 0);
        data["Chiều dài"]  = Number(document.getElementById("length").value || 0);
    }

    console.log("📦 Data gửi AI:", data);

    fetch("/api/predict-price", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(result => {
        document.getElementById("ai_price_m2").value =
            result.price_m2?.toLocaleString("vi-VN");

        document.getElementById("ai_total_price").value =
            result.total_price?.toLocaleString("vi-VN");
        document.getElementById('accept-price-btn').style.display='flex';
    })
    .catch(err => {
        console.error("❌ Lỗi AI:", err);
        alert("Không thể dự đoán giá AI");
    });
}
// ================= QUẢN LÝ HÌNH ẢNH =================
const validTypes = ["image/jpeg", "image/png", "image/webp", "image/gif"];
let detailImages = []; // Mảng lưu trữ các file ảnh chi tiết

// 1. Xử lý Ảnh đại diện (Thumbnail)
document.getElementById("thumbnailInput").addEventListener("change", function() {
    const previewBox = document.getElementById("thumbnailPreview");
    previewBox.innerHTML = ""; // Xóa preview cũ

    if (this.files && this.files[0]) {
        const file = this.files[0];
        if (!validTypes.includes(file.type)) {
            alert("Vui lòng chọn tệp hình ảnh hợp lệ!");
            this.value = "";
            return;
        }
        const reader = new FileReader();
        reader.onload = (e) => {
            previewBox.innerHTML = `
                <div class="preview-item">
                    <img src="${e.target.result}">
                </div>`;
        };
        reader.readAsDataURL(file);
    }
});

// 2. Xử lý Ảnh chi tiết (Cộng dồn)
document.getElementById("imagesInput").addEventListener("change", function() {
    const files = Array.from(this.files);

    files.forEach(file => {
        if (validTypes.includes(file.type)) {
            detailImages.push(file); // Thêm vào mảng tạm
        }
    });

    renderDetailPreviews();
    this.value = ""; // Reset input để có thể chọn lại cùng 1 file
});

function renderDetailPreviews() {
    const previewBox = document.getElementById("imagesPreview");
    previewBox.innerHTML = ""; // Vẽ lại toàn bộ từ mảng detailImages

    detailImages.forEach((file, index) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            const div = document.createElement("div");
            div.className = "preview-item";
            div.innerHTML = `
                <img src="${e.target.result}">
                <button type="button" class="btn-remove" onclick="removeDetailImage(${index})">✕</button>
            `;
            previewBox.appendChild(div);
        };
        reader.readAsDataURL(file);
    });
}
function fillPrice(){
    const housePriceInp = document.getElementById('price-house-inp')
    const totalPriceAI = document.getElementById('ai_total_price')
    housePriceInp.value = totalPriceAI.value
}
// 3. Hàm xóa ảnh chi tiết
function removeDetailImage(index) {
    detailImages.splice(index, 1);
    renderDetailPreviews();
}

function showPostLimitModal() {
    document.getElementById("postLimitModal").style.display = "flex";
    document.body.style.overflow = "hidden";
}

function closePostLimitModal() {
    document.getElementById("postLimitModal").style.display = "none";
    document.body.style.overflow = "auto";
}
// ================= AJAX SUBMIT (Sửa theo form của bạn) =================
// ================= AJAX SUBMIT (Bản sửa lỗi) =================
document.querySelector("form").addEventListener("submit", function (e) {
    e.preventDefault();

    const formData = new FormData(this);

    // 1. Cập nhật City từ dropdown Tỉnh/Thành phố
    const provinceSelect = document.getElementById("province");
    const cityName = provinceSelect.options[provinceSelect.selectedIndex]?.text || "";
    formData.set("city", cityName);

    // 2. Thêm Tỉnh, Quận, Phường vào FormData (Do HTML select thiếu name)
    const districtSelect = document.getElementById("district");
    const wardSelect = document.getElementById("ward");

    formData.set("province", cityName);
    formData.set("district", districtSelect.options[districtSelect.selectedIndex]?.text || "");
    formData.set("ward", wardSelect.options[wardSelect.selectedIndex]?.text || "");

    // 3. Xử lý giá trị AI (Xóa dấu phân cách nghìn trước khi gửi nếu có)
    const aiPriceRaw = document.getElementById("ai_price_m2").value.replace(/[^0-9]/g, '');
    const aiTotalRaw = document.getElementById("ai_total_price").value.replace(/[^0-9]/g, '');
    formData.set("ai_price_m2", aiPriceRaw);
    formData.set("ai_total_price", aiTotalRaw);

    // 4. Nạp mảng ảnh chi tiết (detailImages là mảng tạm bạn đã tạo)
    formData.delete("images[]");
    detailImages.forEach(file => {
        formData.append("images[]", file);
    });

    // --- KIỂM TRA LẠI TRƯỚC KHI FETCH ---
    console.log("--- DỮ LIỆU CUỐI CÙNG ---");
    for (let [key, value] of formData.entries()) {
        if (value instanceof File) {
            console.log(`📁 ${key}: ${value.name}`);
        } else {
            console.log(`📝 ${key}: ${value}`);
        }
    }
    console.log(this.action)
    // 5. Gửi dữ liệu
    fetch(this.action, {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert("✅ Thành công!");
            // Chuyển hướng linh hoạt dựa trên response từ server hoặc vị trí hiện tại
            window.location.href = data.redirect_url || "/";
        } else {
            const ev = data.event
            if(ev === 'create')
                showPostLimitModal();
                const form = document.getElementById("propertyForm");
                if (form) {
                    form.querySelectorAll("input, select, textarea, button")
                        .forEach(el => el.disabled = true);
                }
        }
    })
    .catch(err => {
        console.error("Fetch Error:", err);
    }); console.log(this.action)
});