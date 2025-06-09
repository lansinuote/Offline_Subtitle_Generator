import tkinter as tk
from tkinter import filedialog
import os
import threading
import traceback
from transcribe import transcribe

# 创建主窗口
root = tk.Tk()
root.title('音频转字幕')
root.geometry('600x500')  # 调整窗口尺寸

# 创建一个框架,用于放置输入框和按钮
frame = tk.Frame(root)
frame.pack(padx=10, pady=10, fill=tk.X)

# 添加文件选择框标题
file_title_label = tk.Label(frame, text='请选择音频/视频文件:')
file_title_label.grid(row=0, column=0, padx=5, sticky='w')

# 创建输入框,用来显示和输入文件路径
file_path_entry = tk.Entry(frame)
file_path_entry.grid(row=0, column=1, padx=5, sticky='ew')  # 使输入框自适应宽度
frame.grid_columnconfigure(1, weight=1)  # 让第二列（输入框）自适应宽度

# 创建选择文件按钮
def select_file():
    audio_file_path = filedialog.askopenfilename()  # 打开文件对话框
    if audio_file_path:  # 如果选择了文件
        file_path_entry.delete(0, tk.END)  # 清空输入框
        file_path_entry.insert(0, audio_file_path)  # 将文件路径插入到输入框
        log_message('选择的文件路径: %s' % audio_file_path)
    else:
        log_message('没有选择文件.请重新选择音频文件.')  # 如果用户取消选择,记录提示信息

select_button = tk.Button(frame, text='选择文件', command=select_file)
select_button.grid(row=0, column=2, padx=5, sticky='w')  # 使用grid放置按钮

# 添加处理间隔的输入框
interval_label = tk.Label(frame, text='处理间隔（秒）:')
interval_label.grid(row=1, column=0, padx=5, sticky='w')

interval_entry = tk.Entry(frame)
interval_entry.insert(0, '120')  # 默认值120秒
interval_entry.grid(row=1, column=1, padx=5, sticky='ew')

# 添加每条字幕最大字数的输入框
max_length_label = tk.Label(frame, text='每条字幕最大字数:')
max_length_label.grid(row=2, column=0, padx=5, sticky='w')

max_length_entry = tk.Entry(frame)
max_length_entry.insert(0, '35')  # 默认最大字数为35
max_length_entry.grid(row=2, column=1, padx=5, sticky='ew')

# 创建开始转录按钮
transcribe_button = tk.Button(frame, text='开始转录', command=lambda: threading.Thread(target=transcribe_audio, daemon=True).start())
transcribe_button.grid(row=0, column=3, padx=5, sticky='w')  # 放置在‘选择文件’按钮的右边

# 信息按钮
def show_info():
    log_message("这个程序是由 蓝斯诺特 制作的.感谢使用!")
    log_message("别忘了关注我的B站:https://space.bilibili.com/7877324")
    log_message("别忘了关注我的github:https://github.com/lansinuote")
    log_message("这个程序发布在: https://github.com/lansinuote/Offline_Subtitle_Generator")

info_button = tk.Button(frame, text="信息", command=show_info)
info_button.grid(row=2, column=2, padx=5, sticky='w')

# 音频转录并生成 SRT 文件
def transcribe_audio():

    audio_file_path = file_path_entry.get()  # 获取输入框中的路径
    if not audio_file_path:
        log_message('请先选择一个音频文件!')
        return

    if not os.path.exists(audio_file_path):
        log_message('选择的文件不存在!')
        return

    # 获取用户设置的音频处理间隔时间
    try:
        chunk_duration_sec = int(interval_entry.get())  # 获取输入框的值
    except ValueError:
        log_message('请输入有效的数字作为处理间隔!')
        return

    # 获取用户设置的最大字幕字数
    try:
        one_line_max_length = int(max_length_entry.get())  # 获取最大字数
    except ValueError:
        log_message('请输入有效的数字作为最大字幕字数!')
        return

    # 禁用按钮,防止多次点击
    transcribe_button.config(state=tk.DISABLED)

    try:
        transcribe(log_message,audio_file_path,chunk_duration_sec,one_line_max_length)
        show_info()
    except Exception as e:
        log_message('转录失败: %s' % str(e))
        log_message(traceback.format_exc())
    
    finally:
        # 启用按钮
        transcribe_button.config(state=tk.NORMAL)

# 格式化时间戳
def format_timestamp(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return '%02d:%02d:%02d,%03d' % (h, m, s, ms)

# 创建一个框架,用于放置日志标题、文本框和滚动条
log_frame = tk.Frame(root)
log_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# 添加日志框标题
log_title_label = tk.Label(log_frame, text='日志输出:')
log_title_label.pack(anchor='w', padx=5)

# 创建滚动条
scrollbar = tk.Scrollbar(log_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# 创建一个文本框,用于输出日志
log_text = tk.Text(log_frame, wrap=tk.WORD, state=tk.DISABLED, yscrollcommand=scrollbar.set)
log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# 将滚动条与文本框关联
scrollbar.config(command=log_text.yview)

# 日志输出函数
def log_message(message):
    log_text.config(state=tk.NORMAL)  # 启用编辑
    log_text.insert(tk.END, message + '\n')  # 插入日志信息
    log_text.yview(tk.END)  # 自动滚动到底部
    log_text.config(state=tk.DISABLED)  # 禁止编辑
    print(message)

# 启动主循环
root.mainloop()