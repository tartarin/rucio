#!/usr/bin/env sh

cmd="/bin/rm -rf /tmp/pip-build-root/"
cmd="/etc/init.d/httpd restart"
#cmd="/usr/bin/puppet  agent --test --verbose --debug --no-daemonize"
#cmd="/usr/bin/pip-python install --verbose --upgrade rucio"
cmd="/bin/rm -rf /tmp/pip-build-root/; /usr/bin/pip-python install --verbose --upgrade rucio; /etc/init.d/httpd restart"
#cmd="/usr/bin/pip-python install  distribute==0.6.48"
#cmd="puppet agent --test --verbose --debug --no-daemonize; /etc/init.d/httpd stop; rm -rf /var/log/httpd/error_log ; /etc/init.d/httpd start"
#cmd="/usr/bin/pip-python freeze|grep rucio"
#cmd="/bin/rm -rf /tmp/pip-build-root/"
#cmd="/usr/bin/pip-python freeze|grep SQLAlchemy"
#cmd="/usr/bin/supervisorctl restart all"
#cmd="/etc/init.d/httpd stop"
#cmd="/usr/bin/supervisorctl stop all"
#cmd="/usr/bin/supervisorctl status all"
#cmd="/usr/bin/pip-python freeze|grep SQLAlchemy"
#cmd='/bin/hostname; grep limit /var/log/httpd/error_log'
#cmd='grep SESSIONS_PER_USER /var/log/httpd/error_log'
#cmd="/etc/init.d/httpd stop"

cmd="curl https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py | python; /bin/rm -rf /tmp/pip-build-root/; /usr/bin/pip-python install --verbose --upgrade rucio"
cmd="/bin/rm -rf /tmp/pip-build-root/; /usr/bin/pip-python install --verbose --upgrade rucio"
cmd="hostname;/usr/bin/pip-python freeze|grep rucio"
#cmd="/etc/init.d/httpd graceful; /usr/bin/supervisorctl restart all"
#cmd="puppet agent --test --verbose --debug --no-daemonize"
#cmd="/usr/bin/supervisorctl -c /etc/supervisord.conf update"
#cmd="/usr/bin/supervisorctl restart all; "

#cmd="/etc/init.d/httpd graceful"

#cmd="/etc/init.d/httpd restart"

cmd="/bin/rm -rf /tmp/pip-build-root/; /usr/bin/pip-python install --verbose --upgrade rucio;/usr/bin/supervisorctl restart all; "

cmd="/bin/rm -rf /tmp/pip-build-root/; /usr/bin/pip-python install --verbose --upgrade rucio"

cmd="/usr/bin/supervisorctl restart all;/etc/init.d/httpd graceful"

cmd="/usr/bin/pip-python freeze|grep rucio"


# Prod
# scp -r lib/rucio root@rucio-server-prod-01.cern.ch:/usr/lib/python2.6/site-packages/.
# scp -r lib/rucio root@rucio-server-prod-02.cern.ch:/usr/lib/python2.6/site-packages/.
# scp -r lib/rucio root@rucio-server-prod-03.cern.ch:/usr/lib/python2.6/site-packages/.
# scp -r lib/rucio root@rucio-server-prod-04.cern.ch:/usr/lib/python2.6/site-packages/.
# scp -r lib/rucio root@rucio-daemon-prod-01.cern.ch:/usr/lib/python2.6/site-packages/.
# scp -r lib/rucio root@rucio-daemon-prod-02.cern.ch:/usr/lib/python2.6/site-packages/.
# scp -r lib/rucio root@rucio-daemon-prod-03.cern.ch:/usr/lib/python2.6/site-packages/.
# scp -r lib/rucio root@rucio-daemon-prod-04.cern.ch:/usr/lib/python2.6/site-packages/.
# scp -r lib/rucio root@rucio-daemon-prod-05.cern.ch:/usr/lib/python2.6/site-packages/.
# scp -r lib/rucio root@rucio-daemon-prod-06.cern.ch:/usr/lib/python2.6/site-packages/.
# #
# #
# scp -r  bin/rucio* root@rucio-daemon-prod-01.cern.ch:/usr/bin/.
# scp -r  bin/rucio* root@rucio-daemon-prod-02.cern.ch:/usr/bin/.
# scp -r  bin/rucio* root@rucio-daemon-prod-03.cern.ch:/usr/bin/.
# scp -r  bin/rucio* root@rucio-daemon-prod-04.cern.ch:/usr/bin/.
# scp -r  bin/rucio* root@rucio-daemon-prod-05.cern.ch:/usr/bin/.
# scp -r  bin/rucio* root@rucio-daemon-prod-06.cern.ch:/usr/bin/.


