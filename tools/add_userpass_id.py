#!/usr/bin/env python
# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#                       http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Vincent Garonne, <vincent.garonne@cern.ch>, 2014

from rucio.db import session, models
from rucio.db.constants import IdentityType

if __name__ == '__main__':

    up_id = 'ami'
    up_pwd = 'b009bb87d4be2c6e366d07bdf5e16eab772bd5e773f9b4b51df9e8b169605943'
    up_email = 'tagcollector@lpsc.in2p3.fr'
    account = 'atagcol'

    s = session.get_session()
    identity1 = models.Identity(identity=up_id, identity_type=IdentityType.USERPASS, password=up_pwd, salt='0', email=up_email)
    iaa1 = models.IdentityAccountAssociation(identity=identity1.identity, identity_type=identity1.identity_type, account=account, is_default=False)

    # Apply
#    s.add_all([identity1])
#    s.commit()
    s.add_all([iaa1])
    s.commit()
