#
#
#
# scp -r lib/rucio root@rucio-auth-prod-01.cern.ch:/usr/lib/python2.6/site-packages/.
# scp -r lib/rucio root@rucio-auth-prod-02.cern.ch:/usr/lib/python2.6/site-packages/.
# scp -r lib/rucio root@rucio-daemon-prod-01.cern.ch:/usr/lib/python2.6/site-packages/.
# scp -r lib/rucio root@rucio-daemon-prod-02.cern.ch:/usr/lib/python2.6/site-packages/.
# scp -r lib/rucio root@rucio-daemon-prod-03.cern.ch:/usr/lib/python2.6/site-packages/.
# scp -r lib/rucio root@rucio-daemon-prod-04.cern.ch:/usr/lib/python2.6/site-packages/.
# scp -r lib/rucio root@rucio-daemon-prod-05.cern.ch:/usr/lib/python2.6/site-packages/.
# scp -r lib/rucio root@rucio-daemon-prod-06.cern.ch:/usr/lib/python2.6/site-packages/.
# scp -r lib/rucio root@rucio-daemon-prod-07.cern.ch:/usr/lib/python2.6/site-packages/.
# scp -r lib/rucio root@rucio-daemon-prod-08.cern.ch:/usr/lib/python2.6/site-packages/.
# scp -r lib/rucio root@rucio-daemon-prod-09.cern.ch:/usr/lib/python2.6/site-packages/.
# scp -r lib/rucio root@rucio-daemon-prod-10.cern.ch:/usr/lib/python2.6/site-packages/.
# scp -r lib/rucio root@rucio-daemon-prod-11.cern.ch:/usr/lib/python2.6/site-packages/.
# scp -r lib/rucio root@rucio-daemon-prod-12.cern.ch:/usr/lib/python2.6/site-packages/.
# scp -r lib/rucio root@rucio-daemon-prod-13.cern.ch:/usr/lib/python2.6/site-packages/.
# scp -r lib/rucio root@rucio-daemon-prod-14.cern.ch:/usr/lib/python2.6/site-packages/.
# scp -r lib/rucio root@rucio-daemon-prod-15.cern.ch:/usr/lib/python2.6/site-packages/.
# scp -r lib/rucio root@rucio-daemon-prod-16.cern.ch:/usr/lib/python2.6/site-packages/.
# scp -r lib/rucio root@rucio-daemon-prod-17.cern.ch:/usr/lib/python2.6/site-packages/.
# scp -r lib/rucio root@rucio-daemon-prod-18.cern.ch:/usr/lib/python2.6/site-packages/.
# scp -r lib/rucio root@rucio-redirect-prod-01.cern.ch:/usr/lib/python2.6/site-packages/.
# scp -r lib/rucio root@rucio-server-prod-01.cern.ch:/usr/lib/python2.6/site-packages/.
# scp -r lib/rucio root@rucio-server-prod-02.cern.ch:/usr/lib/python2.6/site-packages/.
# scp -r lib/rucio root@rucio-server-prod-03.cern.ch:/usr/lib/python2.6/site-packages/.
# scp -r lib/rucio root@rucio-server-prod-04.cern.ch:/usr/lib/python2.6/site-packages/.
# scp -r lib/rucio root@rucio-server-prod-05.cern.ch:/usr/lib/python2.6/site-packages/.
#
#
#
cmd="/usr/bin/supervisorctl restart all"
# cmd="/usr/bin/pip-python install --verbose --upgrade rucio"
# cmd="/usr/bin/pip freeze|grep rucio"
echo "$cmd"
ssh root@rucio-daemon-prod-01.cern.ch    "$cmd"
ssh root@rucio-daemon-prod-02.cern.ch    "$cmd"
ssh root@rucio-daemon-prod-03.cern.ch    "$cmd"
ssh root@rucio-daemon-prod-04.cern.ch    "$cmd"
ssh root@rucio-daemon-prod-05.cern.ch    "$cmd"
ssh root@rucio-daemon-prod-06.cern.ch    "$cmd"
ssh root@rucio-daemon-prod-07.cern.ch    "$cmd"
ssh root@rucio-daemon-prod-08.cern.ch    "$cmd"
ssh root@rucio-daemon-prod-09.cern.ch    "$cmd"
ssh root@rucio-daemon-prod-10.cern.ch    "$cmd"
ssh root@rucio-daemon-prod-11.cern.ch    "$cmd"
ssh root@rucio-daemon-prod-12.cern.ch    "$cmd"
ssh root@rucio-daemon-prod-13.cern.ch    "$cmd"
ssh root@rucio-daemon-prod-14.cern.ch    "$cmd"
ssh root@rucio-daemon-prod-15.cern.ch    "$cmd"
ssh root@rucio-daemon-prod-16.cern.ch    "$cmd"
ssh root@rucio-daemon-prod-17.cern.ch    "$cmd"
ssh root@rucio-daemon-prod-18.cern.ch    "$cmd"

cmd="/sbin/service httpd graceful"
# cmd="/sbin/service memcached reload "
# cmd="/sbin/service httpd restart"
# cmd="/usr/bin/pip-python install --verbose --upgrade rucio"
# cmd="/usr/bin/pip freeze|grep rucio"
echo "$cmd"
# ssh root@rucio-auth-prod-01.cern.ch    "$cmd"
# ssh root@rucio-auth-prod-02.cern.ch    "$cmd"
# ssh root@rucio-redirect-prod-01.cern.ch    "$cmd"
# ssh root@rucio-server-prod-01.cern.ch    "$cmd"
# ssh root@rucio-server-prod-02.cern.ch    "$cmd"
# ssh root@rucio-server-prod-03.cern.ch    "$cmd"
# ssh root@rucio-server-prod-04.cern.ch    "$cmd"
# ssh root@rucio-server-prod-05.cern.ch    "$cmd"