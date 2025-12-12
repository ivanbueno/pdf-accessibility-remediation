from pdfixsdk import *
from Utils import inputPath, outputPath

def FixPDF(inputPdfPath: str, outputPdfPath: str):
    # print(f"Remediating: {inputPdfPath}")
    commandPath = inputPath + "/make-accessible.json"

    # Open the PDF document
    pdfix  = GetPdfix()
    if pdfix is None:
        print('Pdfix Initialization fail')

    doc = pdfix.OpenDoc(inputPdfPath, "")
    if doc is None:
        print('Unable to open pdf : ' + pdfix.GetError())

    command = doc.GetCommand()

    cmdStm = pdfix.CreateFileStream(commandPath, kPsReadOnly)
    # cmdStm = pdfix.CreateMemStream()
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
    # print(f"Remediation completed: {outputPdfPath}")
