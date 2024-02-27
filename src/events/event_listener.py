from apscheduler.events import JobEvent


class EventListener:
    @staticmethod
    def listen(event: JobEvent):
        if event.exception:
            print('The job crashed :(')
        else:
            print(event.retval)
            # for d in dir(event):
            #     try:
            #         print(event.__class__.__dict__)
            #     except Exception as e:
            #         print('Cannot print')
