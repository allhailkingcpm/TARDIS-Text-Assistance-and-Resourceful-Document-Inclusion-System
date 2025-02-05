from updater import Updater
# ...existing imports...

class MathTranslatorApp:
    def __init__(self):
        # ...existing init code...
        
        # Initialize updater
        self.updater = Updater()
        self.check_for_updates()
        
        # ...rest of init code...

    def check_for_updates(self):
        """Check for and handle updates"""
        if self.updater.check_for_updates():
            update_window = ctk.CTkToplevel(self.window)
            update_window.title("Update Available")
            update_window.geometry("300x150")
            
            label = ctk.CTkLabel(
                update_window, 
                text="A new version is available.\nWould you like to update now?"
            )
            label.pack(pady=20)
            
            def do_update():
                if self.updater.download_and_install_update():
                    self.show_notification("Update downloaded. Restarting...")
                    self.window.after(2000, self.window.destroy)  # Close after 2 seconds
                update_window.destroy()
            
            def skip_update():
                update_window.destroy()
            
            update_btn = ctk.CTkButton(
                update_window,
                text="Update Now",
                command=do_update
            )
            update_btn.pack(pady=5)
            
            skip_btn = ctk.CTkButton(
                update_window,
                text="Skip",
                command=skip_update
            )
            skip_btn.pack(pady=5)
