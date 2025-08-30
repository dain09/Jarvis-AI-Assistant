# utils.py
# ==============================================================================
# J.A.R.V.I.S. Project - I/O Utilities
# هذا الملف يحتوي على كل الأدوات الخاصة بالإدخال (الميكروفون) والإخراج (الصوت والنص).
# ==============================================================================

import speech_recognition as sr
import arabic_reshaper
from bidi.algorithm import get_display
import os
from playsound import playsound
from langdetect import detect, LangDetectException
from gtts import gTTS
import config

# ==============================================================================
# القسم الأول: الدوال الأساسية للإخراج (يجب تعريفها أولاً)
# ==============================================================================

def print_to_console(text, prompt=""):
    """
    تطبع النص العربي بشكل صحيح في الطرفية.
    """
    full_text = f"{prompt} {text}" if prompt else text
    reshaped_text = arabic_reshaper.reshape(full_text)
    bidi_text = get_display(reshaped_text)
    print(bidi_text)

# --- متغيرات عامة ---
JARVIS_PROMPT = f"🤖 {config.JARVIS_NAME}:"
app_instance = None # سيحمل نسخة من الواجهة الرسومية
microphone = None
recognizer = None

# ==============================================================================
# القسم الثاني: إعداد الميكروفون (لمرة واحدة)
# ==============================================================================
try:
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    
    print_to_console("🎤 الرجاء الصمت لمدة ثانية لمعايرة حساسية الميكروفون...", "SYSTEM:")
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        recognizer.energy_threshold = max(300, recognizer.energy_threshold)
    print_to_console("✅ تمت المعايرة بنجاح! جارفيس جاهز للاستماع.", "SYSTEM:")
except sr.RequestError as e:
    print_to_console(f"❌ خطأ في الاتصال بخدمات جوجل: {e}", "SYSTEM:")
except Exception as e:
    print_to_console(f"❌ خطأ فادح: لم يتم العثور على ميكروفون أو هناك مشكلة في إعداده. {e}", "SYSTEM:")
    microphone = None

# ==============================================================================
# القسم الثالث: دوال الإخراج المتقدمة (Output)
# ==============================================================================

def update_gui(status="", jarvis_response="", user_input=""):
    """
    دالة مركزية لتحديث الواجهة الرسومية.
    """
    if app_instance:
        if status:
            app_instance.update_status_label(status)
        if jarvis_response:
            app_instance.add_to_conversation_log(jarvis_response, "jarvis")
        if user_input:
            app_instance.add_to_conversation_log(user_input, "user")

def speak(text):
    """
    تحول النص إلى كلام مسموع (gTTS) وتحدث الواجهة.
    """
    if not text: return

    print_to_console(text, JARVIS_PROMPT)
    update_gui(jarvis_response=text)
    
    try:
        lang_code = 'ar' if len(text.strip()) < 10 else detect(text)
        if lang_code not in ['ar', 'en']: lang_code = 'en'
    except LangDetectException:
        lang_code = 'ar'

    update_gui(status="يتحدث الآن...")
    try:
        tts = gTTS(text=text, lang=lang_code, slow=False)
        tts.save(config.TEMP_VOICE_FILE)
        playsound(config.TEMP_VOICE_FILE)
        os.remove(config.TEMP_VOICE_FILE)
    except Exception as e:
        error_msg = f"❌ حدث خطأ في النطق باستخدام gTTS: {e}"
        print_to_console(error_msg, "SYSTEM:")
        update_gui(status="خطأ في النطق")

# ==============================================================================
# القسم الرابع: دالة الإدخال (Input)
# ==============================================================================

def takeCommand():
    """
    تستمع لصوت المستخدم بسرعة، تحوله إلى نص، وتحدث الواجهة.
    """
    if not microphone:
        print_to_console("🎤 لا يوجد ميكروفون، لا يمكن استقبال الأوامر الصوتية.", "SYSTEM:")
        return "stop"

    print_to_console(f"🎤 {config.JARVIS_NAME} يستمع الآن...")
    update_gui(status="يستمع الآن...")
    with microphone as source:
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            update_gui(status="جاري تحليل الصوت...")
            query = recognizer.recognize_google(audio, language='ar-EG')
            
            print_to_console(query, "🗣️ أنت:")
            update_gui(user_input=query, status="تم التعرف على الصوت بنجاح")
            return query.lower()

        except sr.WaitTimeoutError:
            update_gui(status="في انتظار الأوامر...")
            return ""
        except sr.UnknownValueError:
            update_gui(status="لم أتمكن من فهم الصوت")
            return ""
        except sr.RequestError:
            speak("عذراً سيدي، خدمات جوجل للتعرف على الصوت مش شغالة حالياً.")
            update_gui(status="خطأ في خدمة جوجل")
            return "stop"
        except Exception as e:
            print_to_console(f"❌ حدث خطأ غير متوقع أثناء الاستماع: {e}", "SYSTEM:")
            update_gui(status="خطأ في الاستماع")
            return ""