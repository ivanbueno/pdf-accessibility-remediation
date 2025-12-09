from Utils import inputPath, outputPath
from pdfixsdk import *
from Validation import validatePdf
from pathlib import Path
import multiprocessing
import time

inputFolder = inputPath + "/judicial-council-pdfs"
outputFolder = outputPath + "/judicial-council-pdfs-accessible"

def FixPDF(inputPdfPath: str, outputPdfPath: str):
    # Open the PDF document
    pdfix  = GetPdfix()
    if pdfix is None:
        print('Pdfix Initialization fail')

    doc = pdfix.OpenDoc(inputPdfPath, "")
    if doc is None:
        print('Unable to open pdf : ' + pdfix.GetError())

    command = doc.GetCommand()

    cmdStm = pdfix.CreateMemStream()
    if not command.SaveCommandsToStream(kActionMakeAccessible, cmdStm, kDataFormatJson, kSaveFull):
        print(pdfix.GetError())

    if not command.LoadParamsFromStream(cmdStm, kDataFormatJson):
        print(pdfix.GetError())

    cmdStm.Destroy()

    # run the command
    if not command.Run():
        print(pdfix.GetError())

    if not doc.Save(outputPdfPath, kSaveFull):
        print(pdfix.GetError())

    doc.Close()

if __name__ == '__main__':

    # Loop through all PDF files in the inputFolder
    # for pdfFile in Path(inputFolder).glob("*.pdf"):
    #     inputPdfPath = str(pdfFile)
    #     outputPdfPath = str(Path(outputFolder) / pdfFile.name)
    #     print(outputPdfPath)

    #     print(f"Processing: {inputPdfPath}")

    #     # Open the PDF document
    #     pdfix  = GetPdfix()
    #     if pdfix is None:
    #         raise Exception('Pdfix Initialization fail')

    #     doc = pdfix.OpenDoc(inputPdfPath, "")
    #     if doc is None:
    #         raise Exception('Unable to open pdf : ' + pdfix.GetError())

    #     command = doc.GetCommand()

    #     cmdStm = pdfix.CreateMemStream()
    #     if not command.SaveCommandsToStream(kActionMakeAccessible, cmdStm, kDataFormatJson, kSaveFull):
    #         raise Exception(pdfix.GetError())

    #     if not command.LoadParamsFromStream(cmdStm, kDataFormatJson):
    #         raise Exception(pdfix.GetError())

    #     cmdStm.Destroy()

    #     # run the command
    #     if not command.Run():
    #         print(pdfix.GetError())

    #     if not doc.Save(outputPdfPath, kSaveFull):
    #         print(pdfix.GetError())

    #     doc.Close()

        # Validate the accessibility of the processed PDF


    input_files = []
    input_outputs = []
    for pdfFile in Path(inputFolder).glob("*.pdf"):
        input_files.append(str(pdfFile))
        input_outputs.append((str(pdfFile), str(Path(outputFolder) / pdfFile.name)))

    print("Starting validation before remediation...")
    start_wall = time.perf_counter()
    start_cpu = time.process_time()
    with multiprocessing.Pool(processes=8) as pool:
        results = pool.map(validatePdf, input_files)
    print(f"VeraPDF Validation - Passed: {results.count(True)}, Failed: {results.count(False)}")
    end_wall = time.perf_counter()
    end_cpu = time.process_time()
    print(f"{end_wall - start_wall:.2f} seconds (wall time)")
    print(f"{end_cpu - start_cpu:.2f} seconds (CPU time)")

    print("PDFix remediation...")
    start_wall = time.perf_counter()
    start_cpu = time.process_time()
    with multiprocessing.Pool(processes=8) as pool:
        results = pool.starmap(FixPDF, input_outputs)
    end_wall = time.perf_counter()
    end_cpu = time.process_time()
    print(f"{end_wall - start_wall:.2f} seconds (wall time)")
    print(f"{end_cpu - start_cpu:.2f} seconds (CPU time)")
    print("Remediation completed.")

    print("Starting validation after remediation...")
    output_files = []
    start_wall = time.perf_counter()
    start_cpu = time.process_time()
    for pdfFile in Path(outputFolder).glob("*.pdf"):
        output_files.append(str(pdfFile))
    with multiprocessing.Pool(processes=8) as pool:
        results = pool.map(validatePdf, output_files)
    print(f"VeraPDF Validation - Passed: {results.count(True)}, Failed: {results.count(False)}")
    end_wall = time.perf_counter()
    end_cpu = time.process_time()
    print(f"{end_wall - start_wall:.2f} seconds (wall time)")
    print(f"{end_cpu - start_cpu:.2f} seconds (CPU time)")
