from Validation import validatePdf
from Utils import inputPath, outputPath
from PDFix import FixPDF
from pathlib import Path
import multiprocessing
import time

inputFolder = inputPath + "/judicial-council-pdfs"
outputFolder = outputPath + "/judicial-council-pdfs-accessible"

if __name__ == '__main__':
    multiprocessing.freeze_support()

    input_files = []
    input_outputs = []
    for pdfFile in Path(inputFolder).glob("*.pdf"):
        input_files.append(str(pdfFile))
        input_outputs.append((str(pdfFile), str(Path(outputFolder) / pdfFile.name)))

    print("Starting validation before remediation...")
    start_wall = time.perf_counter()
    start_cpu = time.process_time()
    with multiprocessing.Pool(processes=4) as pool:
        results = pool.map(validatePdf, input_files)
    print(f"VeraPDF Validation - Passed: {results.count(True)}, Failed: {results.count(False)}")
    end_wall = time.perf_counter()
    end_cpu = time.process_time()
    print(f"{end_wall - start_wall:.2f} seconds (wall time)")
    print(f"{end_cpu - start_cpu:.2f} seconds (CPU time)")

    print("PDFix remediation...")
    start_wall = time.perf_counter()
    start_cpu = time.process_time()
    with multiprocessing.Pool(processes=4) as pool:
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
    with multiprocessing.Pool(processes=4) as pool:
        results = pool.map(validatePdf, output_files)
    print(f"VeraPDF Validation - Passed: {results.count(True)}, Failed: {results.count(False)}")
    end_wall = time.perf_counter()
    end_cpu = time.process_time()
    print(f"{end_wall - start_wall:.2f} seconds (wall time)")
    print(f"{end_cpu - start_cpu:.2f} seconds (CPU time)")
