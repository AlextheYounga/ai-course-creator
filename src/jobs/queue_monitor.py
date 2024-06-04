import json
from termcolor import colored


class QueueMonitor():
    def __init__(self, job_queue, redis_client):
        self.job_queue = job_queue
        self.redis = redis_client
        self.queue_index = 0
        self.total_items = 0
        self.increment = 0

    increment_events = [
        'LessonPageProcessedAndSummarizedSuccessfully',
    ]

    def read_completed_queue(self):
        queue_length = self.job_queue.queue.length(self.job_queue.completed_queue) > 0
        index_lookup = queue_length - 1 if queue_length > 0 else 0
        queue_items = self.redis.lrange(self.job_queue.completed_queue, self.queue_index, index_lookup)
        self.queue_index = index_lookup

        return queue_items


    def update_progress(self):
        queue_items = self.read_completed_queue()
        if not queue_items: return

        for queue_item in queue_items:
            item = json.loads(queue_item)
            event_name = item['data']['eventName']
            event_data = item['data']['eventData']

            self.total_items = event_data.get('totalJobItems', self.total_items)
            if self.increment == 0:
                self.increment = event_data.get('completedJobItems', self.increment)

            print_color = "green" if not "Fail" in event_name else "red"

            if self.total_items == 0:
                message_data = ['Calculating...', f'Event: {event_name}']
                print(colored("{: >20} {: >20}".format(*message_data), print_color))
                continue

            if event_name in self.increment_events:
                self.increment = self.increment + 1

            page_id = event_data.get('pageId', "N/A")
            progress = self.increment / self.total_items * 100
            message_data = [
                f"{progress:.2f}%",
                f"Page: {self.increment}/{self.total_items}",
                f"Page ID: {page_id}",
                f"\tEvent: {event_name}"
            ]

            print(colored("{: >10} {: >20} {: >20} {: >20}".format(*message_data), print_color))
