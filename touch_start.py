import cv2
import numpy as np
import pyautogui
import time
import os
import pygetwindow as gw
from datetime import datetime

TEMPLATE_DIR = 'templates'
DAY_MOD3 = datetime.now().day % 3

# Get screen size using pyautogui
screen_width, screen_height = pyautogui.size()

def screenshot(save_path="screen.png"):
    pyautogui.screenshot("screen.png", region=(0, 0, screen_width, screen_height))

def match_template(screen_path, template_name, threshold=0.85):
    # Move mouse pointer away
    pyautogui.moveTo(10, 10)
    screenshot()
    template_path = os.path.join(TEMPLATE_DIR, template_name)
    screen = cv2.imread(screen_path, cv2.IMREAD_COLOR)
    template = cv2.imread(template_path, cv2.IMREAD_COLOR)

    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
        print(f"✅ Match found ({template_path}) with confidence {max_val:.2f}")
        return max_loc
    print(f"❌ No match for {template_path} (confidence {max_val:.2f})")
    return None

def click_template(template_name, timeout=15, retry_interval=0.3, offset=(10, 10), linger=True, threshold=0.85):
    start_time = time.time()

    while time.time() - start_time < timeout:
        pos = match_template("screen.png", template_name, threshold=threshold)
        if pos:
            x, y = pos
            pyautogui.moveTo(x + offset[0], y + offset[1])
            pyautogui.click()
            print(f"✅ Clicked: {template_name}")

            if not linger:  # It should not linger
                time.sleep(2)
                while match_template("screen.png", template_name, threshold=threshold):
                    pyautogui.moveTo(x + offset[0], y + offset[1])
                    pyautogui.click()
                    time.sleep(1)
                    
            return True
        print(f"🔁 Retrying {template_name}...")
        time.sleep(retry_interval)
        screenshot()

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
    schale_office_path = "schedule_schale_office_location.png"
    schale_ticket_available = "schedule_ticket_0.png"
 
 
    def _actually_run_schedule():
        accepted_schedule, _ = _schedule_in_location()
        for x, y in reversed(accepted_schedule):  # Reverse so we get purple books first
            if match_template("screen.png", schale_ticket_available, 0.95):
                print("Ticket empty")
                # To exit all schedule
                click_template("schedule_all_schedule.png")
                time.sleep(1)
                return
            while not match_template("screen.png", "schedule_start_schedule.png"):
                # click schedule
                pyautogui.moveTo(x + 10, y + 10)
                pyautogui.click()
                pyautogui.sleep(1)

            # run schedule
            click_template("schedule_start_schedule.png")
            time.sleep(1)

            while True:
                # 인연 랭크 업
                if match_template("screen.png", "heart_rank_up.png"):
                    click_template("heart_rank_up.png")
                confirm_pos = match_template("screen.png", "schedule_confirm.png", threshold=0.85)
                
                if confirm_pos:
                    x, y = confirm_pos
                    pyautogui.moveTo(x + 10, y + 10)
                    pyautogui.click()
                    print("✅ Confirmed schedule.")
                    time.sleep(1)
                    break
                
                pyautogui.click()  # click in place to advance
                time.sleep(1)

        # To exit all schedule
        click_template("schedule_all_schedule.png")
        time.sleep(1)


    # Optimal Runs
    _actually_run_schedule()

    click_next_button()
    time.sleep(2)
    screenshot()

    # optimal runs for all locations
    while not match_template("screen.png", schale_office_path):
        if match_template("screen.png", schale_ticket_available, 0.95):
            print("Ticket empty")
            return

        # Optimal Runs
        _actually_run_schedule()

        click_next_button()
        time.sleep(2)
        screenshot()

    print("Optimal run finished.")

    while not match_template("screen.png", schale_ticket_available, 0.95):
        _, all_slots = _schedule_in_location()

        for x, y, num_hearts in all_slots:
            if match_template("screen.png", schale_ticket_available, 0.95):
                print("Ticket empty")
                # To exit all schedule
                click_template("schedule_all_schedule.png")
                time.sleep(1)
                return
            if num_hearts >= 2:
                # click schedule
                pyautogui.moveTo(x + 10, y + 10)
                pyautogui.click()
                pyautogui.sleep(1)

                # run schedule
                click_template("schedule_start_schedule.png")
                time.sleep(1)

                while True:
                    if match_template("screen.png", "heart_rank_up.png"):
                        click_template("heart_rank_up.png")
                    confirm_pos = match_template("screen.png", "schedule_confirm.png", threshold=0.85)
                    
                    if confirm_pos:
                        x, y = confirm_pos
                        pyautogui.moveTo(x + 10, y + 10)
                        pyautogui.click()
                        print("✅ Confirmed schedule.")
                        time.sleep(1)
                        break
                    
                    pyautogui.click()  # click in place to advance
                    time.sleep(1)
        
        # To exit all schedule
        click_template("schedule_all_schedule.png")
        time.sleep(1)

        click_next_button()
        time.sleep(2)
        screenshot()

