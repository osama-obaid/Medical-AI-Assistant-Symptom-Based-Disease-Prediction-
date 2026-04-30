# 🧠 Medical AI Assistant (Symptom-Based Disease Prediction)

## 📌 Project Description

This project is a **Medical AI Web Application** that predicts possible diseases based on user symptoms using Machine Learning.

The system analyzes input symptoms and provides a **preliminary diagnosis** along with additional information such as precautions and descriptions.

It is designed as an intelligent assistant to support early medical guidance.

---

## 🚀 Features

* 🤖 Disease prediction using Machine Learning
* 🧾 Input symptoms through a web interface
* 📊 Uses trained AI model (Decision Tree)
* 📁 Dataset-based analysis (Training & Testing data)
* 📋 Displays:

  * Disease name
  * Description
  * Precautions
* 🌐 Simple and clean web interface

---

## 🛠 Technologies Used

### Backend:

* Python

### Web Framework:

* Flask

### Machine Learning:

* Scikit-learn (Decision Tree)

### Frontend:

* HTML
* CSS

### Data:

* CSV datasets

### Model Files:

* Pickle (`.pkl`)

---

## 📁 Project Structure

```
MEDICAL_AI_PROJECT_PYTHON/
│
├── data/
│   ├── Training.csv
│   ├── Testing.csv
│   ├── symptom_Description.csv
│   ├── symptom_precaution.csv
│   ├── Symptom_severity.csv
│
├── models/
│   ├── decision_tree.pkl
│   ├── label_encoder.pkl
│
├── static/
│   └── style.css
│
├── templates/
│   └── index.html
│
├── app.py
├── medical_ai.py
├── data_processor.py
├── requirement.txt
```

---

## ⚙️ Requirements

Before running the project, install:

* Python 3.8 or higher
* pip (Python package manager)

---

## 📦 Installation

1. Clone the repository:

```
git clone https://github.com/your-username/medical-ai-project.git
cd medical-ai-project
```

2. Install dependencies:

```
pip install -r requirement.txt
```

---

## ▶️ How to Run

Run the Flask app:

```
python app.py
```

Then open your browser:

```
http://127.0.0.1:5000
```

---

## 🧠 How It Works

1. User enters symptoms
2. System processes input
3. AI model predicts disease
4. Results are displayed with:

   * Disease description
   * Suggested precautions

---

## 📌 Future Improvements

* Add more advanced AI models (Random Forest / Deep Learning)
* Improve UI/UX design
* Add user authentication system
* Convert to REST API
* Integrate with mobile app (Expo / Flutter)

---

## ⚠️ Disclaimer

This system provides **preliminary predictions only** and should NOT replace professional medical advice.

---

## 👨‍💻 Author

**Osama Abdullah Obaid**
osamahobaid4@gmail.com
IT Engineer | Web & AI Developer

---

## 📄 License

This project is for educational purposes.
