# 🔥 Custom Firewall using Python, Django & AI

This project is a custom-built firewall system powered by Python, Django, and machine learning. It monitors network traffic, detects suspicious activities, and uses AI models to classify threats in real-time.

---

## 🚀 Features

- 🔍 **Traffic Monitoring** — Captures and logs incoming/outgoing network packets.
- 🤖 **AI-Powered Detection** — Uses machine learning models to detect malicious patterns.
- 🌐 **Web Interface (Django)** — View logs, statistics, and alerts through a user-friendly dashboard.
- ⚠️ **Threat Classification** — Categorizes traffic (normal, suspicious, malicious).
- 📊 **Analytics** — Visualizes attack types and frequencies.

---

## 🛠 Tech Stack

- **Python 3**
- **Django (Web Framework)**
- **Scikit-learn / TensorFlow** (for ML models)
- **Pandas / NumPy** (data processing)
- **PostgreSQL or SQLite** (database)
- **Bootstrap** (for styling frontend)

---

## 📦 Installation

```bash
# Clone the repository
git clone git@github.com:simwawatim/custom-fire-wall-python-django-ai.git
cd custom-fire-wall-python-django-ai

# (Optional) Create a virtual environment
python3 -m venv env
source env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Run the development server
python manage.py runserver
