import logging
import os
from datetime import datetime

from adobe.pdfservices.operation.auth.service_principal_credentials import ServicePrincipalCredentials
from adobe.pdfservices.operation.exception.exceptions import ServiceApiException, ServiceUsageException, SdkException
from adobe.pdfservices.operation.io.cloud_asset import CloudAsset
from adobe.pdfservices.operation.io.stream_asset import StreamAsset
from adobe.pdfservices.operation.pdf_services import PDFServices
from adobe.pdfservices.operation.pdf_services_media_type import PDFServicesMediaType
from adobe.pdfservices.operation.pdfjobs.jobs.autotag_pdf_job import AutotagPDFJob
from adobe.pdfservices.operation.pdfjobs.result.autotag_pdf_result import AutotagPDFResult
from adobe.pdfservices.operation.pdfjobs.jobs.pdf_accessibility_checker_job import PDFAccessibilityCheckerJob
from adobe.pdfservices.operation.pdfjobs.result.pdf_accessibility_checker_result import PDFAccessibilityCheckerResult

class AutoTagPDF:
    def __init__(self, inputFilePath: str, outputFilePath: str):
        try:
            file = open(inputFilePath, 'rb')
            input_stream = file.read()
            file.close()

            # Initial setup, create credentials instance
            credentials = ServicePrincipalCredentials(
                client_id=os.getenv('PDF_SERVICES_CLIENT_ID'),
                client_secret=os.getenv('PDF_SERVICES_CLIENT_SECRET')
            )

            # Creates a PDF Services instance
            pdf_services = PDFServices(credentials=credentials)

            # Creates an asset(s) from source file(s) and upload
            input_asset = pdf_services.upload(input_stream=input_stream,
                                              mime_type=PDFServicesMediaType.PDF)

            # Creates a new job instance
            autotag_pdf_job = AutotagPDFJob(input_asset)

            # Submit the job and gets the job result
            location = pdf_services.submit(autotag_pdf_job)
            pdf_services_response = pdf_services.get_job_result(location, AutotagPDFResult)

            # Get content from the resulting asset(s)
            result_asset: CloudAsset = pdf_services_response.get_result().get_tagged_pdf()
            stream_asset: StreamAsset = pdf_services.get_content(result_asset)

            # Creates an output stream and copy stream asset's content to it
            with open(outputFilePath, "wb") as file:
                file.write(stream_asset.get_input_stream())

        except (ServiceApiException, ServiceUsageException, SdkException) as e:
            logging.exception(f'Exception encountered while executing operation: {e}')

class PDFAccessibilityChecker:
    def __new__(self, inputFilePath: str, outputFilePath: str, outputReportPath: str):
        try:
            pdf_file = open(inputFilePath, 'rb')
            input_stream = pdf_file.read()
            pdf_file.close()
            
            # Initial setup, create credentials instance
            credentials = ServicePrincipalCredentials(
                client_id=os.getenv('PDF_SERVICES_CLIENT_ID'),
                client_secret=os.getenv('PDF_SERVICES_CLIENT_SECRET'))
            
            # Creates a PDF Services instance
            pdf_services = PDFServices(credentials=credentials)
            
            # Creates an asset(s) from source file(s) and upload
            input_asset = pdf_services.upload(input_stream=input_stream, mime_type=PDFServicesMediaType.PDF)
    
            # Creates a new job instance
            pdf_accessibility_checker_job = PDFAccessibilityCheckerJob(input_asset=input_asset)
            
            # Submit the job and gets the job result
            location = pdf_services.submit(pdf_accessibility_checker_job)
            pdf_services_response = pdf_services.get_job_result(location, PDFAccessibilityCheckerResult)
            
            # Get content from the resulting asset(s)
            result_asset: CloudAsset = pdf_services_response.get_result().get_asset()
            stream_asset: StreamAsset = pdf_services.get_content(result_asset)
            
            report_asset: CloudAsset = pdf_services_response.get_result().get_report()
            stream_report: StreamAsset = pdf_services.get_content(report_asset)
            
            output_file_path = outputFilePath
            with open(output_file_path, "wb") as file:
                file.write(stream_asset.get_input_stream())
            
            output_file_path_json = outputReportPath
            with open(output_file_path_json, "wb") as file:
                file.write(stream_report.get_input_stream())

            is_valid = ParseValidationReport(stream_report.get_input_stream().decode('utf-8'))
            return [inputFilePath.split('/')[-1], is_valid]
            # return is_valid
        
        except (ServiceApiException, ServiceUsageException, SdkException) as e:
            # logging.exception(f'Exception encountered while executing operation: {e}')
            return [inputFilePath.split('/')[-1], 'Error', str(e)]
        
def ParseValidationReport(jsonReport: str):
    """
    Parses the JSON validation report from the Adobe PDF Accessibility Checker tool.

    Parameters:
        jsonReport (str): JSON string containing the validation results.

    Returns:
        bool: True if the PDF passes accessibility checks, False otherwise.
    """    
    import json

    report = json.loads(jsonReport)

    # Check if there are any violations
    if report['Summary']['Failed'] == 0:
        return True
    else:
        return False