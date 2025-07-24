 // script.js

// 🔍 Preview selected image in upload.html
function previewImage(event) {
    const reader = new FileReader();
    reader.onload = function () {
        const output = document.getElementById('preview');
        output.src = reader.result;
        output.style.display = 'block';
    };
    reader.readAsDataURL(event.target.files[0]);
}

// ✅ Show success alert after form submit
function showSuccess(message) {
    alert(message || "Form submitted successfully!");
}

// 🧾 Dummy validation function
function validateLogin() {
    const email = document.getElementById("email").value;
    const pass = document.getElementById("password").value;
    if (!email || !pass) {
        alert("Please enter email and password!");
        return false;
    }
    return true;
}

function handleRegister(event) {
    event.preventDefault();
    const name = document.getElementById("fullname").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    if (!name || !email || !password) {
        alert("Please fill all fields.");
        return false;
    }

    // Dummy store in localStorage (optional)
    localStorage.setItem("user", JSON.stringify({ name, email, password }));
    alert("Account created successfully!");

    // Redirect to login
    window.location.href = "login.html";
    return false;
}
// In script.js when result is ready
localStorage.setItem("disease", "Eczema");
localStorage.setItem("confidence", "95%");
window.location.href = "result.html";

// In result.html add <script> to fetch & show
window.onload = function() {
    document.querySelector("strong:nth-of-type(1)").innerText = localStorage.getItem("disease");
    document.querySelector("strong:nth-of-type(2)").innerText = localStorage.getItem("confidence");
};
