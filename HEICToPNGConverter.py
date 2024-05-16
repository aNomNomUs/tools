import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def check_and_install_packages():
    required_packages = {
        "Pillow": "pillow",
        "pillow_heif": "pillow-heif"
    }

    try:
        import pkg_resources
    except ImportError:
        install("setuptools")
        import pkg_resources

    installed_packages = {pkg.key for pkg in pkg_resources.working_set}
    missing_packages = [pkg for pkg, pkg_name in required_packages.items() if pkg.lower() not in installed_packages]

    if missing_packages:
        print("The following packages are required but not installed: " + ', '.join(missing_packages))
        install_permission = input("Do you want to install these packages now? (yes/no): ").lower()
        if install_permission == 'yes':
            for package in missing_packages:
                print(f"Installing {package}...")
                install(required_packages[package])
            print("All required packages have been installed.")
        else:
            print("The required packages were not installed. Exiting...")
            sys.exit(1)
    else:
        print("All required packages are already installed.")

# Check and install packages at the beginning of the script execution
check_and_install_packages()

# Now safe to import other libraries
import os
import logging
from tkinter import Tk, Button, Label, filedialog, messagebox, Text, END, Checkbutton, IntVar
import tkinter as tk
from PIL import Image
import pillow_heif
from tkinter.ttk import Progressbar
import threading

def setup_logging():
    logging.basicConfig(
        filename='conversion.log',
        filemode='w',
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

class HEICToPNGConverter:
    def __init__(self, root):
        self.root = root
        self.overwrite = IntVar()
        self.setup_ui()

    def setup_ui(self):
        self.folder_path = tk.StringVar()

        Label(self.root, text="Select a folder containing HEIC images:").pack(pady=10)

        Button(self.root, text="Select Folder", command=self.select_folder).pack(pady=5)

        self.progress = Progressbar(self.root, orient=tk.HORIZONTAL, length=300, mode='determinate')
        self.progress.pack(pady=20)

        self.convert_button = Button(self.root, text="Start Conversion", command=self.start_conversion_thread, state="disabled")
        self.convert_button.pack(pady=5)

        Checkbutton(self.root, text="Overwrite existing PNG files", variable=self.overwrite).pack(pady=5)

        self.log_text = Text(self.root, height=10, width=50)
        self.log_text.pack(pady=10)

    def select_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)
            self.convert_button.config(state="normal")
            self.log_text.insert(END, f"Folder selected: {folder_selected}\n")

    def start_conversion_thread(self):
        threading.Thread(target=self.start_conversion).start()

    def start_conversion(self):
        directory = self.folder_path.get()
        if directory:
            successful_conversions, failed_conversions = self.convert_heic_to_png(directory)
            self.show_results(successful_conversions, failed_conversions)
        self.progress['value'] = 0

    def convert_heic_to_png(self, directory):
        setup_logging()
        pillow_heif.register_heif_opener()
        files = [f for f in os.listdir(directory) if f.lower().endswith('.heic')]
        total = len(files)
        failed_conversions = []
        successful_conversions = []

        for index, filename in enumerate(files):
            heic_path = os.path.join(directory, filename)
            png_path = os.path.splitext(heic_path)[0] + '.png'
            
            if os.path.exists(png_path) and not self.overwrite.get():
                message = f"{png_path} already exists. Skipping conversion.\n"
                logging.warning(message)
                self.log_text.insert(END, message)
                continue

            try:
                with Image.open(heic_path) as image:
                    image.save(png_path, "PNG")
                message = f"Converted {heic_path} to {png_path}\n"
                logging.info(message)
                self.log_text.insert(END, message)
                successful_conversions.append(filename)
            except Exception as e:
                message = f"Failed to convert {heic_path}: {e}\n"
                logging.error(message)
                self.log_text.insert(END, message)
                failed_conversions.append(filename)

            self.progress['value'] = ((index + 1) / total) * 100
            self.root.update_idletasks()
        
        return successful_conversions, failed_conversions

    def show_results(self, successful_conversions, failed_conversions):
        message = f"Successful conversions: {len(successful_conversions)}\n"
        if failed_conversions:
            message += f"Failed conversions: {', '.join(failed_conversions)}"
        messagebox.showinfo("Conversion Results", message)

if __name__ == '__main__':
    root = Tk()
    root.title("HEIC to PNG Converter")
    app = HEICToPNGConverter(root)
    root.mainloop()
