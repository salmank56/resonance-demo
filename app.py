import os
import sys
import shutil
import threading
import subprocess
import tkinter as tk
from logger_config import setup_logging
from tkinter import filedialog, messagebox, scrolledtext

setup_logging()

class CSVUploader:
    def __init__(self, root):
        self.root = root
        self.root.title("Scraping at Scale")
        #self.root.geometry("600x400")  # Set the window size

        # Title Label
        title_label = tk.Label(root, text="Scraping at Scale", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=20)

        # Upload Button
        self.upload_button = tk.Button(root, text="Upload CSV", command=self.upload_csv, font=("Helvetica", 12))
        self.upload_button.pack(pady=10)

        # Start Button
        self.start_button = tk.Button(root, text="Start Scraping", command=self.start_scraping, state=tk.DISABLED, font=("Helvetica", 12))
        self.start_button.pack(pady=10)

        # Console Output
        self.console_output = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Helvetica", 10))
        self.console_output.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Redirect stdout and stderr
        sys.stdout = self
        sys.stderr = self

        self.csv_path = None
        self.process = None

    def write(self, message):
        self.console_output.insert(tk.END, message)
        self.console_output.see(tk.END)

    def flush(self):
        pass

    def upload_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.csv_path = file_path
            self.save_csv()
            self.start_button.config(state=tk.NORMAL)

    def save_csv(self):
        target_dir = os.getcwd()  # You can change this to your desired directory
        target_path = os.path.join(target_dir, "companies_list.csv")
        try:
            if os.path.exists(target_path):
                os.remove(target_path)
            shutil.copy(self.csv_path, target_path)
            messagebox.showinfo("Success", "CSV file copied and saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save CSV file: {e}")

    def start_scraping(self):
        def run_scraping():
            try:
                self.process = subprocess.Popen(
                    ["python", "main.py"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                for stdout_line in iter(self.process.stdout.readline, ""):
                    print(stdout_line, end="")
                for stderr_line in iter(self.process.stderr.readline, ""):
                    print(stderr_line, end="")
                self.process.stdout.close()
                self.process.stderr.close()
                self.process.wait()
                if self.process.returncode == 0:
                    messagebox.showinfo("Success", "Scraping completed successfully.")
                else:
                    messagebox.showerror("Error", "Scraping failed.")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Scraping failed: {e}")

        threading.Thread(target=run_scraping).start()

    def close_app(self):
        if self.process:
            self.process.terminate()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CSVUploader(root)
    root.mainloop()
