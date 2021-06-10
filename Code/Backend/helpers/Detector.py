from RPi import GPIO

class Detector:

    def __init__(self, pin_detector, cb_detector):
        self.__pin_detector = pin_detector
        self.__cb = cb_detector
        self.__last_status = False

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.__pin_detector, GPIO.IN)

        GPIO.add_event_detect(pin_detector, GPIO.BOTH, self.__cb_detector)


    def __cb_detector(self, pin):
        status = self.status

        if status != self.__last_status:
            self.__cb(self)
            self.__last_status = status


    @property
    def status(self):
        return GPIO.input(self.__pin_detector)


    def close(self):
        GPIO.cleanup(self.__pin_detector)