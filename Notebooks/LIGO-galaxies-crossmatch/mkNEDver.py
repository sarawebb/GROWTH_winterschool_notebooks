import numpy as np
from astropy.table import Table, vstack, hstack, Column, unique
import os, sys, math, pdb, glob, fnmatch, time
import astropy.units as u
from astropy.coordinates import SkyCoord
from astroquery.ned import Ned
from multiprocessing import Pool
def stop(): pdb.set_trace()

def NEDsearch(index):
    try:
	ned = Ned.query_region(coordall[index], radius=10 * u.arcsec, equinox='J2000.0')
	ind=np.where( (ned['Redshift'] < 0.06) )
	if (np.size(ind) == 0):
            #cluall['NotInNED'][index]=1
            out=np.array([(index,1)],dtype=[('index','i4'),('NotInNED','i4')])    
	    #print 'no match in NED with redshift...'
	    #print cluall['NAME','RA','DEC','Z','DISTMPC','NotInNED'][index]
	    #print ned['Object Name','RA(deg)','DEC(deg)','Redshift','Distance (arcmin)']
	    #nrem=nrem+1
	    #stop()
	else:
            out=np.array([(index,0)],dtype=[('index','i4'),('NotInNED','i4')])    
	    
    except:
        #print 'no NED object in database'
        #cluall['NotInNED'][index]=1
        out=np.array([(index,1)],dtype=[('index','i4'),('NotInNED','i4')])    
        #print cluall['NAME','RA','DEC','Z','DISTMPC','NotInNED'][index]
	#nrem=nrem+1
	#stop()	
	
    return out

cluall=Table.read('LIGOcross/CLU_20170106_galexwise_DaveUpdate.fits')
cluall=cluall[0:1000]

usource=unique(cluall,keys='SOURCE')
nall=np.size(cluall)
coordall = SkyCoord(ra=cluall['RA'], dec=cluall['DEC'], unit=(u.deg, u.deg), frame='fk5')

ind=np.where(cluall['SOURCE'] != 'NED_20161120')
#notnedcol=Column(np.zeros(nall,dtype='i4'),name='NotInNED')
#cluall.add_column(notnedcol)

start=time.time()

nrem=0

pool = Pool(processes=4)   
result=pool.map_async(NEDsearch, range(nall), chunksize=1)
while not result.ready():
    sys.stdout.write("num left: %i \r" %(result._number_left*result._chunksize))
    sys.stdout.flush()
    time.sleep(0.25)
out=result.get()
pool.close()
pool.join()

test=np.array(out).flatten()
catout=Table(test)

cluall=hstack([cluall,catout])

end=time.time()
print 'Run time=%.4f mins' %((end-start)/60.)


stop()
sys.exit()
