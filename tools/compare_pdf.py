import os
import sys
from PyPDF2 import PdfReader, PdfWriter
from wand.image import Image
import cv2
import numpy as np
import PyPDF2 
import natsort

# Define the directory containing the images
images = './images'
tempdir = './temp'

# Define the directory containing the comparison
comparedir = './compare'

# Define the prefix
prefix_a = 'version2'
prefix_b = 'version1'

# Define the threshold for detecting differences
threshold = 20

# define color for highlighting

highlight_color = (255, 0, 0)


# Define the prefix to put on the left. The right will have the diff file

prefix_left = 'version1'
prefix_right = 'diff_version2'

# Scale factor to go from portrait to landscape
scale_factor = 0.66

def check_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Directory '{directory}' created!")
    else:
        print(f"Directory '{directory}' already exists.")

def pdf_to_png(input_file,imagedir,pdfdir):
    # Open the input PDF file
    with open(input_file, 'rb') as pdf_file:
        # Create a PDF reader object
        pdf_reader = PdfReader(pdf_file)
        # Iterate through each page of the PDF
        for page_num in range(len(pdf_reader.pages)):
            # Create a new PDF writer object
            pdf_writer = PdfWriter()
            # Add the current page to the PDF writer
            pdf_writer.add_page(pdf_reader.pages[page_num])
            # Write the new PDF file to disk
            output_file = os.path.join(pdfdir,os.path.splitext(input_file)[0] + '_page_{}.pdf'.format(page_num+1))
            with open(output_file, 'wb') as output:
                pdf_writer.write(output)
            # Convert the PDF page to an image
            with Image(filename=output_file, resolution=300) as img:
                # Set the output file name
                output_file_png = os.path.splitext(input_file)[0] + '_page_{}.png'.format(page_num+1)
                # Save the image to file
                img.save(filename=os.path.join(imagedir,output_file_png))
            # Delete the temporary PDF file
            #os.remove(output_file)




def get_bounding_boxes(img_diff):
    _, thresh = cv2.threshold(cv2.cvtColor(img_diff, cv2.COLOR_BGR2GRAY), 0, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    bounding_boxes = []
    for contour in contours:
        bounding_boxes.append(cv2.boundingRect(contour))

    bounding_boxes = sorted(bounding_boxes, key=lambda x: x[0])

    merged_boxes = []
    if bounding_boxes:
        merged_boxes.append(bounding_boxes[0])
        for box in bounding_boxes[1:]:
            last_box = merged_boxes[-1]
            if box[0] < last_box[0] + last_box[2] and box[1] < last_box[1] + last_box[3]:
                merged_boxes[-1] = (
                    min(last_box[0], box[0]),
                    min(last_box[1], box[1]),
                    max(last_box[0] + last_box[2], box[0] + box[2]) - min(last_box[0], box[0]),
                    max(last_box[1] + last_box[3], box[1] + box[3]) - min(last_box[1], box[1])
                )
            else:
                merged_boxes.append(box)

    return merged_boxes

def compare_files(directory,outputdir):
    for file_a in os.listdir(directory):
        if file_a.startswith(prefix_a) and file_a.endswith('.png'):
            file_b = file_a.replace(prefix_a, prefix_b)
            print('comparing ' + file_a + ' and ' + file_b + ':')
            if os.path.exists(os.path.join(directory,file_b)):
                img_a = cv2.imread(os.path.join(directory,file_a))
                img_b = cv2.imread(os.path.join(directory,file_b))

                img_diff = cv2.absdiff(img_a, img_b)
                diff_gray = cv2.cvtColor(img_diff, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(diff_gray, 30, 255, cv2.THRESH_BINARY)

                if cv2.countNonZero(thresh) > 0:
                    bounding_boxes = get_bounding_boxes(img_diff)
                    for box in bounding_boxes:
                        # We draw the bounding boxes on the LATER file - img_a
                        cv2.rectangle(img_a, (box[0]-5, box[1]-5), (box[0]+box[2]+5, box[1]+box[3]+5), highlight_color, 2)
                    diff_file = f"diff_{file_a}" 
                    cv2.imwrite(os.path.join(outputdir,diff_file),img_a)




def create_comparison(inputdir,comparedir,outputdir):
    # Get a list of all the PNG files in the directory
    png_files = [os.path.join(comparedir, f) for f in os.listdir(comparedir) if f.startswith(prefix_right) and f.endswith(".png")]
    outputfile = png_files[0].split("_")[0] + '_' + png_files[0].split("_")[1] + ".pdf"
    outputfile = os.path.join(outputdir,os.path.split(outputfile)[1])
    
    if os.path.exists(outputfile):
        os.remove(outputfile)

    # Iterate through the PNG files and add them to the PDF file
    for png_file in png_files:
        # Open the PNG file using Wand
        with Image(filename=png_file) as img:
            # Convert the image to PDF format
            img.format = 'pdf'
            # Append the converted image to the PDF file
            with open(png_file + ".pdf","wb") as pdf:
                img.save(pdf)


    # Merge the PDF files into a single PDF
    right_files = natsort.natsorted([os.path.join(comparedir, f) for f in os.listdir(comparedir) if f.endswith(".pdf")])

    # Create a PDF writer object
    pdf_writer = PyPDF2.PdfWriter()

            

    for filename in right_files:
        print(filename)
        # find the left file
        page_number = filename.split("_")[3].split(".")[0]
        left_file = prefix_left + "_page_" + page_number + ".pdf"
        
        # Create a new landscape page
        landscape_page = PyPDF2.PageObject.create_blank_page(None, 792, 612)
        # Note: 792 and 612 are the width and height of a landscape page in points

        with open(os.path.join(inputdir,left_file), 'rb') as file:
            left_page_file = PyPDF2.PdfReader(file)
            left_page  = left_page_file.pages[0].rotate(90)
            left_page_width = left_page.mediabox.width
            print("left: " + str(left_page_width))
            # rotate/scale both pages
            transformation_left = PyPDF2.Transformation().scale(scale_factor).translate(0, 0)
            left_page.add_transformation(transformation_left)
            # Add the rotated pages to the landscape page
            landscape_page.merge_page(left_page, False)
        
            with open(filename, 'rb') as file:
                right_page_file = PyPDF2.PdfReader(file)
                right_page = right_page_file.pages[0].rotate(90)
                right_page_width = right_page.mediabox.width
                print("right: " + str(right_page_width))
                # rotate/scale both pages
                transformation_right = PyPDF2.Transformation().scale(left_page_width/right_page_width*scale_factor).translate(400, 0)
                right_page.add_transformation(transformation_right)
                # Add the rotated pages to the landscape page
                landscape_page.merge_page(right_page, False)

            # Add the landscape page to the output PDF file
                pdf_writer.add_page(landscape_page)

        # remove the temporary PDF
        os.remove(filename)
    
    # Save the merged PDF to a file
    with open(outputfile, 'wb') as file:
        pdf_writer.write(file)


if __name__ == '__main__':
    # Get the input file path from the command line arguments
    if len(sys.argv) < 3:
        print('Please provide the path to the comparison PDF files.')
        sys.exit(1)
    version1 = sys.argv[1]
    version2 = sys.argv[2]
    check_directory(tempdir)
    check_directory(images)
    # Convert the input PDF to PNG images
    pdf_to_png(version1,images,tempdir)
    pdf_to_png(version2,images,tempdir)
    # do the comparison
    check_directory(comparedir)
    # Convert the input PDF to PNG images
    compare_files(images,comparedir)
    # Create a consolidated side-by-side comparison
    create_comparison(tempdir,comparedir,".")
