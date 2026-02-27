import pyautogui
import time

def auto_click(interval=5):
    """
    自动点击脚本
    :param interval: 点击间隔时间（秒），默认5秒
    """
    print(f"自动点击脚本已启动，每隔 {interval} 秒点击一次")
    print("按 Ctrl+C 停止脚本")
    print("3秒后开始点击...")
    
    # 给用户3秒时间将鼠标移动到想要点击的位置
    time.sleep(3)
    
    try:
        while True:
            # 获取当前鼠标位置
            x, y = pyautogui.position()
            
            # 执行点击
            pyautogui.click(x, y)
            print(f"点击成功: ({x}, {y})")
            
            # 等待指定间隔
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n脚本已停止")

if __name__ == "__main__":
    # 可以修改这里的数字来调整间隔时间
    auto_click(interval=5)
