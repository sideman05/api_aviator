import queue
import signal
import threading

from django.core.management.base import BaseCommand

from api_app import views


class Command(BaseCommand):
    help = 'Run the Aviator monitor worker continuously.'

    def handle(self, *args, **options):
        stop_event = threading.Event()
        work_queue = queue.Queue(maxsize=1000)

        def _stop_worker(signum, frame):
            stop_event.set()

        signal.signal(signal.SIGTERM, _stop_worker)
        signal.signal(signal.SIGINT, _stop_worker)

        views._set_monitor_state(
            running=True,
            started_at=views._local_iso(),
            last_event='Monitor worker booting',
            event_count=0,
        )

        self.stdout.write(self.style.SUCCESS('Monitor worker started'))
        try:
            views._monitor_runner(work_queue, stop_event)
        except Exception as exc:
            views._set_monitor_state(running=False, last_event=f'Monitor worker crashed: {exc}')
            raise
        finally:
            views._set_monitor_state(running=False, last_event='Monitor worker stopped')
            self.stdout.write(self.style.WARNING('Monitor worker stopped'))
