# SkinSense – AI-Based Skin Disease Detection System

SkinSense is an intelligent web-based platform that leverages AI to detect skin diseases from uploaded images. It provides treatment tips, doctor appointment booking, chat assistance, and downloadable reports—all in a modern, user-friendly interface.

---

## ✅ What We've Completed

### ✅ Frontend UI Pages
- `index.html` – Welcome landing page (responsive and animated)
- `login.html` – Login page for users/doctors
- `register.html` – Registration form
- `upload.html` – Page to upload skin image (UI only)
- `result.html` – Placeholder for prediction result
- `appointment.html` – Appointment booking UI (form-style)
- `dashboard.html` – Initial structure for user/doctor dashboard

### ✅ Project Structure Organized
```
frontend/
├── css/                        # Main stylesheet
│ └── style.css
├── images/                     # Logos for branding
│ └── logo.jpg
├── js/                         # Placeholder for JS logic
│ └── script.js
├── pages/                      # Internal HTML pages
│ ├── appointment.html
│ ├── dashboard.html
│ ├── login.html
│ ├── register.html
│ ├── result.html
│ └── upload.html
├── index.html # Main entry page
└── README.md # Project overview
```

### ✅ UI/UX Features
- Gradient animated background
- Responsive on desktop and mobile
- Google Fonts, Bootstrap 5, and Animate.css integrated
- Logo branding and hover effects
- Smooth transitions and polished layout

---

## 🧱 To-Do (Remaining Features)

### 🧑‍⚕️ User-Side Functionality
- [ ] Form validation in login/register pages
- [ ] Upload image and preview on `upload.html`
- [ ] Connect to AI backend for prediction results
- [ ] Display AI result with confidence score in `result.html`
- [ ] Treatment and product suggestions based on diagnosis
- [ ] Mood tracking + symptom checklist (e.g., itchy, red, painful)
- [ ] Chatbot popup integration (OpenAI / Dialogflow)
- [ ] Appointment calendar with validation
- [ ] PDF report download (styled result)
- [ ] Past history access on dashboard

### 👨‍⚕️ Doctor-Side Functionality
- [ ] Login/Register with role detection
- [ ] Doctor dashboard with case viewer
- [ ] Medical advice update panel
- [ ] Stats display (total cases, regions, conditions)

---

## ⚙️ Tech Stack Overview
| Part           | Tech Used                   | Purpose                                    |
|----------------|------------------------------|---------------------------------------------|
| Frontend       | HTML, CSS, JS, Bootstrap    | Responsive design and layout               |
| AI Model       | TensorFlow / Keras (CNN)    | Predict skin conditions from photos        |
| Backend        | Python (Flask or Django)    | Image processing, model serving            |
| Chatbot        | OpenAI / Dialogflow         | Patient interaction                        |
| Database       | MySQL / MongoDB             | User info, reports, doctor records         |
| PDF Reports    | ReportLab / xhtml2pdf       | Download diagnosis reports                 |
| Maps           | Google Maps API             | Show nearby clinics                        |
| Hosting        | Render / Vercel / Heroku    | Deploy live site                           |

---

## 🚀 How to Run
1. Download or clone the `frontend/` folder
2. Open `index.html` in your browser
3. Ensure logo is placed inside `/images` folder
4. All pages are static and currently not linked to backend

---

## 🔥 Highlights
- Combines AI + Chatbot + Doctor Booking
- Modern responsive UI (mobile + desktop)
- Future support for multilingual interface

---

Built with ❤️ for healthcare innovation.

> Let’s build the backend next and connect the pages!
