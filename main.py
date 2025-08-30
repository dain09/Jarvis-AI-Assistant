# main.py
# ==============================================================================
# J.A.R.V.I.S. Project - The Conductor (v2 - Handles Speaking Logic)
# ==============================================================================

import datetime
import logging
import time
import random
import threading
import importlib # لاستيراد المكتبات بشكل ديناميكي

# استيراد المكتبات الأساسية
import config
import utils
import gemini_mastermind
import gui

# ⭐ تحديث: استيراد المكتبات الثقيلة داخل الدالة لتسريع بدء التشغيل
def lazy_import_tools():
    global tools
    tools_module = importlib.import_module("tools")
    return tools_module

tools = None # سيتم تحميله لاحقاً

# ... (إعدادات logging تبقى كما هي) ...
logging.basicConfig(filename=config.LOG_FILE_NAME, level=logging.INFO, 
                    format='%(asctime)s - %(message)s', encoding='utf-8')

# ==============================================================================
# القسم الثاني: "عقل" جارفيس (الحلقة الرئيسية)
# ==============================================================================

def run_jarvis_logic(app_instance):
    """
    الحلقة الرئيسية التي تعمل في خيط منفصل.
    """
    global tools
    tools = lazy_import_tools() # تحميل الأدوات عند بدء الخيط

    utils.app_instance = app_instance
    utils.wishMe() # تم التبسيط
    utils.speak("قولي أؤمر بإيه؟")
    
    last_interaction_time = time.time()

    while app_instance.is_running:
        query = utils.takeCommand()
        
        if query:
            last_interaction_time = time.time()
            logging.info(f"User: {query}")

            # ⭐ تحديث: منطق النطق قبل التنفيذ لبعض الأوامر
            if "يوتيوب" in query or "شغل" in query and "على يوتيوب" in query:
                utils.speak("تمام، طلبك بيتحضر على يوتيوب 🎬")
            elif "افتح موقع" in query:
                utils.speak("ثانية واحدة هفتحلك الموقع.")

            response = gemini_mastermind.ask_the_mastermind(query)
            utils.speak(response)
            logging.info(f"Jarvis: {response}")
        
        elif time.time() - last_interaction_time > 45:
            idle_message = random.choice(config.IDLE_CHAT_STARTERS)
            utils.speak(idle_message)
            logging.info(f"Jarvis (Idle): {idle_message}")
            last_interaction_time = time.time()

# ==============================================================================
# القسم الرابع: نقطة انطلاق البرنامج
# ==============================================================================

if __name__ == "__main__":
    # استبدال wishMe و morning_briefing بدوال أبسط لتسريع البدء
    utils.wishMe = lambda: utils.speak(f"أهلاً بعودتك يا {config.CREATOR_NAME}")
    
    app = gui.JarvisApp()
    jarvis_thread = threading.Thread(target=run_jarvis_logic, args=(app,), daemon=True)
    jarvis_thread.start()
    app.mainloop()