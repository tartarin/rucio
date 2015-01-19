
from dogpile.cache import make_region

from rucio.core.rse import list_rses, get_rse_protocols

rse_region = make_region().configure(
    'dogpile.cache.memcached',  # 'dogpile.cache.memory'
    expiration_time=1,
    arguments={'url': "127.0.0.1:11211", 'distributed_lock': True},
)


if __name__ == '__main__':

    for rse in list_rses():
        rse_info = get_rse_protocols(rse['rse'])
        print rse['rse'], rse_info
        rse_region.set(str(rse['rse']), rse_info)
        # rse_region.delete(str(rse['rse']))

