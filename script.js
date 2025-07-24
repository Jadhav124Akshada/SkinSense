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

// --- Auth & Navbar Logic ---
const NAV_LINKS = [
  { href: 'index.html', label: 'Home', icon: '🏠', auth: 'any' },
  { href: 'dashboard.html', label: 'Dashboard', icon: '📊', auth: 'auth' },
  { href: 'upload.html', label: 'Upload', icon: '⬆️', auth: 'auth' },
  { href: 'result.html', label: 'Results', icon: '📄', auth: 'auth' },
  { href: 'appointment.html', label: 'Appointments', icon: '📅', auth: 'auth' },
  { href: 'login.html', label: 'Login', icon: '🔑', auth: 'guest' },
  { href: 'register.html', label: 'Register', icon: '📝', auth: 'guest' }
];

function isLoggedIn() {
  return !!localStorage.getItem('ss_user');
}

function getUser() {
  return JSON.parse(localStorage.getItem('ss_user') || 'null');
}

function setUser(user) {
  localStorage.setItem('ss_user', JSON.stringify(user));
}

function logout() {
  localStorage.removeItem('ss_user');
  window.location.href = 'index.html';
}

function renderNavbar() {
  const nav = document.querySelector('.navbar-glass .navbar-links');
  if (!nav) return;
  nav.innerHTML = '';
  const loggedIn = isLoggedIn();
  NAV_LINKS.forEach(link => {
    if (
      link.auth === 'any' ||
      (link.auth === 'auth' && loggedIn) ||
      (link.auth === 'guest' && !loggedIn)
    ) {
      const a = document.createElement('a');
      a.className = 'navbar-link' + (window.location.pathname.endsWith(link.href) ? ' active' : '');
      a.href = link.href;
      a.innerHTML = `<span class="nav-icon">${link.icon}</span> ${link.label}`;
      nav.appendChild(a);
    }
  });
  if (loggedIn) {
    // Avatar dropdown
    const user = getUser();
    const dropdown = document.createElement('div');
    dropdown.className = 'navbar-dropdown';
    dropdown.innerHTML = `
      <img src="https://api.dicebear.com/7.x/identicon/svg?seed=${encodeURIComponent(user.email)}" class="navbar-avatar" alt="avatar">
      <div class="navbar-dropdown-content">
        <span class="navbar-dropdown-link" style="font-weight:700;">${user.name || user.email}</span>
        <a href="dashboard.html" class="navbar-dropdown-link">Dashboard</a>
        <a href="appointment.html" class="navbar-dropdown-link">Appointments</a>
        <a href="#" class="navbar-dropdown-link" onclick="logout()">Logout</a>
      </div>
    `;
    nav.appendChild(dropdown);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  renderNavbar();
  // Protect pages
  const protectedPages = ['dashboard.html','upload.html','result.html','appointment.html'];
  if (protectedPages.some(p => window.location.pathname.endsWith(p)) && !isLoggedIn()) {
    window.location.href = 'login.html';
  }
  // Hide login/register if already logged in
  if ((window.location.pathname.endsWith('login.html') || window.location.pathname.endsWith('register.html')) && isLoggedIn()) {
    window.location.href = 'dashboard.html';
  }
  // Password show/hide
  document.querySelectorAll('input[type="password"]').forEach(input => {
    const wrapper = input.parentElement;
    if (wrapper && !wrapper.querySelector('.show-pass')) {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'show-pass btn btn-sm btn-outline-secondary';
      btn.style.marginLeft = '0.5em';
      btn.innerText = 'Show';
      btn.onclick = (e) => {
        e.preventDefault();
        input.type = input.type === 'password' ? 'text' : 'password';
        btn.innerText = input.type === 'password' ? 'Show' : 'Hide';
      };
      wrapper.appendChild(btn);
    }
  });
});

