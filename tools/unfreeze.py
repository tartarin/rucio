

f = open('dsns.csv')
dsns = [line.rstrip() for line in f.readlines()]
f.close()

for dsn in dsns:
    scope, name = dsn.split(':')
    query = '''UPDATE ATLAS_RUCIO.DIDS SET is_open=1 WHERE scope='%(scope)s' and name='%(name)s' and did_type='D' and  is_open=0;''' % locals()
    print query