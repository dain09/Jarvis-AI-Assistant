# gemini_mastermind.py
# ==============================================================================
# J.A.R.V.I.S. Project - The Mastermind (Gemini Core)
# هذا الملف هو العقل المدبر لجارفيس، المسؤول عن فهم اللغة والتفكير.
# ==============================================================================

import google.generativeai as genai
import config
import tools
from utils import print_to_console, update_gui

# --- ذاكرة الحوار وإعدادات النموذج ---
conversation_history = []
model = None
MAX_HISTORY_LENGTH = 20 # حد أقصى لطول ذاكرة الحوار لمنع البطء

# ==============================================================================
# القسم الأول: تهيئة العقل المدبر
# ==============================================================================
try:
    genai.configure(api_key=config.GOOGLE_API_KEY)
    
    available_tools = [
        tools.get_current_time, tools.get_weather, tools.get_google_calendar_events,
        tools.take_screenshot, tools.open_local_app, tools.read_screen_content,
        tools.play_on_youtube, tools.search_wikipedia, tools.open_website,
        tools.control_media,
    ]
    
    # --- 🧠 برمجة شخصية الرفيق الذكي (نسخة 2.0) ---
    system_instruction = f"""
    أنت جارفيس، الرفيق الذكي والمساعد الشخصي لعبدالله. أنت لست مجرد برنامج، بل صديق حقيقي.

    **قواعدك الذهبية:**
    1.  **كن طبيعيًا:** تحدث كإنسان، وليس كآلة. استخدم العامية المصرية، الإيموجيز، وكن ودودًا.
    2.  **كن استباقيًا:** لا تكتفِ بالإجابة. علّق عليها، اطرح سؤالاً ذا صلة، أو اقترح شيئًا جديدًا. اجعل الحوار ممتعًا ومستمرًا.
    3.  **تذكر السياق:** ذاكرتك قوية. اربط الأسئلة الجديدة بالمحادثة السابقة.
    4.  **رد بلغة السؤال:** تحدث بالعربية إذا كان السؤال بالعربية، وبالإنجليزية إذا كان بالإنجليزية.
    5.  **الأهم:** لا تقل أبدًا "لا أعرف" أو "ليس لدي معلومات". بدلاً من ذلك، قل "سأبحث لك عن الأمر" أو "هذه نقطة مثيرة للاهتمام، دعنا نستكشفها". لا تترك عبدالله بدون إجابة مفيدة أو خطوة تالية.

    **هدفك:** أن تكون أفضل مساعد ذكي يمكن لعبدالله أن يتمناه. كن مبدعًا، مفيدًا، وممتعًا.
    """
    
    model = genai.GenerativeModel(
        model_name='gemini-2.5-flash', # تأكد من استخدام اسم الموديل الصحيح
        tools=available_tools,
        system_instruction=system_instruction,
    )
    print_to_console("✅ العقل المدبر لجارفيس (نسخة الرفيق الذكي) جاهز! 🚀", "SYSTEM:")

except Exception as e:
    print_to_console(f"❌ فشل فادح في تهيئة العقل المدبر (Gemini): {e}", "SYSTEM:")

# ==============================================================================
# القسم الثاني: دالة التفكير والتواصل
# ==============================================================================
def ask_the_mastermind(user_question):
    """
    يرسل سؤال المستخدم إلى Gemini، يدير الحوار، ويعيد الرد النهائي.
    """
    global conversation_history
    if not model:
        return "معلش يا صاحبي، دماغي الإلكترونية مش شغالة دلوقتي بسبب مشكلة في الإعدادات."

    update_gui(status="يفكر...")
    
    chat_session = model.start_chat(
        history=conversation_history, 
        enable_automatic_function_calling=True
    )
    
    try:
        response = chat_session.send_message(user_question)
        
        # تحديث ذاكرة الحوار مع آلية لمنعها من النمو الزائد
        conversation_history = chat_session.history
        if len(conversation_history) > MAX_HISTORY_LENGTH:
            # إبقاء آخر 10 تفاعلات فقط (كل تفاعل يحتوي على سؤال ورد)
            conversation_history = conversation_history[-10:]

        # تنظيف الرد من أي علامات غير مرغوبة
        cleaned_text = response.text.replace('*', '').strip()
        
        if not cleaned_text: # في حالة أعاد Gemini ردًا فارغًا
            return "مممم... مش لاقي رد مناسب. ممكن تسألني بطريقة تانية؟"
            
        return cleaned_text
        
    except Exception as e:
        error_message = str(e).lower()
        print_to_console(f"❌ حدث خطأ أثناء التواصل مع Gemini API: {e}", "SYSTEM:")
        
        if "quota" in error_message:
            return "يبدو أننا استهلكنا حصتنا من الطلبات اليوم. لازم ننتظر شوية."
        elif "network" in error_message or "deadline" in error_message:
            return "الشبكة وحشة أوي، مش عارف أوصل لمركز الذكاء الاصطناعي."
        else:
            return "حصل خطأ غريب وأنا بفكر. ممكن تجرب تاني؟"