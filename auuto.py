import pyautogui
import time

print("移动鼠标到目标位置，按 Ctrl+C 停止程序")

try:
    while True:
        time.sleep(3)
        # 获取当前鼠标坐标
        x, y = pyautogui.position()
        print(f"X: {x}, Y: {y}", end="\n")  # 动态更新坐标
        time.sleep(0.1)  # 每 0.1 秒刷新一次
except KeyboardInterrupt:
    print("\n退出程序")
