from RPi import GPIO
import time

class Lock:

    def __init__(self, id,  pin_lock, pin_lock_feedback, cb_feedback):
        self.id = id
        self.__pin_lock = pin_lock
        self.__pin_lock_feedback = pin_lock_feedback
        self.__cb = cb_feedback

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.__pin_lock, GPIO.OUT)
        GPIO.setup(self.__pin_lock_feedback, GPIO.IN, GPIO.PUD_UP)

        self.__last_status = self.status
        GPIO.add_event_detect(self.__pin_lock_feedback, GPIO.BOTH, callback=self.__cb_feedback)


    def __cb_feedback(self, pin):
        status = self.status

        if status != self.__last_status:
            self.__cb(self)
            self.__last_status = status


    def open(self):
        GPIO.output(self.__pin_lock, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(self.__pin_lock, GPIO.LOW)


    @property
    def status(self):
        return GPIO.input(self.__pin_lock_feedback)


    def close(self):
        GPIO.cleanup([self.__pin_lock, self.__pin_lock_feedback])