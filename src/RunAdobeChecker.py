from Adobe import PDFAccessibilityChecker
from Validation import validatePdf
from Utils import inputPath, outputPath
from pathlib import Path
import multiprocessing
import time
import csv

inputFolder = inputPath + "/judicial-council-pdfs"
outputFolder = outputPath + "/adobe"
outputFolderReports = outputPath + "/adobe-reports"

if __name__ == '__main__':
    multiprocessing.freeze_support()

    input_files = []
    input_outputs = []
    for pdfFile in Path(inputFolder).glob("*.pdf"):
        input_files.append(str(pdfFile))
        input_outputs.append((str(pdfFile), str(Path(outputFolder) / pdfFile.name), str(Path(outputFolderReports) / (pdfFile.stem + ".json"))))

    print()
    print("VeraPDF VALIDATION")
    start_wall = time.perf_counter()
    start_cpu = time.process_time()
    with multiprocessing.Pool(processes=4) as pool:
        results = pool.map(validatePdf, input_files)
    end_wall = time.perf_counter()
    end_cpu = time.process_time()
    # print(f"Passed: {results.count(True)}, Failed: {results.count(False)}, Errors: {results.count('Error')}")
    print(f"{end_wall - start_wall:.2f} seconds (wall time)")
    print(f"{end_cpu - start_cpu:.2f} seconds (CPU time)")
    # Write results to CSV
    with open(outputPath + '/noncompliant_vera_validation_results.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(results)

    print()
    print("ADOBE VALIDATION")
    start_wall = time.perf_counter()
    start_cpu = time.process_time()
    with multiprocessing.Pool(processes=1) as pool:
        results = pool.starmap(PDFAccessibilityChecker, input_outputs)
    end_wall = time.perf_counter()
    end_cpu = time.process_time()
    print(f"Passed: {results.count(True)}, Failed: {results.count(False)}, Errors: {results.count('Error')}")
    print(f"{end_wall - start_wall:.2f} seconds (wall time)")
    print(f"{end_cpu - start_cpu:.2f} seconds (CPU time)")
    # Write results to CSV
    with open(outputPath + '/remediated_adobe_validation_results.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(results)