scp -r lib/rucio root@rucio-auth-int-01.cern.ch:/usr/lib/python2.6/site-packages/.
scp -r lib/rucio root@rucio-daemon-int-01.cern.ch:/usr/lib/python2.6/site-packages/.
scp -r lib/rucio root@rucio-daemon-int-02.cern.ch:/usr/lib/python2.6/site-packages/.
scp -r lib/rucio root@rucio-daemon-int-03.cern.ch:/usr/lib/python2.6/site-packages/.
scp -r lib/rucio root@rucio-daemon-int-04.cern.ch:/usr/lib/python2.6/site-packages/.
scp -r lib/rucio root@rucio-server-int-01.cern.ch:/usr/lib/python2.6/site-packages/.
scp -r lib/rucio root@rucio-server-int-02.cern.ch:/usr/lib/python2.6/site-packages/.
scp -r lib/rucio root@rucio-server-int-03.cern.ch:/usr/lib/python2.6/site-packages/.



cmd="/usr/bin/supervisorctl restart all"
echo "$cmd"
ssh root@rucio-daemon-int-01.cern.ch    "$cmd"
ssh root@rucio-daemon-int-02.cern.ch    "$cmd"
ssh root@rucio-daemon-int-03.cern.ch    "$cmd"
ssh root@rucio-daemon-int-04.cern.ch    "$cmd"

cmd="/sbin/service httpd graceful"
echo "$cmd"
ssh root@rucio-auth-int-01.cern.ch      "$cmd"
ssh root@rucio-server-int-01.cern.ch    "$cmd"
ssh root@rucio-server-int-02.cern.ch    "$cmd"
ssh root@rucio-server-int-03.cern.ch    "$cmd"

cmd="curl https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py | python; /bin/rm -rf /tmp/pip-build-root/; /usr/bin/pip-python install --verbose --upgrade rucio"
# cmd="/usr/bin/yum install  -y  openldap-devel"

# cmd="/bin/rm -rf /tmp/pip-build-root/; /usr/bin/pip-python install --verbose --upgrade rucio"

cmd="hostname;/usr/bin/pip-python freeze|grep rucio"

cmd="/bin/rm -rf /tmp/pip-build-root/; /usr/bin/pip-python install --verbose --upgrade rucio"

cmd="/usr/bin/puppet agent --test --verbose --debug --no-daemonize"

# cmd="/etc/init.d/httpd graceful"

# cmd="rm -f /var/log/httpd/access_log /var/log/httpd/error_log; /sbin/service httpd graceful"


# cmd="/usr/bin/yum install -y memcached; /sbin/service memcached restart; /usr/bin/pip-python install python-memcached"

# cmd="/usr/bin/pip-python freeze|grep memcached"

#cmd="/usr/bin/yum install -y \
#       http://emisoft.web.cern.ch/emisoft/dist/EMI/2/sl6/x86_64/updates/gridsite-1.7.29-1.el6.x86_64.rpm \
#       http://emisoft.web.cern.ch/emisoft/dist/EMI/2/sl6/x86_64/updates/gridsite-libs-1.7.29-1.el6.x86_64.rpm"

# cmd='rpm -qav|grep gridsite'

# ssh root@voatlasrucio-auth-dev-01     "$cmd"
# ssh root@voatlasrucio-daemon-dev-01   "$cmd"
# ssh root@voatlasrucio-daemon-dev-02   "$cmd"
# ssh root@voatlasrucio-server-dev-01.cern.ch   "$cmd"
# ssh root@voatlasrucio-server-dev-02.cern.ch   "$cmd"
# ssh root@voatlasrucio-server-dev-03.cern.ch   "$cmd"
# ssh root@voatlasrucio-server-dev-04.cern.ch   "$cmd"
# #
# ssh root@voatlasrucio-collector-prod-01.cern.ch "$cmd"

# ssh root@voatlasrucio-auth-prod-01.cern.ch      "$cmd"
# ssh root@voatlasrucio-auth-prod-02.cern.ch      "$cmd"
# ssh root@rucio-auth-prod-01.cern.ch      "$cmd"
# ssh root@rucio-auth-prod-02.cern.ch      "$cmd"

# ssh root@voatlasrucio-redirect-prod-01.cern.ch  "$cmd"

# cmd="curl https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py | python; "
# cmd="/sbin/service httpd graceful"
# echo "$cmd"
# ssh root@rucio-server-prod-01.cern.ch    "$cmd"
# ssh root@rucio-server-prod-02.cern.ch    "$cmd"
# ssh root@rucio-server-prod-03.cern.ch    "$cmd"
# ssh root@rucio-server-prod-04.cern.ch    "$cmd"

# cmd="/usr/bin/supervisorctl restart all"
# echo "$cmd"
# # Judge, kronos
# ssh root@rucio-daemon-prod-01.cern.ch    "$cmd"
# # Poller, consumer, hermes
# ssh root@rucio-daemon-prod-02.cern.ch    "$cmd"
# # undertaker
# ssh root@rucio-daemon-prod-03.cern.ch    "$cmd"
# # Automatix, necromancer
# ssh root@rucio-daemon-prod-04.cern.ch    "$cmd"
# # Reaper
# ssh root@rucio-daemon-prod-05.cern.ch    "$cmd"
# # Submiter
# ssh root@rucio-daemon-prod-06.cern.ch    "$cmd"
