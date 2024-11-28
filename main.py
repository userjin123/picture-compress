import os
import tkinter as tk
from tkinter import ttk, filedialog
from threading import Thread
import cv2
import numpy as np
import logging

# 日志设置
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")


def select_path(entry):
    """选择文件夹路径"""
    path = filedialog.askdirectory()
    if path:
        entry.delete(0, "end")
        entry.insert("end", path)


def pic_compress(pic_path, out_path, target_size, quality=90, step=5):
    """图片压缩"""
    with open(pic_path, 'rb') as f:
        pic_byte = f.read()

    img_np = np.frombuffer(pic_byte, np.uint8)
    img_cv = cv2.imdecode(img_np, cv2.IMREAD_ANYCOLOR)

    current_size = len(pic_byte) / 1024
    while current_size > target_size and quality > 0:
        _, pic_byte = cv2.imencode('.jpg', img_cv, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
        quality -= step
        current_size = len(pic_byte) / 1024

    with open(out_path, 'wb') as f:
        f.write(pic_byte)

    return current_size


class CompressApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("图片批量压缩")
        self.window.geometry("600x400")
        self.window.resizable(False, False)

        # 输入路径
        tk.Label(self.window, text="图片文件夹：").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.input_path = tk.Entry(self.window, width=50)
        self.input_path.grid(row=0, column=1, padx=10, pady=10)
        tk.Button(self.window, text=" 选 择 ", command=lambda: select_path(self.input_path)).grid(row=0, column=2, padx=10)

        # 输出路径
        tk.Label(self.window, text="保存文件夹：").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.output_path = tk.Entry(self.window, width=50)
        self.output_path.grid(row=1, column=1, padx=10, pady=10)
        tk.Button(self.window, text=" 选 择 ", command=lambda: select_path(self.output_path)).grid(row=1, column=2, padx=10)

        # 目标大小
        tk.Label(self.window, text="目标大小 (KB)：").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.target_size = tk.Entry(self.window, width=10)
        self.target_size.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        tk.Label(self.window, text="若保存文件夹不存在，则自动创建").grid(row=2, column=1, padx=10, pady=10, sticky="e")

        # 压缩按钮
        self.compress_btn = tk.Button(self.window, text="开始压缩", command=self.start_compression)
        self.compress_btn.grid(row=3, column=1, pady=10)

        # 日志框
        tk.Label(self.window, text="日志：").grid(row=4, column=0, padx=10, pady=10, sticky="nw")
        self.log_text = tk.Text(self.window, height=10, width=60, state="disabled")
        self.log_text.grid(row=4, column=1, columnspan=2, padx=10, pady=10)

    def log_message(self, message):
        """向日志框输出信息"""
        self.log_text.config(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def compress_images(self, input_path, output_path, max_size):
        """批量压缩图片"""
        try:
            max_size = int(max_size)
        except ValueError:
            self.log_message("错误：请输入正确的目标大小！")
            return

        if not os.path.exists(input_path):
            self.log_message("错误：图片文件夹不存在！")
            return
        if not os.path.exists(output_path):
            self.log_message("错误：保存文件夹不存在！")
            return

        files = os.listdir(input_path)
        images = [f for f in files if f.lower().endswith(('jpg', 'jpeg', 'png'))]
        if not images:
            self.log_message("错误：没有找到支持的图片文件！")
            return

        self.log_message(f"开始压缩，共有 {len(images)} 张图片。")
        for i, img in enumerate(images, 1):
            try:
                img_path = os.path.join(input_path, img)
                out_path = os.path.join(output_path, img)
                compressed_size = pic_compress(img_path, out_path, target_size=max_size)
                self.log_message(f"[{i}/{len(images)}]  压缩完成，大小：{compressed_size:.2f} KB")
            except Exception as e:
                self.log_message(f"[{i}/{len(images)}]  压缩失败：{e}")

        self.log_message("所有图片压缩完成！")

    def start_compression(self):
        """开始压缩任务（多线程）"""
        input_path = self.input_path.get()
        output_path = self.output_path.get()
        max_size = self.target_size.get()
        if not os.path.exists(output_path):
            # 如果路径不存在，则创建文件夹
            os.makedirs(output_path)
            print(f"保存文件夹不存在，创建该文件夹")

        self.compress_btn.config(state="disabled")
        Thread(target=self.compress_images, args=(input_path, output_path, max_size), daemon=True).start()
        self.compress_btn.config(state="normal")

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    app = CompressApp()
    app.run()
