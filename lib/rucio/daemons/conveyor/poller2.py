

import traceback
import threading


from time import time, sleep

from rucio.core import request as request_core
from rucio.common.utils import chunks
from rucio.daemons.conveyor import common
from rucio.db.constants import RequestState, RequestType
from rucio.transfertool import fts3

graceful_stop = threading.Event()


def poller(worker_number=1, total_workers=1, chunk_size=100):

    print '%(worker_number)s / %(total_workers)s: Poller started' % locals()
    while not graceful_stop.is_set():
        try:
            s = time()
            transfer_requests = request_core.get_next(request_type=[RequestType.TRANSFER, RequestType.STAGEIN, RequestType.STAGEOUT],
                                                      state=RequestState.SUBMITTED,
                                                      thread=worker_number,
                                                      total_threads=total_workers,
                                                      limit=10000)
            n = len(transfer_requests)
            print '%(worker_number)s / %(total_workers)s: get_next %(n)s requests' % locals()

            if not transfer_requests:
                sleep(0.01)
                continue

            for chunk in chunks(transfer_requests, chunk_size):
                try:
                    s = time()
                    fts3.query_all(transfer_requests=chunk)
                    print 'fts3.query_all', time() - s
                    s = time()
                    common.update_requests_states(chunk)
                    print 'update_requests_states', time() - s
                except:
                    print traceback.format_exc()

        except:
            print traceback.format_exc()


def stop(signum=None, frame=None):
    """
    Graceful exit.
    """
    graceful_stop.set()


def run(total_workers=1, chunk_size=10):
    print 'main: starting processes'

    threads = list()
    for i in xrange(0, total_workers):
        kwargs = {'worker_number': i,
                  'total_workers': total_workers,
                  'chunk_size': chunk_size}
        threads.append(threading.Thread(target=poller, kwargs=kwargs))
    [t.start() for t in threads]
    while threads[0].is_alive():
        [t.join(timeout=3.14) for t in threads]


if __name__ == '__main__':
    run(total_workers=30, chunk_size=100)
