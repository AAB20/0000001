import google.generativeai as genai
import wikipedia
import csv
import os
from datetime import datetime

# ---------------------------------------------------------
# ضع مفتاح Gemini API هنا
# ---------------------------------------------------------
genai.configure(api_key="AIzaSyAaLeEulxYgS25yNDMHHImkNMCNk_iUiUA")

# ---------------------------------------------------------
# المواضيع المدعومة
# ---------------------------------------------------------
topics_en = [
    "Iraqi Turkmens", "Syrian Turkmen", "Turkmeneli", "Kirkuk",
    "Altun Kupri massacre", "1959 Kirkuk massacre", "Gokturks",
    "Seljuk Empire", "Ottoman Empire", "Oghuz Turks", "Azerbaijan"
]

topics_tr = [
    "Irak Türkmenleri", "Suriye Türkmenleri", "Türkmeneli", "Kerkük",
    "Altınköprü Katliamı", "1959 Kerkük Katliamı", "Göktürkler",
    "Büyük Selçuklu İmparatorluğu", "Osmanlı İmparatorluğu", "Oğuzlar",
    "Azerbaycan"
]

topics_ar = [
    "التركمان العراقيون", "التركمان السوريون", "تركمان إيلي", "كركوك",
    "مجزرة آلتون كوبري", "مجزرة كركوك 1959", "الغوك تورك",
    "الدولة السلجوقية", "الإمبراطورية العثمانية", "أتراك الأوغوز",
    "أذربيجان"
]

# ---------------------------------------------------------
# CSV file
# ---------------------------------------------------------
csv_file = "chat_history.csv"
if not os.path.exists(csv_file):
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Datetime", "Question", "Answer", "Source"])

# ---------------------------------------------------------
# 1. تحديد اللغة
# ---------------------------------------------------------
def detect_language(text):
    if any(ch in text for ch in "ابتثجحخدذرزسشصضطظعغفقكلمنهوي"):
        return "ar"
    if any(ch in text for ch in "çğıöşüÇĞİÖŞÜ"):
        return "tr"
    return "en"

# ---------------------------------------------------------
# 2. تلخيص ويكيبيديا (موجز متوسط)
# ---------------------------------------------------------
def summarize_wiki(text, max_sentences=5):
    sentences = text.split(".")
    summary = ". ".join(sentences[:max_sentences]).strip()
    if not summary.endswith("."):
        summary += "."
    return summary

# ---------------------------------------------------------
# 3. إجابة ويكيبيديا
# ---------------------------------------------------------
def wiki_answer(query, lang):
    wikipedia.set_lang(lang)
    try:
        full = wikipedia.page(query).summary
        return summarize_wiki(full, max_sentences=5)
    except:
        return None

# ---------------------------------------------------------
# 4. هل الموضوع ضمن القائمة؟
# ---------------------------------------------------------
def is_topic_allowed(question, lang):
    if lang == "ar":
        return any(topic in question for topic in topics_ar)
    if lang == "tr":
        return any(topic in question for topic in topics_tr)
    return any(topic in question for topic in topics_en)

# ---------------------------------------------------------
# 5. إجابة Gemini
# ---------------------------------------------------------
def gemini_answer(question):
    question = question.strip()
    if not question:
        return "لا يمكن إرسال سؤال فارغ إلى Gemini!"
    model = genai.GenerativeModel("gemini-2.0-flash")
    return model.generate_content(question).text

# ---------------------------------------------------------
# 6. حفظ في CSV
# ---------------------------------------------------------
def save_to_csv(question, answer, source):
    dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(csv_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([dt, question, answer, source])

# ---------------------------------------------------------
# 7. الشات بوت
# ---------------------------------------------------------
def chatbot(question):
    question = question.strip()
    if not question:
        return "الرجاء كتابة سؤال صحيح!"
    
    lang = detect_language(question)

    # ويكيبيديا أولاً
    if is_topic_allowed(question, lang):
        ans = wiki_answer(question, lang)
        if ans:
            save_to_csv(question, ans, "Wikipedia")
            return ans

    # Gemini لغير المواضيع
    ans = gemini_answer(question)
    save_to_csv(question, ans, "Gemini")
    return ans

# ---------------------------------------------------------
# 8. التشغيل في CMD
# ---------------------------------------------------------
if __name__ == "__main__":
    print("Chatbot يعمل عبر CMD — يدعم العربية والتركية والإنجليزية.")
    print("يتم حفظ كل الأسئلة في chat_history.csv")
    
    while True:
        q = input("\nسؤالك: ").strip()
        if q.lower() in ["exit", "خروج", "çıkış"]:
            print("تم الإغلاق.")
            break
        print("\nالجواب:\n" + chatbot(q))
