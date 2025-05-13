import cv2
import numpy as np
import pyautogui
import time
import os

TEMPLATE_PATH = 'templates/touch_start.png'

def screenshot(save_path="screen.png"):
    pyautogui.screenshot(save_path)

def match_template(screen_path, template_path, threshold=0.85):
    screen = cv2.imread(screen_path, cv2.IMREAD_GRAYSCALE)
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)

    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
        print(f"Match found with confidence {max_val:.2f}")
        return max_loc
    print(f"No match (confidence {max_val:.2f})")
    return None

def click_image(timeout=15, retry_interval=0.3):
    """
    Keeps trying to find and click the button until timeout (in seconds).
    """
    start_time = time.time()

    while time.time() - start_time < timeout:
        screenshot()
        pos = match_template("screen.png", TEMPLATE_PATH)
        if pos:
            x, y = pos
            pyautogui.moveTo(x + 100, y + 10)  # move out of menu button
            pyautogui.click()
            print("✅ Clicked: Touch to Start")
            return True
        else:
            print("🔁 Button not found, retrying...")
            time.sleep(retry_interval)

    print("⏱️ Timeout: Button not found after waiting.")
    return False


click_image()
