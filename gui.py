# gui.py
# ==============================================================================
# J.A.R.V.I.S. Project - GUI (v6 - Grid Layout Fix)
# ==============================================================================

import customtkinter as ctk
import config
import threading
import time

class JarvisApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.is_running = True
        self.title(f"{config.JARVIS_NAME} - Personal Assistant")
        self.geometry("800x600")
        self.minsize(600, 400)
        
        ctk.set_appearance_mode(config.APPEARANCE_MODE)
        ctk.set_default_color_theme(config.COLOR_THEME)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._animation_thread = None
        self._is_animating = False

        self.create_header()
        self.create_conversation_log()
        self.create_status_bar()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_header(self):
        """إنشاء الجزء العلوي من الواجهة (الرأس)."""
        header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=config.SECONDARY_BG_COLOR)
        header_frame.grid(row=0, column=0, sticky="ew")
        
        # ⭐ تصحيح: استخدام grid هنا أيضاً
        header_frame.grid_columnconfigure(0, weight=1) # لجعل العنوان يتوسط الإطار
        
        header_label = ctk.CTkLabel(
            header_frame, 
            text=f"{config.JARVIS_NAME}",
            font=(config.FONT_FAMILY, config.TITLE_FONT_SIZE, "bold"),
            text_color=config.ACCENT_COLOR
        )
        # ⭐ تصحيح: استبدال pack بـ grid
        header_label.grid(row=0, column=0, pady=15)
        
    def create_conversation_log(self):
        # ... (لا تغيير هنا) ...
        self.conversation_log = ctk.CTkTextbox(self, font=(config.FONT_FAMILY, config.NORMAL_FONT_SIZE), text_color=config.TEXT_COLOR, fg_color=config.MAIN_BG_COLOR, border_width=0, wrap="word", state="disabled")
        self.conversation_log.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.conversation_log.tag_config("jarvis_tag", foreground=config.ACCENT_COLOR, underline=True)
        self.conversation_log.tag_config("user_tag", foreground="white", underline=True)
        self.conversation_log.tag_config("right_align", justify="right")

    def create_status_bar(self):
        """إنشاء شريط الحالة السفلي."""
        status_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=config.SECONDARY_BG_COLOR, height=30)
        status_frame.grid(row=2, column=0, sticky="ew")

        # ⭐ تصحيح: استخدام grid هنا أيضاً
        self.status_label = ctk.CTkLabel(
            status_frame, 
            text="جاري بدء التشغيل...",
            font=(config.FONT_FAMILY, 12)
        )
        # ⭐ تصحيح: استبدال pack بـ grid
        self.status_label.grid(row=0, column=0, padx=10)

    # --- باقي الكود يبقى كما هو ---
    
    def update_status_label(self, new_status):
        if new_status.strip() == "يفكر...":
            self.start_thinking_animation()
        else:
            self.stop_thinking_animation()
            self.status_label.configure(text=new_status)

    def add_to_conversation_log(self, message, speaker):
        self.conversation_log.configure(state="normal")
        prompt_text = f":{config.JARVIS_NAME}" if speaker == "jarvis" else f":{config.CREATOR_NAME}"
        tag = "jarvis_tag" if speaker == "jarvis" else "user_tag"
        full_message = f"{message}{prompt_text}\n\n"
        self.conversation_log.insert("end", full_message, ("right_align",))
        start_index = self.conversation_log.index(f"end - {len(prompt_text) + 3}c")
        end_index = self.conversation_log.index(f"end - 3c")
        self.conversation_log.tag_add(tag, start_index, end_index)
        self.conversation_log.see("end")
        self.conversation_log.configure(state="disabled")

    def thinking_animation_loop(self):
        dots = ""
        while self._is_animating:
            dots = "" if len(dots) >= 3 else dots + "."
            self.status_label.configure(text=f"يفكر {dots}")
            time.sleep(0.5)

    def start_thinking_animation(self):
        if not self._is_animating:
            self._is_animating = True
            self._animation_thread = threading.Thread(target=self.thinking_animation_loop, daemon=True)
            self._animation_thread.start()

    def stop_thinking_animation(self):
        self._is_animating = False

    def on_closing(self):
        self._is_animating = False
        self.is_running = False
        self.destroy()

    def close_app(self):
        self.on_closing()

if __name__ == "__main__":
    app = JarvisApp()
    app.mainloop()