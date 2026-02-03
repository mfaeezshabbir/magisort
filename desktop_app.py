import os
import customtkinter as ctk
from tkinter import filedialog
from organizer import organize_folder, undo_organization, Path
import threading

# Set appearance and color theme
ctk.set_appearance_mode("Dark")

class MagisortApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("Magisort")
        self.geometry("500x700")
        self.configure(fg_color="#0f172a") # Deep navy background
        
        # Indigo Color Palette
        self.indigo = "#6366f1"
        self.indigo_hover = "#4f46e5"
        self.card_bg = "#1e293b"
        self.border_color = "#334155"

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) # Center card expands

        # 1. Header Section
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=20, pady=(40, 20), sticky="nsew")
        self.header_frame.grid_columnconfigure(0, weight=1)

        self.logo_label = ctk.CTkLabel(
            self.header_frame, text="✨", 
            font=ctk.CTkFont(size=32)
        )
        self.logo_label.grid(row=0, column=0, pady=(0, 5))

        self.title_label = ctk.CTkLabel(
            self.header_frame, text="Magisort", 
            font=ctk.CTkFont(family="Inter", size=36, weight="bold"),
            text_color="#ffffff"
        )
        self.title_label.grid(row=1, column=0)

        # 2. Path Selection Section (Top Row)
        self.path_frame = ctk.CTkFrame(self, fg_color=self.card_bg, corner_radius=12, border_width=1, border_color=self.border_color)
        self.path_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.path_frame.grid_columnconfigure(1, weight=1)

        self.folder_icon = ctk.CTkLabel(self.path_frame, text="📂", font=ctk.CTkFont(size=18))
        self.folder_icon.grid(row=0, column=0, padx=(15, 5), pady=10)

        self.path_entry = ctk.CTkEntry(
            self.path_frame, 
            placeholder_text="C:/Users/Example/Documents", 
            fg_color="transparent", 
            border_width=0,
            text_color="#94a3b8",
            font=ctk.CTkFont(size=13)
        )
        self.path_entry.grid(row=0, column=1, sticky="ew", padx=5)

        self.browse_button = ctk.CTkButton(
            self.path_frame, text="Browse", width=80, height=32,
            fg_color="#334155", hover_color="#475569",
            command=self.browse_folder
        )
        self.browse_button.grid(row=0, column=2, padx=10, pady=10)

        # 3. Central Status Card
        self.center_card = ctk.CTkFrame(self, fg_color="#161e2e", corner_radius=20, border_width=0)
        self.center_card.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")
        self.center_card.grid_columnconfigure(0, weight=1)
        self.center_card.grid_rowconfigure(0, weight=1)

        # Decorative Illustration placeholder
        self.illustrations_frame = ctk.CTkFrame(self.center_card, fg_color="transparent")
        self.illustrations_frame.grid(row=0, column=0) # Removed sticky="center"
        
        self.file_icon = ctk.CTkLabel(self.illustrations_frame, text="📄📄\n📄📄", font=ctk.CTkFont(size=40), text_color="#6366f1")
        self.file_icon.grid(row=0, column=0, padx=10)
        
        self.arrow_label = ctk.CTkLabel(self.illustrations_frame, text="→", font=ctk.CTkFont(size=30), text_color="#475569")
        self.arrow_label.grid(row=0, column=1, padx=20)
        
        self.dest_folder_icon = ctk.CTkLabel(self.illustrations_frame, text="📁", font=ctk.CTkFont(size=60), text_color="#6366f1")
        self.dest_folder_icon.grid(row=0, column=2, padx=10)

        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(self.center_card, width=300, height=8, progress_color=self.indigo, fg_color="#334155")
        self.progress_bar.grid(row=1, column=0, pady=(0, 20))
        self.progress_bar.set(0)

        self.status_text = ctk.CTkLabel(
            self.center_card, text="Ready to sort", 
            font=ctk.CTkFont(size=14),
            text_color="#94a3b8"
        )
        self.status_text.grid(row=2, column=0, pady=(0, 40))

        # 4. Action Buttons (Bottom)
        self.actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.actions_frame.grid(row=3, column=0, padx=20, pady=(0, 40), sticky="ew")
        self.actions_frame.grid_columnconfigure((0, 1), weight=1)

        self.organize_btn = ctk.CTkButton(
            self.actions_frame, text="🪄 Organize Folder", 
            height=56, corner_radius=14,
            fg_color=self.indigo, hover_color=self.indigo_hover,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.run_organize
        )
        self.organize_btn.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        self.undo_btn = ctk.CTkButton(
            self.actions_frame, text="↺ Undo Last", 
            height=56, corner_radius=14,
            fg_color="#312e81", hover_color="#3730a3", # Darker indigo
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.run_undo
        )
        self.undo_btn.grid(row=0, column=1, padx=(10, 0), sticky="ew")

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, folder)
            self.status_text.configure(text=f"Selected: {os.path.basename(folder)}")

    def update_progress(self, val):
        self.progress_bar.set(val)

    def run_organize(self):
        path = self.path_entry.get().strip()
        if not path:
            self.status_text.configure(text="Error: Please select a folder", text_color="#ef4444")
            return

        def task():
            try:
                self.organize_btn.configure(state="disabled")
                self.status_text.configure(text="Sorting in progress...", text_color="#94a3b8")
                self.progress_bar.set(0.3)
                
                organize_folder(path)
                
                self.progress_bar.set(1.0)
                self.status_text.configure(text="Done! Everything is sorted.", text_color="#22c55e")
            except Exception as e:
                self.status_text.configure(text=f"Error: {str(e)}", text_color="#ef4444")
            finally:
                self.organize_btn.configure(state="normal")

        threading.Thread(target=task).start()

    def run_undo(self):
        path = self.path_entry.get().strip()
        if not path:
            self.status_text.configure(text="Error: Select folder to undo", text_color="#ef4444")
            return

        def task():
            try:
                self.undo_btn.configure(state="disabled")
                self.status_text.configure(text="Reverting changes...", text_color="#94a3b8")
                self.progress_bar.set(0.5)
                
                undo_organization(path)
                
                self.progress_bar.set(0)
                self.status_text.configure(text="Changes reverted successfully.", text_color="#6366f1")
            except Exception as e:
                self.status_text.configure(text=f"Error: {str(e)}", text_color="#ef4444")
            finally:
                self.undo_btn.configure(state="normal")

        threading.Thread(target=task).start()

if __name__ == "__main__":
    app = MagisortApp()
    app.mainloop()
