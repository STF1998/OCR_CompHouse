import cv2
import numpy
from pdf2image import convert_from_path as conversion
import os
import pikepdf

def clip_pdf(pdf_path):

    pdf = pikepdf.open(pdf_path, "rb", allow_overwriting_input=True)
    length = len(pdf.pages)
    print(length)

    upper = 16
    if length < upper:
        upper = length

    lower = 6
    if length < lower:
        lower = 0

    del pdf.pages[upper + 1:]
    del pdf.pages[:lower]

    pdf.save(pdf_path)

def detect_skew(greyscale_img):


    non_absolute_black_coordinates = numpy.column_stack(numpy.where(greyscale_img > 0))
    skew_angle = cv2.minAreaRect(non_absolute_black_coordinates)[-1]

    if skew_angle == 90:
        return 0
    if skew_angle < -45:
        return -(90+skew_angle)
 
    return -skew_angle

def deal_with_skew(skew_angle, greyscale_img):


    height, width = greyscale_img.shape
    img_center = (width / 2, height / 2)

    rotationMatrix = cv2.getRotationMatrix2D(img_center, skew_angle, 1.0)
    rotated_img = cv2.warpAffine(greyscale_img,
                                rotationMatrix,
                                (width, height),
                                borderMode = cv2.BORDER_REFLECT)
    
    return rotated_img


def pdf_to_png(filepath):

    # clip-pdf if required 
    clip_pdf(filepath)

    # some font sizes are small on balance sheets e.g (font_size < 8) and so it is recommended in this case
    # to increase DPI to 400-600. The claimed accuracy benefits are not present in this application, as noted
    # from confidence ratings on OCR output. To maintain speed DPI is kept at 300 
    pages = conversion(filepath, 400)
    image_counter = 1

    filepath = filepath.strip(".pdf")

    for page in pages:
        page.save(f"{filepath}-{image_counter}.png", 'PNG')
        image_counter += 1
    

def pre_process(png_filepath):
        
    for_return = []
    png_files = []
    margin_inches = 0.5
    default_page_height = 11 # The default height of a page in popular word processors
    default_page_width = 8.5 # The default width of a page

    print(png_filepath)
    i = 1
    while os.path.isfile(f"{png_filepath}-{i}.png"):
        png_files.append(f"{png_filepath}-{i}.png")
        i += 1

    
    i = 1
    for png_file in png_files:
        
        # read in the png image with the greyscale flag on 
        img = cv2.imread(png_file, cv2.IMREAD_GRAYSCALE)

        # find header and margin sizes
        bottom_header_size = round(img.shape[0]*(margin_inches*2)/default_page_height)
        margin_size = round((img.shape[1]*margin_inches)/default_page_width)


        # not normally an issue with companies house but, I have included skew correction in case
        skew_angle = detect_skew(img)
        if skew_angle != 0:
            img = deal_with_skew(skew_angle, img)
        
        #Some have staple and puncture markes on page border - this solves for this issue
        # with very low risk of losing information 
        # [top: bottom, left, right]
        crop_img = img[200: -(bottom_header_size + 200), 100:-100]


         # OTSU Binarizastion and inverting the image for morphological transformations 
        NaN, binary = cv2.threshold(crop_img, 127, 255,cv2.THRESH_BINARY_INV) 

        # using a small kernel just to get rid of small white noice rather than deal with fancy fonts.
        # I have never observed fancy fonts in the proffessional standards of accountants so I do not need to 
        # account for it.

        #opening (erosions followed by dilation) gets rid of white noise and restores text boundaries
        opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, numpy.ones((2,2), numpy.uint8))

        dilation = cv2.dilate(opening ,numpy.ones((1,1), numpy.uint8) ,iterations = 1)
        
        # Undo inversion 
        transformed_image = cv2.bitwise_not(dilation)
        
        # over-write
        cv2.imwrite(png_file, transformed_image)
        for_return.append(png_file)

    return for_return