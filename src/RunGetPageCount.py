from Validation import validatePdf
from Utils import inputPath, outputPath
from PDFix import GetPageCount
from pathlib import Path
import multiprocessing
import time
import csv

inputFolder = inputPath + "/live"
outputFolder = outputPath + "/count"

if __name__ == '__main__':
    multiprocessing.freeze_support()

    # Get the main directories to in the input folder
    input_directories = []
    for directory in Path(inputFolder).iterdir():
        if directory.is_dir():
            input_directories.append(str(directory))

    # Loop through all PDF files in the input directories
    for directory in input_directories:
        input_files = []

        for pdfFile in Path(directory).rglob("*.pdf"):
            input_files.append(str(pdfFile))

        print(directory.split('/')[-1] + " GetPageCount...")
        start_wall = time.perf_counter()
        start_cpu = time.process_time()
        results = []
        with multiprocessing.Pool(processes=4) as pool:
            results.append(pool.map(GetPageCount, input_files))
        end_wall = time.perf_counter()
        end_cpu = time.process_time()
        print(f"{end_wall - start_wall:.2f} seconds (wall time)")
        print(f"{end_cpu - start_cpu:.2f} seconds (CPU time)")

        # Write results to CSV
        with open(outputFolder + '/' + directory.split('/')[-1] + '_page_counts.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['File Path', 'Page Count'])
            for result in results[0]:
                writer.writerow(result)
