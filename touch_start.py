import cv2
import numpy as np
import pyautogui
import time
import os
import pygetwindow as gw
import pyautogui

TEMPLATE_DIR = 'templates'

def screenshot(save_path="screen.png"):
    pyautogui.screenshot(save_path)

def match_template(screen_path, template_path, threshold=0.85):
    screen = cv2.imread(screen_path, cv2.IMREAD_GRAYSCALE)
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)

    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
        print(f"✅ Match found ({template_path}) with confidence {max_val:.2f}")
        return max_loc
    print(f"❌ No match for {template_path} (confidence {max_val:.2f})")
    return None

def click_template(template_name, timeout=15, retry_interval=0.3, offset=(10, 10)):
    path = os.path.join(TEMPLATE_DIR, template_name)
    start_time = time.time()

    while time.time() - start_time < timeout:
        screenshot()
        pos = match_template("screen.png", path)
        if pos:
            x, y = pos
            pyautogui.moveTo(x + offset[0], y + offset[1])
            pyautogui.click()
            print(f"✅ Clicked: {template_name}")
            return True
        print(f"🔁 Retrying {template_name}...")
        time.sleep(retry_interval)

    print(f"⏱️ Timeout: {template_name} not found.")
    exit(1)

def click_next_button():
    # Find BlueStacks window
    win = None
    for w in gw.getWindowsWithTitle("BlueStacks"):
        if w.visible and w.width > 500:
            win = w
            break

    if not win:
        print("❌ BlueStacks window not found.")
        return

    x, y, w, h = win.left, win.top, win.width, win.height

    # Calculate position relative to window
    target_x = x + 25
    target_y = y + int(h * 0.51)

    print(f"✅ Clicking at ({target_x}, {target_y})")
    pyautogui.moveTo(target_x, target_y)
    pyautogui.click()
    time.sleep(1)

def run_schedule():
    
    schale_office_path = os.path.join(TEMPLATE_DIR, "schale_office_in_schedule.png")
    schale_office_visited = False

    # Schale office initial visit
    while True:
        screenshot()
        pos = match_template("screen.png", schale_office_path)
        if pos:
            schale_office_visited = True
            break
        else:
            print("schale office not found")





# === Run automation sequence ===
#click_template("touch_to_start.png", offset=(100, 10))       # avoid menu
#click_template("exit_announcements.png")
#click_template("cafe_icon.png")
#click_template("cafe_collect.png")
#click_template("cafe_collect_confirm.png")
#click_template("cafe_collect_touch.png")
#click_template("cafe_collect_x.png")
#click_template("cafe_back.png")
#click_template("schedule_icon.png")
#click_template("schale_office.png")
#click_template("schedule_icon.png")

#run_schedule()
