import cv2

from touch_start import _schedule_in_location

def debug_run_schedule_location():
    # Call your detection function
    accepted_coords, all_slots = _schedule_in_location()

    # Reload the screenshot used inside the function
    screen = cv2.imread("screen.png")

    # These should match your function's slot layout
    OFFSET_RIGHT = 330
    OFFSET_BOTTOM = 60

    # Collect slot metadata by re-running heart detection logic
    # You can move this into _schedule_in_location() later for better reuse
    def annotate_slots(accepted_coords, all_slots):
        for idx, (x, y, hearts) in enumerate(all_slots):
            top_left = (x, y)
            bottom_right = (x + OFFSET_RIGHT, y + OFFSET_BOTTOM)

            is_accepted = (x, y) in accepted_coords
            color = (0, 255, 0) if is_accepted else (0, 0, 255)

            # Draw slot rectangle
            cv2.rectangle(screen, top_left, bottom_right, color, 2)

            # Prepare text
            label = f"#{idx+1} : {hearts} hearts"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            thickness = 1

            # Get text size to align right
            (text_w, text_h), _ = cv2.getTextSize(label, font, font_scale, thickness)
            text_x = x + OFFSET_RIGHT - text_w
            text_y = y - 10  # 10px above the box

            cv2.putText(screen, label, (text_x, text_y), font, font_scale, color, thickness)

    # Annotate all slots
    annotate_slots(accepted_coords, all_slots)

    # Show result
    cv2.imshow("Schedule Slot Debug", screen)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    debug_run_schedule_location()
