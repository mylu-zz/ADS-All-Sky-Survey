#randomAstrometry.py
#max lu

from SIMBAD import Client
from subprocess import *
import os, signal, time, random

#user-adjustable parameters
runTime1 = 15          # Astrometry run-time given object coordinates (s)
runTime2 = 150         # Astrometry run-time without object coordinates (s)
numObjects = 10        # maximum number of SIMBAD objects in a paper to test
radius = 1             # radius from given coordinates (deg)
downsampleFactor = 4   # downsample factor
numImages = 300        # size of sample

images = []
failed_images = []
ra_dec = []
times = []

totImages = os.listdir('./images/.')

testImages = []
totImagesLength = str(len(totImages))

def simbadSolve(inverted):
    for obj in SimbadClient.objects:
        simbadRA = str(obj).split('|')[1]
        simbadDec = str(obj).split('|')[2]
        print 'testing simbad object coordinates: ' + simbadRA + " " + simbadDec
        if inverted == false:
            process = subprocess.Popen('/var/opt/astronometry/bin/solve-field --overwrite --dir astrometry_output --no-plots --downsample ' + str(downsampleFactor) + ' --ra ' + simbadRA + ' --dec ' + simbadDec + ' --radius ' + str(radius) + ' ./images/' + image,stdout=PIPE,stderr=STDOUT,shell=True,preexec_fn=os.setsid)
        else:
            process = subprocess.Popen('/var/opt/astronometry/bin/solve-field --overwrite --dir astrometry_output --no-plots --downsample ' + str(downsampleFactor) + ' --ra ' + simbadRA + ' --dec ' + simbadDec + ' --radius ' + str(radius) + ' ./images_inverted/' + image,stdout=PIPE,stderr=STDOUT,shell=True,preexec_fn=os.setsid)
        time.sleep(runTime1)
        try:
            os.killpg(process.pid,signal.SIGTERM)
        except OSError:
            pass
        #Checks to see if Astrometry is successful
        output = process.communicate()[0]
        if output.find('solved')>-1 and output.find('Failed')==-1:
            success = True
            ra_decIndex = output.find('(RA,Dec)') + 11
            ra_dec.append(output[ra_decIndex:output.find(') deg.') + 1])
            images.append(image)
            if inverted==false:
                print 'image ' + image + ' solved'
            else:
                print 'inverted image ' + image + 'solved'
            times.append(time.time()-startImage)
            break
        elif output.find('Command failed: return value 255')>-1:
            print "Error: " + output
        break

def generalSolve(inverted):
    if inverted == false:
        process = subprocess.Popen('/var/opt/astronometry/bin/solve-field --overwrite --dir astrometry_output --no-plots --downsample ' + str(downsampleFactor) + ' ./images/' + image,stdout=PIPE,stderr=STDOUT,shell=True,preexec_fn=os.setsid)
    else:
        process = subprocess.Popen('/var/opt/astronometry/bin/solve-field --overwrite --dir astrometry_output --no-plots --downsample ' + str(downsampleFactor) + ' ./images_inverted/' + image,stdout=PIPE,stderr=STDOUT,shell=True,preexec_fn=os.setsid)
    time.sleep(runTime2)
    try:
        os.killpg(process.pid,signal.SIGTERM)
    except OSError:
        pass
    output = process.communicate()[0]
    #checks to see if Astrometry is successful
    if output.find('solved')>-1 and output.find('Failed')==-1:
        success = True
        if inverted == false:
            print 'image ' + image + ' solved'
        else:
            print 'inverted image ' + image + ' solved'
        ra_decIndex = output.find('(RA,Dec)') + 11
        ra_dec.append(output[ra_decIndex:output.find(') deg.') + 1])
        images.append(image)
        times.append(time.time()-startImage)
    elif output.find('Command failed: return value 255')>-1:
        print "Error: " + output

# create random sample of images
i = 0
while i < numImages:
    number = int(random.random()*len(totImages))
    if testImages.count(totImages[number]) == 0:
        testImages.append(totImages[number])
    subprocess.call('cp ' + './images/' + totImages[number] + ' ./test_images/' + totImages[number],shell=True)
    totImages.pop(number)
    i = i+1

# transfer images to valinor
subprocess.call('scp -r ./test_images/ maxlu@valinor.cfa.harvard.edu:',shell=True)
print 'Testing ' + str(numImages) + ' within ' + str(totImagesLength)

# find total solve time
start = time.time()
f = open('astrometry_output.txt','w')

i = 0
for image in testImages:
    btemps = os.listdir('../../.././tmp/.')
    startImage = time.time()
    
    i = i + 1
    f.seek(0)
    f.write('testing image ' + str(i) + ' out of ' + str(numImages) + ' images\n')
    #gets list of SIMBAD objects within a paper
    SimbadClient = Client()
    bibcode = image[0:image.index('-')]
    SimbadClient.bibcode = bibcode
    SimbadClient.getObjects() 

    success = False

    #Runs Astrometry on image given SIMBAD coordinates as parameters
    if len(SimbadClient.objects)!=0 and len(SimbadClient.objects) <= numObjects:
        print 'testing image: ' + image
        simbadSolve(false)

    #Runs Astrometry on inverted image given SIMBAD coordinates as parameters            
    if success == False:
        if len(SimbadClient.objects)!=0 and len(SimbadClient.objects) <= numObjects:
            print 'testing inverted image: ' + image
            simbadSolve(true)

    #Runs Astrometry on image without SIMBAD coordinates
    if success == False:
        print 'testing image ' + image + " without simbad object coordinates"
        generalSolve(false)

    #Runs Astrometry on inverted image without SIMBAD coordinates
    if success == False:
        print 'testing inverted image ' + image + " without simbad object coordinates"
        generalSolve(true)

    #Moves images if Astrometry is not successful
    if success == False:
        print 'image ' + image + ' did not solve'
        failed_images.append(image)
    print ''
    etemps = os.listdir('../../.././tmp/.')
    for tmp in etemps:
        if btemps.count(tmp) == 0:
            subprocess.call('rm -f ../../.././tmp/' + tmp,shell=True)

#Prints solved images and coordinates+
print ''
print 'solved images:'
f.write('\n\n\n')
f.write('solved images:\n')
for i in range(len(images)):
    print "Image: " + images[i] + "      Coordinates: " + ra_dec[i] + "      Time: " + str(times[i])
    f.write("Image: " + images[i] + "      Coordinates: " + ra_dec[i] + "      Time: " + str(times[i]) + '\n')
print '\n\n\n\n\nfailed images:'
f.write('\n\n\n\n\nfailed images:')
for i in range(len(failed_images)):
    print "Image: " + failed_images[i]
    f.write("Image: " + failed_images[i]+ '\n')

print ''
print "Elapsed time: " + str(time.time() - start) + " seconds"
print ''
f.write("\n\n\n\nElapsed time: " + str(time.time() - start) + " seconds\n\n")
