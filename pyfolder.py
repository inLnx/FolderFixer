import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pathlib
import json
import shutil
import time
import os

class FolderFixApp:

    def __init__(self, root):
        self.root = root
        self.root.title("FolderFix - Clutter-Free Folders")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")

        self.selected_folder = ""
        self.file_preview_plan = {}
        self.undo_log_path = pathlib.Path("undo_log.json")
        self.config_path = pathlib.Path("config.json")
        self.categories = {}
        self.progress_bar = None
        self.is_sorting = False

        self.create_widgets()
        self.load_config()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="20 20 20 20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.configure(style="TFrame")

        self.style = ttk.Style()
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TButton", font=("Inter", 12), padding=10, relief="flat", background="#e0e0e0")
        self.style.map("TButton", background=[("active", "#d0d0d0")])
        self.style.configure("TLabel", font=("Inter", 12), background="#f0f0f0")
        self.style.configure("Header.TLabel", font=("Inter", 16, "bold"), background="#f0f0f0")
        self.style.configure("Status.TLabel", font=("Inter", 10, "italic"), background="#f0f0f0")

        header_label = ttk.Label(main_frame, text="FolderFix", style="Header.TLabel")
        header_label.pack(pady=(0, 10))
        ttk.Label(main_frame, text="Automatically organize your files with a click.", style="TLabel").pack(pady=(0, 20))

        folder_frame = ttk.Frame(main_frame, style="TFrame")
        folder_frame.pack(fill=tk.X, pady=10)

        self.folder_label = ttk.Label(folder_frame, text="No folder selected", style="TLabel")
        self.folder_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        select_btn = ttk.Button(folder_frame, text="Select Folder", command=self.select_folder)
        select_btn.pack(side=tk.RIGHT)

        button_frame = ttk.Frame(main_frame, style="TFrame")
        button_frame.pack(fill=tk.X, pady=10)

        self.preview_btn = ttk.Button(button_frame, text="Generate Preview", command=self.generate_preview, state=tk.DISABLED)
        self.preview_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.sort_btn = ttk.Button(button_frame, text="Sort Files", command=self.sort_files, state=tk.DISABLED)
        self.sort_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))

        self.undo_btn = ttk.Button(button_frame, text="Undo Last Sort", command=self.undo_last_sort)
        self.undo_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

        self.config_btn = ttk.Button(button_frame, text="Open Config", command=self.open_config)
        self.config_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

        ttk.Label(main_frame, text="Proposed Changes / History Log", style="TLabel").pack(pady=(10, 5))
        self.log_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=15, font=("Courier", 10), state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        status_frame = ttk.Frame(self.root, relief=tk.SUNKEN)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_label = ttk.Label(status_frame, text="Ready.", style="Status.TLabel", anchor=tk.W)
        self.status_label.pack(fill=tk.X, padx=10, pady=5)

        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", mode="determinate")
        self.progress_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=5)

    def log_message(self, message):
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)
        self.root.update_idletasks()

    def set_status(self, message):
        self.status_label.configure(text=message)
        self.root.update_idletasks()

    def load_config(self):
        try:
            if not self.config_path.exists():
                default_config = {
                    "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".xls", ".xlsx", ".ppt", ".pptx"],
                    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".ico", ".raw", ".tiff"],
                    "Videos": [".mp4", ".mov", ".avi", ".mkv", ".flv", ".webm", ".3gp", ".mpeg", ".wmv"],
                    "Audio": [".mp3", ".wav", ".aac", ".flac", ".ogg", ".wma"],
                    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".iso"],
                    "Executables": [".exe", ".dmg", ".pkg", ".app", ".msi"],
                    "Code": [".py", ".js", ".html", ".css", ".java", ".c", ".cpp", ".h", ".sh", ".json", ".xml"]
                }
                with open(self.config_path, "w") as f:
                    json.dump(default_config, f, indent=4)
                self.log_message(f"Created default config file at: {self.config_path}")

            with open(self.config_path, "r") as f:
                self.categories = json.load(f)
            self.set_status("Configuration loaded successfully.")

        except (IOError, json.JSONDecodeError) as e:
            messagebox.showerror("Config Error", f"Could not load config file: {e}")
            self.set_status("Error loading configuration.")

    def open_config(self):
        try:
            os.startfile(self.config_path)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open config file: {e}")

    def select_folder(self):
        new_folder = filedialog.askdirectory()
        if new_folder:
            self.selected_folder = pathlib.Path(new_folder)
            self.folder_label.config(text=f"Selected folder: {self.selected_folder}")
            self.preview_btn.config(state=tk.NORMAL)
            self.sort_btn.config(state=tk.DISABLED)
            self.log_text.configure(state=tk.NORMAL)
            self.log_text.delete("1.0", tk.END)
            self.log_text.configure(state=tk.DISABLED)
            self.set_status(f"Folder selected. Ready to generate preview.")

    def generate_preview(self):
        if not self.selected_folder or not self.selected_folder.is_dir():
            messagebox.showerror("Error", "Please select a valid folder first.")
            return

        self.set_status("Scanning folder and generating preview...")
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.insert(tk.END, f"--- PREVIEWING CHANGES FOR: {self.selected_folder} ---\n\n")
        self.file_preview_plan = {}
        total_files = 0
        moved_count = 0

        files_to_check = (f for f in self.selected_folder.rglob("*") if f.is_file())

        for file_path in files_to_check:
            if file_path.name in ["config.json", "undo_log.json", os.path.basename(__file__)]:
                continue
            
            total_files += 1
            file_extension = file_path.suffix.lower()
            found_category = None

            for category, extensions in self.categories.items():
                if file_extension in extensions:
                    found_category = category
                    break

            if found_category:
                destination_folder = self.selected_folder / found_category
                if destination_folder.exists() and not destination_folder.is_dir():
                    self.log_message(f"Warning: A file named '{found_category}' exists. Cannot create a folder for it.")
                    continue
                
                if found_category not in self.file_preview_plan:
                    self.file_preview_plan[found_category] = []
                self.file_preview_plan[found_category].append(file_path)
                
                self.log_text.insert(tk.END, f"[PREVIEW] Move '{file_path.name}' to '{found_category}'\n")
                moved_count += 1
        
        self.log_text.insert(tk.END, f"\n--- END OF PREVIEW ---\nFound {total_files} files, {moved_count} will be moved.\n")
        self.log_text.configure(state=tk.DISABLED)
        self.set_status("Preview generated. Ready to sort.")
        self.sort_btn.config(state=tk.NORMAL if moved_count > 0 else tk.DISABLED)

    def sort_files(self):
        if self.is_sorting:
            messagebox.showwarning("Warning", "Sorting is already in progress.")
            return

        if not self.file_preview_plan:
            messagebox.showinfo("Info", "No files burh :(")
            return

        response = messagebox.askyesno(
            "Confirm Sort",
            f"Are you sure you want to move files in '{self.selected_folder}' according to the preview?"
        )
        if not response:
            return

        self.is_sorting = True
        self.set_status("Sorting files...")
        self.sort_btn.config(state=tk.DISABLED)
        self.preview_btn.config(state=tk.DISABLED)
        self.undo_btn.config(state=tk.DISABLED)
        
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.insert(tk.END, "--- STARTING SORT OPERATION ---\n\n")

        current_undo_log = {"timestamp": time.time(), "moves": []}
        
        total_files_to_move = sum(len(files) for files in self.file_preview_plan.values())
        moved_count = 0
        self.progress_bar["maximum"] = total_files_to_move
        self.progress_bar["value"] = 0

        batch_size = 100
        processed_in_batch = 0

        for category, files in self.file_preview_plan.items():
            destination_folder = self.selected_folder / category
            try:
                destination_folder.mkdir(exist_ok=True)
            except OSError as e:
                self.log_message(f"Error creating directory '{destination_folder}': {e}")
                continue

            for file_path in files:
                new_path = destination_folder / file_path.name
                
                try:
                    shutil.move(file_path, new_path)
                    current_undo_log["moves"].append({
                        "original": str(file_path),
                        "destination": str(new_path)
                    })
                    self.log_message(f"Moved: '{file_path.name}' -> '{category}'")
                    
                    moved_count += 1
                    processed_in_batch += 1
                    self.progress_bar["value"] = moved_count
                    self.root.update_idletasks()
                    
                    if processed_in_batch >= batch_size:
                        time.sleep(0.01)
                        processed_in_batch = 0

                except Exception as e:
                    self.log_message(f"Error moving file '{file_path.name}': {e}")
        
        if current_undo_log["moves"]:
            with open(self.undo_log_path, "w") as f:
                json.dump(current_undo_log, f, indent=4)
            self.log_message(f"\nSort complete. {moved_count} files moved. Undo log saved.")
        else:
            self.log_message("\nSort complete. No files were moved.")

        self.set_status("Sorting finished.")
        self.sort_btn.config(state=tk.DISABLED)
        self.preview_btn.config(state=tk.NORMAL)
        self.undo_btn.config(state=tk.NORMAL)
        self.is_sorting = False

    def undo_last_sort(self):
        if not self.undo_log_path.exists():
            messagebox.showinfo("Info", "No undo log found.")
            return

        response = messagebox.askyesno(
            "Confirm Undo",
            "Are you sure you want to undo the last sort operation?"
        )
        if not response:
            return

        try:
            with open(self.undo_log_path, "r") as f:
                undo_data = json.load(f)
            
            self.set_status("Undoing last sort...")
            self.log_text.configure(state=tk.NORMAL)
            self.log_text.delete("1.0", tk.END)
            self.log_text.insert(tk.END, "--- STARTING UNDO OPERATION ---\n\n")

            total_to_undo = len(undo_data["moves"])
            undone_count = 0
            self.progress_bar["maximum"] = total_to_undo
            self.progress_bar["value"] = 0

            for move in reversed(undo_data["moves"]):
                original_path = pathlib.Path(move["original"])
                destination_path = pathlib.Path(move["destination"])
                
                try:
                    shutil.move(destination_path, original_path)
                    self.log_message(f"Undid: '{destination_path.name}' -> '{original_path.parent.name}'")

                    undone_count += 1
                    self.progress_bar["value"] = undone_count
                    self.root.update_idletasks()

                except Exception as e:
                    self.log_message(f"Error undoing file move for '{destination_path.name}': {e}")

            for move in undo_data["moves"]:
                destination_path = pathlib.Path(move["destination"])
                if destination_path.parent.exists() and not any(destination_path.parent.iterdir()):
                    try:
                        destination_path.parent.rmdir()
                        self.log_message(f"Removed empty directory: '{destination_path.parent.name}'")
                    except OSError as e:
                        self.log_message(f"Error removing directory '{destination_path.parent.name}': {e}")

            os.remove(self.undo_log_path)
            self.log_message("\nUndo complete. Log file deleted.")
            self.set_status("Undo finished.")
            self.sort_btn.config(state=tk.DISABLED)

        except (IOError, json.JSONDecodeError) as e:
            messagebox.showerror("Undo Error", f"Could not read undo log: {e}")
            self.set_status("Error during undo process.")

if __name__ == "__main__":
    root = tk.Tk()
    app = FolderFixApp(root)
    root.mainloop()
