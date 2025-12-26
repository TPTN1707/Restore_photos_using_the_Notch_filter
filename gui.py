import pathlib
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageOps
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import cv2
from notchfilter import IdealNotchFilter, ButterworthNotchFilter, GaussianNotchFilter
import os 
from ctypes import *
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

if not os.path.exists('tmp'):
    os.makedirs('tmp')

def set_plot_title(title, fs = 16):
    plt.title(title, fontsize = fs)

class MainApp:
    def __init__(self):
        # Thiết lập root
        windll.shcore.SetProcessDpiAwareness(1)
        self.root = ttk.Window(themename="darkly")
        self.root.title("Bộ lọc Notch")
        self.root.iconphoto(False, tk.PhotoImage(file = pathlib.Path("img/icon.png")))
        self.root.geometry("1000x600")

        # Tạo frame chính
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        # Thiết lập phía bên trái của GUI
        self.left_frame = ttk.Labelframe(main_frame, text="Ảnh Gốc", padding=10)
        self.left_frame.pack(side=LEFT, fill=BOTH, expand=YES, padx=(0, 5))

        self.original_img = ttk.Label(self.left_frame, image="", text="Tải ảnh để xem trước tại đây!", wraplength=200)
        self.original_img.pack(fill=BOTH, expand=YES, pady=10)

        control_frame = ttk.Frame(self.left_frame)
        control_frame.pack(fill=X, expand=YES)

        self.btn_browse_img = ttk.Button(control_frame, text="Chọn Ảnh", command=self.browse_img, style='info.TButton')
        self.btn_browse_img.pack(side=LEFT, fill=X, expand=YES, padx=(0, 5))

        self.btn_apply_filter = ttk.Button(control_frame, text="Áp dụng Bộ lọc", command=self.apply_filter, style='success.TButton')
        self.btn_apply_filter.pack(side=LEFT, fill=X, expand=YES, padx=(5, 0))

        options_frame = ttk.Frame(self.left_frame)
        options_frame.pack(fill=X, expand=YES, pady=10)

        ttk.Label(options_frame, text="Loại Bộ lọc Notch:").grid(row=0, column=0, sticky="w", pady=5)
        self.select_filter_var = tk.StringVar(self.root)
        self.select_filter_var.set('Lý tưởng')
        self.select_filter = ttk.Combobox(options_frame, textvariable=self.select_filter_var, values=['Lý tưởng', 'Butterworth', 'Gaussian'])
        self.select_filter.grid(row=0, column=1, sticky="ew", pady=5)

        ttk.Label(options_frame, text="Số điểm:").grid(row=1, column=0, sticky="w", pady=5)
        self.number_of_points = ttk.Entry(options_frame)
        self.number_of_points.grid(row=1, column=1, sticky="ew", pady=5)
        self.number_of_points.insert(tk.END, '6')

        ttk.Label(options_frame, text="Bán kính băng tần:").grid(row=2, column=0, sticky="w", pady=5)
        self.frequency = ttk.Entry(options_frame)
        self.frequency.grid(row=2, column=1, sticky="ew", pady=5)
        self.frequency.insert(tk.END, '121.0')

        ttk.Label(options_frame, text="Bậc của Bộ lọc Butterworth:").grid(row=3, column=0, sticky="w", pady=5)
        self.butterworth_order = ttk.Entry(options_frame)
        self.butterworth_order.grid(row=3, column=1, sticky="ew", pady=5)
        self.butterworth_order.insert(tk.END, 1)

        options_frame.columnconfigure(1, weight=1)

        # Thiết lập phía bên phải của GUI
        self.right_frame = ttk.Labelframe(main_frame, text="Ảnh đã Lọc", padding=10)
        self.right_frame.pack(side=RIGHT, fill=BOTH, expand=YES, padx=(5, 0))

        self.filter_img = ttk.Label(self.right_frame, image="", text="Áp dụng bộ lọc cho ảnh\nđể xem kết quả tại đây!", wraplength=200)
        self.filter_img.pack(fill=BOTH, expand=YES, pady=10)

        self.btn_save_img = ttk.Button(self.right_frame, text="Lưu Ảnh này", command=self.save_img, style='info.TButton')
        self.btn_save_img.pack(fill=X, expand=YES, pady=(0, 5))

        self.btn_summary = ttk.Button(self.right_frame, text="Hiển thị Tổng quan", command=self.show_summary, style='info.TButton')
        self.btn_summary.pack(fill=X, expand=YES, pady=(0, 5))

        self.info_lbl = ttk.Label(self.right_frame, text="SẴN SÀNG")
        self.info_lbl.pack(fill=X, expand=YES, pady=(5, 0))

        self.progress_bar = ttk.Progressbar(self.right_frame, mode='indeterminate')
        self.progress_bar.pack(fill=X, expand=YES, pady=(5, 0))

    def browse_img(self):
        try:
            file = filedialog.askopenfilename(title="Tải Ảnh", filetypes=[('Ảnh', ['*jpeg','*png','*jpg'])])
            if file:
                file = ImageOps.grayscale((Image.open(file)))
                file.save(pathlib.Path("tmp/original_img.png"))
                file = ImageTk.PhotoImage(file)
                self.original_img.configure(text="", image=file)
                self.original_img.image = file
        except Exception as e:
            messagebox.showerror("Đã xảy ra lỗi!", str(e))

    def get_fshift_and_save_dft(self):
        img = Image.open(pathlib.Path("tmp/original_img.png"))
        img = np.asarray(img)
        f = np.fft.fft2(img)
        fshift = np.fft.fftshift(f)
        dft = 20 * np.log(np.abs(fshift))
        matplotlib.image.imsave(pathlib.Path("tmp/dft.png"), dft, cmap="gray")
        return fshift, dft

    def apply_filter(self):
        try:
            self.info_lbl.configure(text="ĐANG XỬ LÝ")
            self.progress_bar.start()
            fshift, dft = self.get_fshift_and_save_dft()
            plt.clf()
            plt.imshow(Image.open(pathlib.Path("tmp/dft.png")), cmap="gray")
            set_plot_title("Nhấp vào ảnh để chọn điểm. (Nhấn phím bất kỳ để Bắt đầu)")
            plt.waitforbuttonpress()
            set_plot_title(f'Chọn {self.number_of_points.get()} điểm bằng cách nhấp chuột')
            points = np.asarray(plt.ginput(int(self.number_of_points.get()), timeout=-1))     
            plt.close()
            
            # Áp dụng bộ lọc
            if self.select_filter_var.get() == "Lý tưởng":
                IdealNotchFilter().apply_filter(fshift, points, float(self.frequency.get()), pathlib.Path("tmp/filtered_img.png"))
            elif self.select_filter_var.get() == "Butterworth":
                ButterworthNotchFilter().apply_filter(fshift, points, float(self.frequency.get()), pathlib.Path("tmp/filtered_img.png"), order=int(self.butterworth_order.get()))
            elif self.select_filter_var.get() == "Gaussian":
                GaussianNotchFilter().apply_filter(fshift, points, float(self.frequency.get()), pathlib.Path("tmp/filtered_img.png"))
            
            self.info_lbl.configure(text="HOÀN THÀNH")
            self.progress_bar.stop()
            
            # Hiển thị ảnh đã lọc
            filter_img = ImageTk.PhotoImage(ImageOps.grayscale((Image.open(pathlib.Path("tmp/filtered_img.png")))))
            self.filter_img.configure(image=filter_img, text="")
            self.filter_img.image = filter_img
        except Exception as e:
            messagebox.showerror("Đã xảy ra lỗi!", str(e))
            self.info_lbl.configure(text="LỖI")
            self.progress_bar.stop()

    def save_img(self):
        try:
            directory = filedialog.asksaveasfilename(title="Lưu Ảnh", filetypes=[('Ảnh',['*jpeg','*png','*jpg'])])
            if directory:
                Image.open(pathlib.Path("tmp/filtered_img.png")).save(directory)
                messagebox.showinfo("Thành công", "Ảnh đã được lưu thành công!")
        except Exception as e:
            messagebox.showerror("Đã xảy ra lỗi!", str(e))

    def save_dft(self, path, save_path):
        img = ImageOps.grayscale((Image.open(path)))
        img = np.asarray(img)
        f = np.fft.fft2(img)
        fshift = np.fft.fftshift(f)
        dft = 20 * np.log(np.abs(fshift))
        matplotlib.image.imsave(save_path, dft, cmap="gray")

    def show_summary(self):
        f, axarr = plt.subplots(2,2, figsize=(12,10))
        f.suptitle("Tổng quan Bộ lọc Notch", fontsize=16)
        
        axarr[0,0].imshow(Image.open(pathlib.Path("tmp/original_img.png")), cmap="gray")
        axarr[0,0].set_title("Ảnh Gốc")
        
        axarr[0,1].imshow(Image.open(pathlib.Path("tmp/filtered_img.png")), cmap="gray")
        axarr[0,1].set_title("Ảnh đã Lọc")
        
        axarr[1,0].imshow(Image.open(pathlib.Path("tmp/dft.png")), cmap="gray")
        axarr[1,0].set_title("DFT của Ảnh Gốc")
        
        self.save_dft(pathlib.Path("tmp/filtered_img.png"), pathlib.Path("tmp/tdft.png"))
        axarr[1,1].imshow(Image.open(pathlib.Path("tmp/tdft.png")), cmap="gray")
        axarr[1,1].set_title("DFT của Ảnh đã Lọc")
        
        plt.tight_layout()
        plt.show()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    MainApp().run()
