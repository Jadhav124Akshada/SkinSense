 // script.js

//  Preview selected image in upload.html
function previewImage(event) {
    const reader = new FileReader();
    reader.onload = function () {
        const output = document.getElementById('preview');
        output.src = reader.result;
        output.style.display = 'block';
    };
    reader.readAsDataURL(event.target.files[0]);
}

//  Show success alert after form submit
function showSuccess(message) {
    alert(message || "Form submitted successfully!");
}


//  Login form validation
function validateLogin(event) {
    event.preventDefault();
    const email = document.getElementById("email").value.trim();
    const pass = document.getElementById("password").value;
    let valid = true;
    let message = "";
    if (!email || !pass) {
        message = "Please enter email and password!";
        valid = false;
    } else if (!/^\S+@\S+\.\S+$/.test(email)) {
        message = "Please enter a valid email address!";
        valid = false;
    }
    if (!valid) {
        alert(message);
        return false;
    }
    // Redirect to dashboard if valid
    window.location.href = 'dashboard.html';
    return false;
}

//  Register form validation
function validateRegister(event) {
    event.preventDefault();
    const fullname = document.getElementById("fullname").value.trim();
    const email = document.getElementById("email").value.trim();
    const pass = document.getElementById("password").value;
    let valid = true;
    let message = "";
    if (!fullname || !email || !pass) {
        message = "Please fill in all fields!";
        valid = false;
    } else if (!/^\S+@\S+\.\S+$/.test(email)) {
        message = "Please enter a valid email address!";
        valid = false;
    } else if (pass.length < 6) {
        message = "Password must be at least 6 characters!";
        valid = false;
    }
    // Check for confirm password field if present
    const confirm = document.getElementById("confirm-password");
    if (confirm) {
        if (pass !== confirm.value) {
            message = "Passwords do not match!";
            valid = false;
        }
    }
    if (!valid) {
        alert(message);
        return false;
    }
    alert("Registration successful!");
    window.location.href = 'login.html';
    return false;
}

