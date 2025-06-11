import whisper
import os
from pydub import AudioSegment
import torch
import sys

if hasattr(sys, '_MEIPASS'):
    libs_path = os.path.join(sys._MEIPASS, 'libs')
else:
    libs_path = './libs'

os.environ['PATH'] = libs_path + os.pathsep + os.environ['PATH']

# AudioSegment.converter = os.path.join(os.path.dirname(__file__), 'libs', 'ffmpeg.exe')

# 格式化时间戳
def format_timestamp(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return '%02d:%02d:%02d,%03d' % (h, m, s, ms)

def transcribe(log_message,audio_file_path,chunk_duration_sec,one_line_max_length):
    segment_counter = 1
    subtitle_counter = 1

    if not os.path.exists(audio_file_path):
        log_message('选择的文件不存在!')
        return

    chunk_duration_ms = chunk_duration_sec * 1000  # 转换为毫秒

    # 获取文件名并生成字幕文件
    srt_file_path = audio_file_path + '.srt'

    # 输出所有的参数到日志框
    log_message('音频文件路径: %s' % audio_file_path)
    log_message('处理间隔: %d秒' % chunk_duration_sec)
    log_message('每条字幕最大字数: %d' % one_line_max_length)
    log_message('字幕文件将输出到: %s' % srt_file_path)

    # 清空 SRT 文件内容
    open(srt_file_path, 'w', encoding='utf-8').close()

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    log_message('使用计算设备:%s'%device)

    log_message('正在加载神经网络模型...')
    # 强制使用CPU
    model_path = os.path.join(os.path.dirname(__file__), 'libs', 'large-v3-turbo.pt')
    model = whisper.load_model(model_path, device=device)  # 加载模型
    log_message('神经网络模型加载完成!')

    # 加载音频文件并按时间分割
    log_message('正在加载音频文件...')
    audio = AudioSegment.from_file(audio_file_path)
    duration_ms = len(audio)  # 获取音频总时长（毫秒）

    total_chunks = duration_ms // chunk_duration_ms + (1 if duration_ms % chunk_duration_ms > 0 else 0)  # 计算总段数

    log_message('音频文件加载完成!音频总时长:%d秒,将分成 %d 段处理.' % (duration_ms / 1000, total_chunks))

    # 记录上一个段落的结束时间
    last_end_time = 0

    for start_ms in range(0, duration_ms, chunk_duration_ms):
        end_ms = start_ms + chunk_duration_ms

        if end_ms > duration_ms:
            end_ms = duration_ms

        # 计算当前段落的持续时间（秒）
        log_message('正在处理时间段 %d: %ds --> %ds' % (segment_counter,start_ms/1000,end_ms/1000))

        if end_ms - start_ms < 1000:
            log_message('持续时间过短, 放弃处理')
            continue

        chunk = audio[start_ms:end_ms]
        chunk_file_path = os.path.join(os.path.dirname(audio_file_path),'chunk_%d.wav'%segment_counter)
        chunk.export(chunk_file_path, format='wav')  # 导出当前段落为 WAV 文件

        # 逐段转录
        transcript = model.transcribe(chunk_file_path)

        for segment in transcript['segments']:
            #segment -> {'start': 3.7, 'end': 7.38, 'text': '那么所谓强化学习呢就是我们有一个机器人'}
            # 使用累加的时间段,确保时间是连续的
            start = segment['start'] + start_ms/1000
            end = segment['end'] + start_ms/1000

            if start > end_ms/1000:
                start = end_ms/1000

            if end > end_ms/1000:
                end = end_ms/1000

            text = segment['text'].strip()

            # 确保每条字幕的字数不超过最大字数
            split_count = len(text) // one_line_max_length + 1

            for i in range(split_count):
                split_duration = (end - start) / split_count

                split_start = format_timestamp(start + split_duration * i)
                split_end = format_timestamp(start + split_duration * (i + 1))
                split_text = text[one_line_max_length*i:one_line_max_length*(i+1)].strip()

                if not split_text:
                    continue

                with open(srt_file_path, 'a', encoding='utf-8') as f:
                    f.write('%d\n' % subtitle_counter)
                    f.write('%s --> %s\n' % (split_start, split_end))
                    f.write('%s\n\n' % split_text)

                log_message('转录段落 %d: %s --> %s' % (segment_counter, split_start, split_end))
                log_message('转录内容: %s' % (split_text))

                subtitle_counter += 1

        try:
            os.remove(chunk_file_path)
        except Exception as e:
            log_message('删除临时文件 %s 失败, 异常信息: %s , 也许你可以稍后手动删除它.' % (str(e),chunk_file_path))
        segment_counter += 1
        last_end_time += end - last_end_time


    log_message('转录完成!字幕文件保存在:%s' % srt_file_path)