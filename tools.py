# tools.py
# ==============================================================================
# J.A.R.V.I.S. Project - The Toolbox (v3 - No Direct Speaking)
# ⭐ تحديث جذري: هذا الملف الآن لا يتحدث مباشرة. مهمته فقط تنفيذ الأدوات وإعادة النتائج النصية.
# ==============================================================================

import datetime
import webbrowser
import wikipedia
import os
import requests
import pyautogui
import pytesseract
import pywhatkit as kit
import pytz
import random

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import google.generativeai as genai

import config
# ⭐ تم إزالة استدعاء 'speak'. سنستدعي فقط الدوال التي لا تتحدث.
from utils import print_to_console, update_gui

# ... (باقي الكود التمهيدي كما هو) ...
try:
    pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_CMD_PATH
except FileNotFoundError:
    print_to_console("⚠️ تحذير: Tesseract مش موجود. قراءة الشاشة مش هتشتغل.", "SYSTEM:")
def is_internet_available():
    try:
        requests.get("https://www.google.com", timeout=3)
        return True
    except requests.ConnectionError:
        return False

# ==============================================================================
#  صندوق الأدوات (بدون نطق مباشر)
# ==============================================================================

def get_current_time():
    now = datetime.datetime.now()
    return f"الساعة دلوقتي {now.strftime('%I:%M %p').replace('AM', 'صباحاً').replace('PM', 'مساءً')} ⏰"

def get_weather(city_name: str = config.DEFAULT_CITY):
    # ... (الكود يبقى كما هو) ...
    update_gui(status=f"جاري البحث عن طقس {city_name}...")
    if not is_internet_available():
        return "النت فاصل يا صاحبي، مش هعرف أجيب الطقس 🔌"
    url = f"http://api.weatherapi.com/v1/current.json?key={config.WEATHER_API_KEY}&q={city_name}&lang=ar"
    try:
        data = requests.get(url).json()
        if "error" in data:
            return f"معرفتش ألاقي مدينة اسمها {city_name} على الخريطة 🗺️"
        city = data["location"]["name"]
        temp = int(data["current"]["temp_c"])
        desc = data["current"]["condition"]["text"]
        return f"الجو في {city} عامل {temp}° درجة، والحالة {desc} 🌤️"
    except requests.RequestException:
        return "خدمة الطقس معلقة حالياً، حاول كمان شوية 📡"
        
def get_google_calendar_events():
    # ... (الكود يبقى كما هو) ...
    update_gui(status="جاري فحص أجندة جوجل...")
    if not is_internet_available():
        return "مش عارف أوصل للتقويم من غير نت 😟"
    creds, token_path, credentials_path = None, "token.json", "credentials.json"
    if not os.path.exists(credentials_path):
        return "ملف credentials.json الخاص بجوجل غير موجود."
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, config.SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try: creds.refresh(Request())
            except Exception: creds = None
        if not creds:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, config.SCOPES)
                creds = flow.run_local_server(port=0)
            except Exception as e:
                print_to_console(f"❌ خطأ في إنشاء صلاحيات جوجل: {e}")
                return "حدث خطأ أثناء الحصول على صلاحيات الوصول لأجندة جوجل."
        with open(token_path, "w") as token:
            token.write(creds.to_json())
    try:
        service = build("calendar", "v3", credentials=creds)
        now_utc = datetime.datetime.utcnow().isoformat() + "Z"
        events_result = service.events().list(calendarId="primary", timeMin=now_utc, maxResults=5, singleEvents=True, orderBy="startTime").execute()
        events = events_result.get("items", [])
        if not events: return random.choice(config.QUIRKY_NO_EVENTS_REPLIES)
        event_list = ["أجندتك بتقول الآتي يا ريس 🗓️:"]
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            start_time = datetime.datetime.fromisoformat(start.replace("Z", "+00:00"))
            local_time = start_time.astimezone(pytz.timezone("Africa/Cairo"))
            formatted_time = local_time.strftime("%I:%M %p").replace("AM", "صباحاً").replace("PM", "مساءً")
            event_list.append(f"- عندك '{event['summary']}' الساعة {formatted_time}")
        return "\n".join(event_list)
    except Exception as e:
        print_to_console(f"❌ خطأ في الوصول للتقويم: {e}")
        return "فيه مشكلة في الوصول لأجندة جوجل دلوقتي."

def take_screenshot():
    # ... (الكود يبقى كما هو) ...
    update_gui(status="جاري أخذ لقطة للشاشة...")
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"screenshot_{timestamp}.png"
        pyautogui.screenshot(file_name)
        return f"لقطة الشاشة اتحفظت يا فنان باسم {file_name} 📸"
    except Exception as e:
        print_to_console(f"❌ خطأ في أخذ لقطة شاشة: {e}")
        return "للأسف معرفتش أصور الشاشة، فيه حاجة غلط 😥"

