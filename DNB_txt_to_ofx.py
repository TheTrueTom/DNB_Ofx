import time
import hashlib
import os

def strip_non_ascii(string):
    stripped = (c for c in string if 0 < ord(c) < 127)
    return ''.join(stripped)

def treatLine(line):
	cleanLine = strip_non_ascii(line)
	cleanLine = cleanLine.translate(None, '\"')
	cleanLine = cleanLine.translate(None, '\r')
	cleanLine = cleanLine.translate(None, '\n')
	elements = cleanLine.split(";")

	date = time.strptime(elements[0], "%d.%m.%Y")
	description = elements[1]
	value = 0

	if len(elements[3]) == 0:
		value = float(elements[4].translate(None, ','))
	else:
		value = -float(elements[3].translate(None, ','))

	operationHash = (hashlib.sha1(cleanLine.encode())).hexdigest()
	
	return (date, description, value, operationHash)

def readOperationsFromFile(filename):
	file = open(filename, 'r')

	operations = []
	i = 0

	for line in file:
		if i != 0:
			operations.append(treatLine(line))
		i+= 1

	file.close()

	print("Read " + str(i-1) + " operations")
	print("Stored " + str(len(operations)) + " operations")

	return operations

def writeHeadersToFile(filename, operations):
	file = open(filename, 'w')

	startDate = operations[0][0]
	endDate = operations[len(operations) - 1][0]

	header = "<OFX>\n<SIGNONMSGSRSV1>\n<SONRS>\n<STATUS>\n<CODE>0\n<SEVERITY>INFO\n</STATUS>\n"
	header += "<DTSERVER>20160101000000"
	header += "<LANGUAGE>FRA\n</SONRS></SIGNONMSGSRSV1>\n<BANKMSGSRSV1>\n<STMTTRNRS>\n<TRNUID>69027900210"
	header += "<STATUS>\n<CODE>0\n<SEVERITY>INFO\n</STATUS>\n<STMTRS>\n<CURDEF>NOK\n<BANKACCTFROM>\n"
	header += "<BANKID>16006\n<BRANCHID>36011\n<ACCTID>69027900210\n<ACCTTYPE>CHECKING\n</BANKACCTFROM>\n<BANKTRANLIST>\n"
	header += "<DTSTART>" + time.strftime("%Y%m%d%H%M%S", startDate) + "\n"
	header += "<DTEND>" + time.strftime("%Y%m%d%H%M%S", endDate) + "\n"

	file.write(header)
	file.close()

def writeFooterToFile(filename):
	file = open(filename, 'a')

	footer = "</BANKTRANLIST>\n</STMTRS>\n</STMTTRNRS>\n</BANKMSGSRSV1>\n</OFX>\n"

	file.write(footer)
	file.close()

def writeOperationsToFile(filename, operations):
	file = open(filename, 'a')

	operationsList = sorted(operations, key=lambda tup: tup[0])

	counter = 0

	for operation in operationsList:
		operationString = "<STMTTRN>\n<TRNTYPE>OTHER\n"
		operationString += "<DTPOSTED>" + time.strftime("%Y%m%d", operation[0]) + "\n"
		operationString += "<TRNAMT>" + str(operation[2]) + "\n"
		operationString += "<FITID>" + operation[3] + "\n"
		operationString += "<NAME>" + operation[1] + "\n"
		operationString += "<MEMO> \n</STMTTRN>\n"

		file.write(operationString)
		counter += 1

	file.close()

	print("Wrote " + str(counter) + " operations")

for root, subfolders, files in os.walk("input"):
	for file in files:
		if file[-3:] == 'txt':
			outputFilename = file[:-3] + 'ofx'
			outputPath = os.path.join('output',outputFilename)

			operations = readOperationsFromFile(os.path.join('input',file))
			writeHeadersToFile(outputPath, operations)
			writeOperationsToFile(outputPath, operations)
			writeFooterToFile(outputPath)