def _schedule_in_location():
    # File paths
    SCREEN_PATH = "screen.png"
    LABEL_PATH = "templates/schedule_attending_students.png"
    HEART_PATH = "templates/schedule_heart.png"

    # Offsets for bounding box relative to label position
    OFFSET_TOP = 0
    OFFSET_BOTTOM = 60
    OFFSET_LEFT = 0
    OFFSET_RIGHT = 330
    MATCH_THRESHOLD = 0.85

    click_template("schedule_all_schedule.png")
    time.sleep(2)

    screenshot()
    
    # Load images
    screen = cv2.imread(SCREEN_PATH)
    label = cv2.imread(LABEL_PATH)
    heart_template = cv2.imread(HEART_PATH)

    #screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
    #label_gray = cv2.cvtColor(label, cv2.COLOR_BGR2GRAY)

    # Step 1: Match labels to find slot anchors
    res = cv2.matchTemplate(screen, label, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= MATCH_THRESHOLD)
    points = list(zip(*loc[::-1]))  # (x, y)

    # Step 2: Sort the schedule boxes row-wise
    points = sorted(points, key=lambda p: (p[1] // 100, p[0]))

    def count_hearts_in_slot(slot_img, heart_template, threshold=0.85):
        #slot_gray = cv2.cvtColor(slot_img, cv2.COLOR_BGR2GRAY)
        #heart_gray = cv2.cvtColor(heart_template, cv2.IMREAD_GRAYSCALE)

        result = cv2.matchTemplate(slot_img, heart_template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(result >= threshold)
        points = list(zip(*loc[::-1]))

        # Remove near-duplicates (within 5px of each other)
        filtered = []
        for pt in points:
            if all(abs(pt[0] - fx) > 5 or abs(pt[1] - fy) > 5 for fx, fy in filtered):
                filtered.append(pt)

        return len(filtered)

    # Step 3: Check each slot and collect valid ones
    accepted_slots = []
    slots_total = len(points)

    all_slots = []

    for idx, (x, y) in enumerate(points):
        x1 = x + OFFSET_LEFT
        y1 = y + OFFSET_TOP
        x2 = x + OFFSET_RIGHT
        y2 = y + OFFSET_BOTTOM

        slot_img = screen[y1:y2, x1:x2]
        heart_count = count_hearts_in_slot(slot_img, heart_template)
        all_slots.append((x1, y1, heart_count))

        print(f"Slot {idx+1}/{slots_total}: {heart_count} hearts")

        if idx in [4, 5] and heart_count >= 3:
            print(f"✅ Matched slot {idx} (last 2, {heart_count} hearts)")
            accepted_slots.append((x1, y1))
        elif idx >= 6 and heart_count >= 2:
            print(f"✅ Matched slot {idx} (last 3~4, {heart_count} hearts)")
            accepted_slots.append((x1, y1))

    if not accepted_slots:
        print("⚠️ No optimal slot found.")

    return accepted_slots, all_slots


def do_startup():
    click_template("touch_to_start.png", offset=(100, 10), linger=False) 
    time.sleep(15)
    click_template("daily_check_in.png", linger=False) 
    time.sleep(3)
    click_template("exit_announcements.png", linger=False)
    time.sleep(2)
    click_template("monthly_check_in.png", offset=(300, 300), linger=False) 
    time.sleep(4)
    if match_template("screen.png", "social_confirm.png", 0.95):
        click_template("social_confirm.png", linger=False)

def do_ap_overflow():
    if match_template("screen.png", "notification.png", 0.95):
        click_template("social_confirm.png", linger=False)
    
def do_cafe():
    # Need to implement student nadenade feature
    click_template("cafe_icon.png", linger=False) 
    time.sleep(5)
    click_template("cafe_visited_students.png")
    time.sleep(2)
    click_template("cafe_visited_students_exit.png", linger=False) 
    time.sleep(2)
    click_template("cafe_collect.png")
    time.sleep(2)
    click_template("cafe_collect_confirm.png")
    time.sleep(2)
    click_template("cafe_collect_touch.png")
    time.sleep(2)
    do_ap_overflow()
    time.sleep(2)
    click_template("cafe_collect_x.png", linger=False)  
    time.sleep(2)
    click_template("cafe_back.png")
    time.sleep(8)

def do_schedule():
    click_template("schedule_icon.png", linger=False) 
    time.sleep(5)
    click_template("schedule_schale_office.png", linger=False)  
    time.sleep(2)
    run_schedule()
    click_template("cafe_back.png", linger=False)  
    time.sleep(5)

def do_social():
    click_template("social_icon.png", linger=False, threshold=0.95)  
    time.sleep(2)
    click_template("social_circle.png")
    time.sleep(4)
    click_template("social_confirm.png")
    time.sleep(2)
    click_template("cafe_back.png")
    time.sleep(5)

def do_create():
    click_template("create_icon.png", linger=False) 
    time.sleep(5)
    click_template("create_receive.png")
    time.sleep(2)
    click_template("create_touch.png")
    time.sleep(2)
    click_template("create_quick.png")
    time.sleep(2)
    click_template("create_start.png")
    time.sleep(2)
    click_template("social_confirm.png")
    time.sleep(2)
    click_template("cafe_back.png")
    time.sleep(5)

def do_mission():
    click_template("mission_icon.png", linger=False)  
    time.sleep(5)
    click_template("mission_receive_all.png")
    time.sleep(2)
    do_ap_overflow()
    time.sleep(2)
    click_template("mission_touch.png")
    time.sleep(2)
    click_template("cafe_back.png")
    time.sleep(5)

def do_market():
    click_template("market_icon.png", linger=False) 
    time.sleep(5)
    click_template("market_pvp.png")
    time.sleep(2)
    click_template("market_30ap.png")
    time.sleep(2)
    click_template("market_60ap.png")
    time.sleep(2)
    click_template("market_select_buy.png")
    time.sleep(2)
    click_template("confirm_yellow.png")
    time.sleep(3)
    click_template("market_touch.png", linger=False) 
    time.sleep(2)
    do_ap_overflow()
    time.sleep(2)
    click_template("cafe_back.png")
    time.sleep(5)

def do_work():
    click_template("work_icon.png")
    time.sleep(5)
    #_do_wanted()
    _do_exchange()
    _do_pvp()

    click_template("cafe_back.png")
    time.sleep(2)

# 현상수배
def _do_wanted():
    click_template("wanted_icon.png")
    time.sleep(2)
    match DAY_MOD3:
        case 0:
            click_template("wanted_highway.png")
        case 1:
            click_template("wanted_desert_railroad.png")
        case 2:
            click_template("wanted_classroom.png")
    time.sleep(2)

    # File paths
    LABEL_PATH = "templates/wanted_enter.png"

    screenshot()

    # Load images
    screen = cv2.imread("screen.png")
    label = cv2.imread(LABEL_PATH)
    screenshot()
    res = cv2.matchTemplate(screen, label, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= 0.85)
    points = list(zip(*loc[::-1]))  # (x, y)
    points = sorted(points, key=lambda p: (p[1] // 100, p[0]))

    last_point = points[-1]
    x, y = last_point

    pyautogui.moveTo(x + 10, y + 10)
    pyautogui.click()
    pyautogui.sleep(1)

    click_template("sweep_max.png")
    time.sleep(1)
    click_template("sweep_start.png", linger=False)
    time.sleep(2)
    click_template("social_confirm.png")
    time.sleep(2)
    click_template("skip.png")
    time.sleep(2)
    click_template("wanted_confirm.png", linger=False)
    time.sleep(2)
    click_template("cafe_collect_x.png")
    time.sleep(2)
    click_template("cafe_back.png")
    time.sleep(2)
    click_template("cafe_back.png")
    time.sleep(2)
    
# 학원교류회
def _do_exchange():
    click_template("exchange_icon.png")
    time.sleep(5)

    match DAY_MOD3:
        case 0:
            click_template("exchange_trinity.png")
        case 1:
            click_template("exchange_ghehenna.png")
        case 2:
            click_template("exchange_millennium.png")
    time.sleep(2)

    # File paths
    LABEL_PATH = "templates/wanted_enter.png"

    screenshot()

    # Load images
    screen = cv2.imread("screen.png")
    label = cv2.imread(LABEL_PATH)
    screenshot()
    res = cv2.matchTemplate(screen, label, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= 0.85)
    points = list(zip(*loc[::-1]))  # (x, y)
    points = sorted(points, key=lambda p: (p[1] // 100, p[0]))

    last_point = points[-1]
    x, y = last_point

    pyautogui.moveTo(x + 10, y + 10)
    pyautogui.click()
    pyautogui.sleep(1)

    click_template("sweep_max.png")
    time.sleep(1)
    click_template("sweep_start.png", linger=False)
    time.sleep(2)
    click_template("social_confirm.png")
    time.sleep(2)
    click_template("skip.png")
    time.sleep(2)
    click_template("wanted_confirm.png", linger=False)
    time.sleep(2)
    click_template("cafe_collect_x.png")
    time.sleep(2)
    click_template("cafe_back.png")
    time.sleep(2)
    click_template("cafe_back.png")
    time.sleep(2)

def _do_pvp():
    click_template("pvp_icon.png")
    time.sleep(5)
    click_template("pvp_receive.png", threshold=0.95)
    time.sleep(2)
    click_template("pvp_touch.png", linger=False)
    time.sleep(2)
    click_template("pvp_receive2.png", threshold=0.95)
    time.sleep(2)
    click_template("pvp_touch.png", linger=False)
    time.sleep(2)
    click_template("pvp_reset.png", offset=(0,100))
    time.sleep(2)
    click_template("pvp_attack_setup.png", linger=False)
    time.sleep(2)
    click_template("pvp_sally.png", linger=False)
    time.sleep(2)
    click_template("social_confirm.png", linger=False)
    time.sleep(2)
    click_template("cafe_back.png")
    time.sleep(2)


if __name__ == "__main__":
    do_startup()
    do_work()
    do_cafe()
    do_schedule()
    do_social()
    do_create()
    do_market()
    do_mission()
    