APPS = {
    "notepad": "notepad.exe", "نوت باد": "notepad.exe",
    "calculator": "calc.exe", "اله حاسبه": "calc.exe", "الاله الحاسبه": "calc.exe",
    "excel": "excel.exe", "اكسل": "excel.exe",
    "word": "winword.exe", "وورد": "winword.exe",
    "paint": "mspaint.exe", "الرسام": "mspaint.exe"
}
def open_local_app(app_name: str):
    # ... (الكود يبقى كما هو) ...
    update_gui(status=f"جاري محاولة فتح {app_name}...")
    for name, path in APPS.items():
        if name in app_name.lower():
            try:
                os.startfile(path)
                return f"فتحتلك {name} فوراً 💻"
            except Exception:
                return f"حاولت أفتح {name} بس للأسف فشلت 😟"
    return f"معنديش فكرة إزاي أفتح برنامج اسمه {app_name} 🤔"

def read_screen_content():
    # ⭐ تم إزالة 'speak' من هنا
    update_gui(status="جاري تحليل محتوى الشاشة...")
    try:
        screenshot = pyautogui.screenshot()
        text_on_screen = pytesseract.image_to_string(screenshot, lang='ara+eng')
        if not text_on_screen.strip():
            return "الشاشة فاضية، ملقتش أي نص أقرأه."
        update_gui(status="جاري تلخيص النص...")
        summary_prompt = f"لخص النص التالي المأخوذ من شاشة المستخدم في نقاط رئيسية وموجزة جداً باللغة العربية: --- {text_on_screen} ---"
        summary_model = genai.GenerativeModel('gemini-1.5-flash')
        response = summary_model.generate_content(summary_prompt)
        return f"ملخص اللي على الشاشة بيقول: {response.text}"
    except pytesseract.TesseractNotFoundError:
        return "Tesseract مش متثبت صح. مقدرش أقرأ الشاشة من غيره."
    except Exception as e:
        print_to_console(f"❌ خطأ في قراءة الشاشة: {e}")
        return "حصل خطأ غريب وأنا بحاول أقرأ الشاشة."

def play_on_youtube(search_query: str):
    # ⭐ تم إزالة 'speak' من هنا
    update_gui(status=f"جاري البحث عن '{search_query}' في يوتيوب...")
    if not is_internet_available():
        return "يوتيوب محتاج نت يا صاحبي! 📶"
    try:
        kit.playonyt(search_query)
        # الآن نعيد رسالة ليقوم main بنطقها
        return f"تمام، شغلتلك {search_query} على يوتيوب... استمتع! 😉"
    except Exception:
        return f"حاولت أشغلك {search_query} بس حصلت مشكلة."

def search_wikipedia(topic: str):
    # ... (الكود يبقى كما هو) ...
    update_gui(status=f"جاري البحث عن '{topic}' في ويكيبيديا...")
    if not is_internet_available():
        return "ويكيبيديا كمان محتاجة نت للأسف 🤷‍♂️"
    try:
        wikipedia.set_lang("ar")
        summary = wikipedia.summary(topic, sentences=2)
        return f"ويكيبيديا بتقول عن {topic}:\n{summary}"
    except Exception:
         return f"دورت كويس بس ملقتش حاجة عن {topic} في ويكيبيديا 🧐"
         
def open_website(website_name: str):
    # ⭐ تم إزالة 'speak' من هنا
    update_gui(status=f"جاري فتح موقع {website_name}...")
    if not is_internet_available():
        return "لا يمكنني فتح المواقع بدون اتصال بالإنترنت."
    clean_name = website_name.replace(' ', '').lower()
    if '.' not in clean_name:
        clean_name += '.com'
    url = f"https://www.{clean_name}"
    webbrowser.open(url)
    return f"فتحتلك موقع {website_name} يا كبير! 👍"
    
def control_media(action: str):
    # ... (الكود يبقى كما هو) ...
    action = action.lower()
    try:
        if any(word in action for word in ["play", "pause", "شغل", "وقف", "شغال", "كمل"]):
            pyautogui.press('playpause'); return "تم يا فندم."
        elif any(word in action for word in ["next", "التالية", "بعدها"]):
            pyautogui.press('nexttrack'); return "اللي بعده!"
        elif any(word in action for word in ["previous", "السابقة", "قبلها"]):
            pyautogui.press('prevtrack'); return "رجعنا للي فات."
        elif any(word in action for word in ["volume up", "ارفع", "علي"]):
            pyautogui.press('volumeup', presses=5); return "عليت الصوت 🔊"
        elif any(word in action for word in ["volume down", "وطي", "اخفض"]):
            pyautogui.press('volumedown', presses=5); return "وطيت الصوت 🔉"
        elif any(word in action for word in ["mute", "اكتم", "صامت"]):
            pyautogui.press('volumemute'); return "شششش 🤫"
        else:
            return "مش فاهم قصدك بإيه في التحكم في الميديا."
    except Exception as e:
        print_to_console(f"❌ حدث خطأ في التحكم بالميديا: {e}")
        return "معرفتش أتحكم في الميديا، فيه حاجة غلط."