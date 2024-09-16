import cv2
from cvzone.HandTrackingModule import HandDetector


# Constants
WIDTH, HEIGHT = 1280, 1080
BUTTON_WIDTH, BUTTON_HEIGHT = 100, 100
BUTTON_SPACING = 10
EQUATION_FONT_SIZE = 3
EQUATION_FONT_COLOR = (0, 0, 0)


class Calculator:
    def __init__(self, pos, width, height, value):
        self.pos = pos
        self.width = width
        self.height = height
        self.value = value

    def draw_button(self, img):
        cv2.rectangle(img, self.pos, (self.pos[0] + self.width, self.pos[1] + self.height),
                      (125, 125, 225), cv2.FILLED)
        cv2.rectangle(img, self.pos, (self.pos[0] + self.width, self.pos[1] + self.height),
                      (50, 50, 50), 3)
        cv2.putText(img, self.value, (self.pos[0] + 30, self.pos[1] + 70), cv2.FONT_HERSHEY_PLAIN,
                    2, (50, 50, 50), 2)

    def click(self, x, y, img):
        if self.pos[0] < x < self.pos[0] + self.width and \
                self.pos[1] < y < self.pos[1] + self.height:
            cv2.rectangle(img, (self.pos[0] + 3, self.pos[1] + 3),
                          (self.pos[0] + self.width - 3, self.pos[1] + self.height - 3),
                          (255, 255, 255), cv2.FILLED)
            cv2.putText(img, self.value, (self.pos[0] + 25, self.pos[1] + 80), cv2.FONT_HERSHEY_PLAIN,
                        5, (0, 0, 0), 5)
            return True
        return False


def create_buttons():
    buttons = [['7', '8', '9', 'C'],
               ['4', '5', '6', '*'],
               ['1', '2', '3', '+'],
               ['0', '-', '/', '='],
               ['(', ')', '.', 'del']]
    button_list = []
    for x in range(4):
        for y in range(5):
            xpos = x * (BUTTON_WIDTH + BUTTON_SPACING) + 700
            ypos = y * (BUTTON_HEIGHT + BUTTON_SPACING) + 100
            button_list.append(Calculator((xpos, ypos), BUTTON_WIDTH, BUTTON_HEIGHT, buttons[y][x]))
    return button_list


def main():

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(3, WIDTH)
    cap.set(4, HEIGHT)
    detector = HandDetector(detectionCon=0.9, maxHands=1)

    button_list = create_buttons()
    equation = ''
    counter = 0

    while True:
        success, img = cap.read()
        if not success:
            print("Failed to capture image")
            continue

        img = cv2.flip(img, 1)
        hands, img = detector.findHands(img)

        for button in button_list:
            button.draw_button(img)

        if hands:
            lm_list = hands[0]['lmList']
            if len(lm_list) >= 21:  # Ensure there are enough landmarks
                length, _, img = detector.findDistance(lm_list[8][:2], lm_list[12][:2], img)
                x, y = lm_list[8][:2]

                if length < 50 and counter == 0:
                    for i, button in enumerate(button_list):
                        if button.click(x, y, img):
                            my_value = button.value
                            if my_value == '=':
                                try:
                                    equation = str(eval(equation))
                                except Exception:
                                    print("Syntax Error")
                                    equation = 'Syntax Error'
                            elif equation == 'Syntax Error':
                                equation = ''
                            elif my_value == 'C':
                                equation = ''
                            elif my_value == 'del':
                                equation = equation[:-1]
                            else:
                                equation += my_value
                            counter = 1

        if counter != 0:
            counter += 1
            if counter > 10:
                counter = 0

        cv2.rectangle(img, (700, 20), (1100, 100),
                      (175, 125, 155), cv2.FILLED)
        cv2.rectangle(img, (700, 20), (1100, 100),
                      (50, 50, 50), 3)
        cv2.putText(img, equation, (710, 80), cv2.FONT_HERSHEY_PLAIN,
                    EQUATION_FONT_SIZE, EQUATION_FONT_COLOR, 3)
        cv2.putText(img, '', (50, 50), cv2.FONT_HERSHEY_PLAIN,
                    3, (0, 0, 0), 3)

        cv2.imshow("Virtual Calculator", img)
        cv2.moveWindow("Virtual Calculator", 0, 0)

        if cv2.waitKey(10) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
