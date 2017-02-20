from PyPDF2 import PdfFileWriter, PdfFileReader
import os

inputpdf = PdfFileReader(open("paper/test.pdf", "rb"))
path = "paper/test_split"
if not os.path.isdir(path):
   os.makedirs(path)


for i in range(inputpdf.numPages):
    output = PdfFileWriter()
    output.addPage(inputpdf.getPage(i))
    with open("paper/test_split/test%s.pdf" % i, "wb") as outputStream:
        output.write(outputStream)

#run PDF2img.sh
#os.system("bash PDF2img.sh")
