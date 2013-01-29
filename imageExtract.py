#imageExtract.py
#max lu

import os, subprocess,time
import random
start = int(round(time.time()*1000))
pdfPaths = []

f = open('extraction.txt','w')

#extracts images from pdfs in papers
startExtract = int(round(time.time()*1000))

pdfList = open('../.././ads/articles/bitmaps/pdfs.list','r')
for pdf in pdfList.readlines():
    if pdf.find('RGB')>-1 or pdf.find('GRAY')>-1:
	for phrase in pdf.split():
            if phrase.find('seri')>-1:
                pdfPaths.append(phrase)

paperCount = len(pdfPaths)
count = 0
for filepath in pdfPaths:
    bibcode = filepath[filepath.rfind('/') + 1:filepath.find(".pdf")]
    count = count + 1
    f.seek(0)
    f.write('now extracting paper ' + str(count) + ' out of ' + str(paperCount))
    subprocess.call('pdfimages -p ' + '../.././ads/articles/bitmaps/' + filepath + " ./images/" + bibcode,shell=True)

stopExtract = int(round(time.time()*1000))
f.write("\nExtraction time : " + str(stopExtract - startExtract) + "ms\n\n")
print "Extraction time : " + str(stopExtract - startExtract) + "ms"


#remove pdf pages
startImageRemove = int(round(time.time()*1000))
f.write('removing images...\n')
for img in os.listdir('./images/.'):
    if img.find('.pbm') > -1:
        subprocess.call('rm ' + './images/' + img,shell=True)
    elif os.stat('./images/' + img).st_size <=100:
        subprocess.call('cp ./images/' + img + ' ./smallimages/' + img,shell=True)
        subprocess.call('rm ./images/' + img,shell=True)

noisyimages = []
for image in os.listdir('./images/.'):
    if int(image[len(image)-7:len(image)-4]) > 200:
	if noisyimages.count(image[:image.find('-')]) == 0:
            noisyimages.append(image[:image.find('-')])
f.write('noisy images:\n')
for filename in noisyimages:
    f.write(filename + '\n')
    for image in os.listdir('./images/.'):
	if filename in image:
	    subprocess.call('cp ./images/' + image + ' ./noisy_images/' + image,shell=True)
            subprocess.call('rm ./images/' + image,shell=True)

#trims extracted images
for filename in os.listdir('./images/.'):
    subprocess.call('convert -trim ' + './images/' + filename + " " + './images/' + filename, shell=True)
stopImageRemove = int(round(time.time()*1000))
f.write( "Image Removal time: " + str(stopImageRemove - startImageRemove) + "ms\n\n")
print "Image Removal time: " + str(stopImageRemove - startImageRemove) + "ms"

#inverts files in converted_images, copies to converted_images_inverted
startInvert = int(round(time.time()*1000))
f.write("inverting images...")
for filename in os.listdir('./images/.'):
    subprocess.call('convert ' + "./images/" + filename + " -negate " + "./images_inverted/" + filename, shell=True)
    count = count + 1
stopInvert = int(round(time.time()*1000))
f.write("\nInvert time: " + str(stopInvert - startInvert) + "ms\n\n")
print "Invert time: " + str(stopInvert - startInvert) + "ms"

end = int(round(time.time()*1000))
f.write("\nElapsed time: " + str(end - start) + "ms\n\n\n")
print "Elapsed time: " + str(end - start) + "ms"



