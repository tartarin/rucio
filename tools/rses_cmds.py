
if __name__ == '__main__':

    rses = [u'BNL-OSG2_DATADISK', u'BNL-OSG2_DDMTEST', u'BNL-OSG2_DATATAPE', u'BNL-OSG2_DET-SLHC', u'BNL-OSG2_HOTDISK', u'BNL-OSG2_LOCALGROUPDISK', u'BNL-OSG2_MCTAPE', u'BNL-OSG2_PERF-EGAMMA', u'BNL-OSG2_PERF-FLAVTAG', u'BNL-OSG2_PERF-JETS', u'BNL-OSG2_PERF-MUONS', u'BNL-OSG2_PHYS-HI', u'BNL-OSG2_PHYS-SM', u'BNL-OSG2_PHYS-TOP', u'BNL-OSG2_PRODDISK', u'BNL-OSG2_SCRATCHDISK', u'BNL-OSG2_TRIG-DAQ', u'BNL-OSG2_USERDISK']
    for rse in rses:
        print "dq2-set-location-status -e %(rse)s -p d -s auto -r 'Migration to Rucio done'" % locals()
#        print "dq2-set-location-status -e %(rse)s -p d -s off -r 'Migration to Rucio'" % locals()
