
import pickle
import numpy as np
import pandas as pd
import csv
import re
from langdetect import detect
from deep_translator import GoogleTranslator

# ================= تحميل الموديل والمحول =================
with open("models/decision_tree.pkl", "rb") as f:
    clf = pickle.load(f)

with open("models/label_encoder.pkl", "rb") as f:
    le = pickle.load(f)

# ================= تحميل الأعمدة =================
training = pd.read_csv("data/Training.csv")
cols = training.columns[:-1]   # pandas Index
col_names = list(cols)
# خريطة لتطابق الأسماء بسهولة (lowercase keys)
col_map = {c.lower(): c for c in col_names}

# ================= تحميل الملفات المساندة =================
severityDictionary = {}
description_list = {}
precautionDictionary = {}

def getDescription():
    with open("data/symptom_Description.csv", encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        for row in csv_reader:
            if len(row) >= 2:
                description_list[row[0]] = row[1]

def getSeverityDict():
    with open("data/symptom_severity.csv", encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        for row in csv_reader:
            try:
                severityDictionary[row[0]] = int(row[1])
            except:
                pass

def getprecautionDict():
    with open("data/symptom_precaution.csv", encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        for row in csv_reader:
            if len(row) >= 5:
                precautionDictionary[row[0]] = [row[1], row[2], row[3], row[4]]

getDescription()
getSeverityDict()
getprecautionDict()

# ================= الجلسات =================
sessions = {}

# ================= الرسائل =================
messages = {
    "greeting": {
        "en": "Hello! 👋 I am your medical assistant. How can I help you today?",
        "ar": "مرحباً 👋 أنا مساعدك الطبي. كيف يمكنني مساعدتك اليوم؟"
    },
    "ask_symptom": {
        "en": "Please tell me your symptoms (comma separated).",
        "ar": "من فضلك اذكر الأعراض التي تشعر بها (مفصولة بفواصل)."
    },
    "ask_days": {
        "en": "Okay. From how many days have you had these symptoms?",
        "ar": "حسناً، منذ كم يوم لديك هذه الأعراض؟"
    },
    "confirm_more": {
        "en": "Do you have any other symptoms to mention? (yes/no)",
        "ar": "هل لديك أعراض أخرى تريد ذكرها؟ (نعم/لا)"
    },
    "invalid_days": {
        "en": "Please enter a valid number for days.",
        "ar": "من فضلك أدخل عدداً صحيحاً يمثل عدد الأيام."
    },
    "not_enough": {
        "en": "You need to provide at least 3 symptoms for a valid diagnosis. Please add more symptoms.",
        "ar": "تحتاج إلى إدخال 3 أعراض على الأقل للتشخيص. من فضلك أضف المزيد من الأعراض."
    },
    "answer_yesno": {
        "en": "Please answer with yes or no.",
        "ar": "من فضلك أجب بنعم أو لا."
    }
}

# ================= كشف اللغة =================
def detect_language(text):
    try:
        lang = detect(text)
        return "ar" if lang == "ar" else "en"
    except:
        return "en"

# ================= ترجمة =================
def translate(text, target_lang="en"):
    try:
        return GoogleTranslator(source="auto", target=target_lang).translate(text)
    except:
        return text

# ================= أدوات مساعدة =================
# تحويل نص إلى رقم (يدعم أرقام رقمية و كلمات إنجليزية وعربية شائعة)
number_words_en = {
    "zero":0, "one":1, "two":2, "three":3, "four":4, "five":5, "six":6, "seven":7, "eight":8, "nine":9,
    "ten":10, "eleven":11, "twelve":12, "thirteen":13, "fourteen":14, "fifteen":15, "sixteen":16,
    "seventeen":17, "eighteen":18, "nineteen":19, "twenty":20, "thirty":30, "forty":40, "fifty":50
}
number_words_ar = {
    "صفر":0, "واحد":1, "اثنين":2, "اثنان":2, "ثلاثة":3,"   ثلاثة ايام":3,"ثلاثة":3, "أربعة":4, "خمسة":5, "ستة":6, "سبعة":7, "ثمانية":8,
    "تسعة":9, "عشرة":10, "أحد عشر":11, "اثنا عشر":12, "ثلاثة عشر":13, "أربعة عشر":14, "خمسة عشر":15
}

def parse_int_from_text(text):
    if not text:
        return None
    t = text.strip()
    # حاول التحويل المباشر (يدعم أرقام عربي-هندية Unicode مثل '٣')
    try:
        return int(t)
    except:
        pass
    # ابحث عن أرقام داخل النص
    m = re.search(r'[-+]?\d+', t)
    if m:
        try:
            return int(m.group())
        except:
            pass
    # حاول مطابقة كلمات انجليزية/عربية
    tlower = t.lower()
    # لو النص عربي، جرب تحويله إلى إنجليزي ثم تحقق
    try:
        translated_to_en = translate(t, "en").lower()
    except:
        translated_to_en = tlower
    if translated_to_en in number_words_en:
        return number_words_en[translated_to_en]
    if tlower in number_words_ar:
        return number_words_ar[tlower]
    # تحقق إنجليزي مباشر (لو المستخدم كتب "three")
    if tlower in number_words_en:
        return number_words_en[tlower]
    return None

# تعرف إن كانت الإجابة نعم/لا (نأخذ بعين الاعتبار الترجمة والرسالة الأصلية)
affirmatives_en = {"yes","y","yeah","yep","sure","ok","okay"}
negatives_en = {"no","n","nope","nah"}
affirmatives_ar = {"نعم","ايه","ايوه","نعمِ","نعما"}
negatives_ar = {"لا","لاأ","لأ","لاا"}

def is_affirmative(orig, translated_en):
    te = (translated_en or "").strip().lower()
    og = (orig or "").strip().lower()
    if te.split()[0] in affirmatives_en if te else False:
        return True
    if any(a in og for a in affirmatives_ar):
        return True
    return False

def is_negative(orig, translated_en):
    te = (translated_en or "").strip().lower()
    og = (orig or "").strip().lower()
    if te.split()[0] in negatives_en if te else False:
        return True
    if any(n in og for n in negatives_ar):
        return True
    return False

# تطبيع اسم العرض لمحاولة مطابقته مع أسماء أعمدة الـ CSV
def normalize_symptom_candidate(text):
    if not text:
        return ""
    s = text.lower().strip()
    # أزل أي رموز غير أحرف/أرقام/مسافة
    s = re.sub(r'[^a-z0-9\u0600-\u06FF\s]', '', s)  # يسمح بالحروف العربية والإنجليزية والأرقام
    # استبدال المسافات بشرطة سفلية
    s = re.sub(r'\s+', '_', s.strip())
    return s

# ================= المحادثة الرئيسية =================
def ask_questions(user_id, message):
    orig_msg = (message or "").strip()
    if not orig_msg:
        # رسالة فارغة
        # اختر اللغة الافتراضية (إنجليزية) أو الجلسة إذا موجودة
        lang = sessions.get(user_id, {}).get("lang", "en")
        return messages["ask_symptom"][lang]

    detected = detect_language(orig_msg)
    # إذا الجلسة موجودة نثبت لغة الجلسة (لا تتغير أثناء الجلسة)
    if user_id in sessions:
        user_lang = sessions[user_id].get("lang", detected)
    else:
        user_lang = detected

    # ترجمة للإنجليزي للمعالجة الداخلية (تفصل أعراض، تفهم نعم/لا، الخ)
    translated_en = translate(orig_msg, "en").lower()

    # كشف التحيات (نستخدم النص الأصلي والنص المترجم)
    greetings_keywords = ["hi", "hello", "hey", "السلام عليكم", "مرحبا", "هلا"]
    low_orig = orig_msg.lower()
    if any(g in low_orig for g in greetings_keywords) or any(g in translated_en for g in greetings_keywords):
        # لو الجلسة غير موجودة ننشئها بلغة المستخدم المكتشفة
        if user_id not in sessions:
            sessions[user_id] = {"symptoms": [], "days": None, "state": "ask_symptom", "lang": user_lang}
        return messages["greeting"][user_lang]

    # إنشاء جلسة جديدة لو لم تكن موجودة
    if user_id not in sessions:
        sessions[user_id] = {"symptoms": [], "days": None, "state": "ask_symptom", "lang": user_lang}
        return messages["ask_symptom"][user_lang]

    session = sessions[user_id]
    state = session.get("state", "ask_symptom")

    # ===== المرحلة 1: استقبال الأعراض =====
    if state == "ask_symptom":
        # نقسم على الفاصلة الإنجليزية و/أو الفاصلة العربية
        parts = [p.strip() for p in re.split(r'[,\u060C]', translated_en) if p.strip()]
        if not parts:
            return messages["ask_symptom"][user_lang]

        added = []
        for p in parts:
            cand = normalize_symptom_candidate(p)  # ex: "headache" -> "headache", "back pain"->"back_pain"
            # حاول إيجاد التطابق في خريطة الأعمدة
            if cand in col_map:
                col_name = col_map[cand]
                if col_name not in session["symptoms"]:
                    session["symptoms"].append(col_name)
                    added.append(col_name)
            else:
                # لو لم يجد تطابق، خزن الشكل المطوَّع (قد يتم تجاهله لاحقاً إن لم يكن في الأعمدة)
                if cand and cand not in session["symptoms"]:
                    session["symptoms"].append(cand)
                    added.append(cand)

        if len(session["symptoms"]) < 3:
            # نطلب المزيد من الأعراض
            return messages["ask_symptom"][user_lang]

        session["state"] = "ask_days"
        return messages["ask_days"][user_lang]

    # ===== المرحلة 2: استقبال عدد الأيام =====
    elif state == "ask_days":
        days = parse_int_from_text(orig_msg)
        if days is None:
            # حاول أيضاً من النص المترجم
            days = parse_int_from_text(translated_en)
        if days is None:
            return messages["invalid_days"][user_lang]
        session["days"] = days
        session["state"] = "confirm_more"
        return messages["confirm_more"][user_lang]

    # ===== المرحلة 3: إضافة أعراض أخرى أو التشخيص =====
    elif state == "confirm_more":
        if is_affirmative(orig_msg, translated_en):
            session["state"] = "ask_symptom"
            return messages["ask_symptom"][user_lang]
        elif is_negative(orig_msg, translated_en):
            if len(session["symptoms"]) < 3:
                return messages["not_enough"][user_lang]
            else:
                result = diagnose(session["symptoms"], session["days"], session["lang"])
                sessions.pop(user_id, None)
                return format_result(result, session["lang"])
        else:
            return messages["answer_yesno"][user_lang]

# ================= التشخيص =================
def diagnose(symptoms, days, user_lang):
    input_vector = np.zeros(len(cols))
    for symptom in symptoms:
        # symptom قد يكون اسم عمود صحيح أو مرادف (normalized)
        # نجرّب عدة طرق للمطابقة:
        # 1) مباشرة اسم العمود (case-sensitive)
        if symptom in cols:
            input_vector[cols.get_loc(symptom)] = 1
            continue
        # 2) lower -> خريطة col_map
        key = str(symptom).lower()
        if key in col_map:
            col_name = col_map[key]
            input_vector[cols.get_loc(col_name)] = 1
            continue
        # 3) استبدال underscore بمسافة ومحاولة (في حال الأعمدة مسماة بطريقة مختلفة)
        maybe_space = key.replace('_', ' ')
        if maybe_space in col_map:
            col_name = col_map[maybe_space]
            input_vector[cols.get_loc(col_name)] = 1
            continue
        # إذا لم يوجد تطابق نتجاهله (لا نوقف العملية)
        # يمكن لاحقاً إضافة خوارزمية fuzzy match إن رغبت

    predicted = clf.predict([input_vector])
    disease = le.inverse_transform(predicted)[0]

    # وصف واحتياطات
    desc = description_list.get(disease, "No description available.")
    precautions = precautionDictionary.get(disease, ["No precautions available."])

    # إذا كانت لغة المستخدم عربية، نترجم النتائج للعربية
    if user_lang == "ar":
        try:
            desc = translate(desc, "ar")
            precautions = [translate(p, "ar") for p in precautions]
            disease_translated = translate(disease, "ar")
        except:
            disease_translated = disease
    else:
        disease_translated = disease

    severity_score = sum([severityDictionary.get(s, 0) for s in symptoms])
    if (severity_score * (days or 1)) / (len(symptoms) + 1) > 13:
        advice = {"en": "⚠️ You should consult a doctor.", "ar": "⚠️ يجب أن تستشير طبيباً."}
    else:
        advice = {"en": "ℹ️ It might not be severe, but take precautions.", "ar": "ℹ️ قد لا يكون الأمر خطيراً، لكن عليك أخذ الاحتياطات."}

    return {
        "disease": disease,
        "disease_translated": disease_translated,
        "description": desc,
        "precautions": precautions,
        "advice": advice
    }

# ================= تنسيق النتيجة =================
def format_result(result, user_lang="en"):
    if user_lang == "ar":
        response = f" بناءً على الأعراض التي ذكرتها، قد تكون مصاب بـ **{result['disease_translated']}**.\n\n"
        response += f"الوصف: {result['description']}\n\n"
        response += f"{result['advice']['ar']}\n\n"
        response += "الاحتياطات:\n"
        for i, p in enumerate(result['precautions'], 1):
            response += f"{i}. {p}\n"
    else:
        response = f"🔎 Based on your symptoms, you may have **{result['disease']}**.\n\n"
        response += f"Description: {result['description']}\n\n"
        response += f"{result['advice']['en']}\n\n"
        response += "Precautions:\n"
        for i, p in enumerate(result['precautions'], 1):
            response += f"{i}. {p}\n"
    return response
