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
function validateForm() {
    const name=document.getElementById("fullname").value.trim();
    const email = document.getElementById("email").value.trim();
    const pass = document.getElementById("password").value;
    const result=document.getElementById("error");

    const nameregax=/^[A-Za-z\s]{2,}$/;

    if(!nameregax.test(name) || name==" "){
       alert("Enter valid fullname");
       return false;
    }
    const emailregax=/[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailregax.test(email) || email==" ") {
        alert("Please enter correct email format");
        return false;
    }
    
    const passregax=/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$/;
    if(passregax.test(pass)){
        result.innerText="Strong password";
        result.style.color="green";
    }
    else{
        result.innerText="Password must be at least 8 characters,include uppercase,lowercase,number,and special character";
        result.style.color="red";
        return false;
    }
    
        window.location.href = 'dashboard.html';
    
        return false;
}



