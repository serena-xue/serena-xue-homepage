import os
import requests
from icalendar import Calendar, Event
import sys

# --- 配置 ---
# 从环境变量中获取源日历URL
SOURCE_URL = os.environ.get('SOURCE_CALENDAR_URL')
# 定义要过滤掉的关键词
FILTER_KEYWORD = 'Office Hours'
# 定义输出目录和文件名
OUTPUT_DIR = 'output'
OUTPUT_FILENAME = 'filtered_calendar.ics'
OUTPUT_FILE_PATH = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)


def filter_calendar():
    """
    获取、过滤并保存日历。
    """
    if not SOURCE_URL:
        print("错误：环境变量 SOURCE_CALENDAR_URL 未设置。")
        sys.exit(1)  # 脚本失败并退出

    try:
        # 1. 下载源日历内容
        print(f"正在从 {SOURCE_URL} 获取日历...")
        response = requests.get(SOURCE_URL)
        response.raise_for_status()  # 如果请求失败则抛出异常

        # 2. 解析日历
        source_cal = Calendar.from_ical(response.content)

        # 3. 创建一个新的日历对象
        new_cal = Calendar()

        # 复制源日历的元数据
        for key, value in source_cal.items():
            if key.upper() != 'VEVENT':
                new_cal.add(key, value)

        print("开始过滤事件...")
        event_count = 0
        filtered_count = 0

        # 4. 遍历所有事件并应用过滤规则
        for component in source_cal.walk('VEVENT'):
            event_count += 1

            # --- 本地调试：打印前10个源事件的标题 ---
            if event_count <= 10:
                print(f"[调试] 源事件 {event_count}: {component.get('summary', '没有标题')}")
            # -----------------------------------------

            summary = component.get('summary', '').upper()

            # 如果标题中不包含关键词，则保留该事件
            if FILTER_KEYWORD.upper() not in summary:
                new_cal.add_component(component)
            else:
                filtered_count += 1
                print(f"已过滤事件: {component.get('summary')}")
        print(f"处理完成。总共 {event_count} 个事件，过滤掉 {filtered_count} 个。")

        # 5. 确保输出目录存在
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        # 6. 将新日历写入文件
        with open(OUTPUT_FILE_PATH, 'wb') as f:
            f.write(new_cal.to_ical())
        print(f"已生成新的日历文件: {OUTPUT_FILE_PATH}")

    except requests.exceptions.RequestException as e:
        print(f"获取日历时发生网络错误: {e}")
        sys.exit(1)  # 脚本失败并退出
    except Exception as e:
        print(f"处理日历时发生未知错误: {e}")
        sys.exit(1)  # 脚本失败并退出


if __name__ == "__main__":
    filter_calendar()

