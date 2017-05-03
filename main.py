import re
import csv
from dependency import Dependency, License
from bs4 import BeautifulSoup

import requests

URL_CONSTANT = 'https://mvnrepository.com/artifact/'

# The first task is it to run the mvn dependency:list command. For now, let's assume that the user has already run it.
# We will be asking the user the location of the output of the dependency:list command

groupToSkip = raw_input("Please give a group to skip if any\n")  # 'com.zapstitch'
fileToOpen = raw_input(
    "Please give the path to the dependency:list output command\n")  # '/Users/user/Desktop/dependencies.txt'
with open(fileToOpen) as mvn:
    mvnOutput = mvn.readlines()
    dependencyList = set()
    evaluateDependency = False
    skipPattern = re.compile('\[INFO\]\s+\n')
    for line in mvnOutput:
        if 'The following files have been resolved:' in line:
            # This is our starting grid for the dependency
            evaluateDependency = True
        elif evaluateDependency:
            if not skipPattern.match(line):
                matchObj = re.match(r'\[INFO\]\s+([\w.\-_]+):([\w.\-_]+):\w+:([\w.\-_]+):(\w+)', line)
                if matchObj.group(1) in groupToSkip:
                    continue
                dependencyToAdd = Dependency(groupId=matchObj.group(1), artifactId=matchObj.group(2), versionId=matchObj.group(3), scope=matchObj.group(4))
                dependencyList.add(dependencyToAdd)
            else:
                evaluateDependency = False

print 'Unique dependencies ' + str(len(dependencyList)) + '\n'

# Now we have the list of dependencies... let's get the info about them from the maven central
for dependency in dependencyList:
    print dependency.name()
    urlToHit = URL_CONSTANT + str(dependency.groupId) + "/" + str(dependency.artifactId) + "/" + str(dependency.versionId)
    resp = requests.get(urlToHit)
    response = resp.text
    soup = BeautifulSoup(response, "html.parser")
    try:
        allLicenseRow = []
        for vS in soup.find_all('div', class_='version-section'):
            if 'Licenses' in vS.find('h2').get_text():
                allLicenseRow = vS.find('table').find('tbody').find_all('tr')
                break

        for licenseRow in allLicenseRow:
            cells = licenseRow.find_all("td")
            dependency.addLicense(License(cells[0].get_text(), cells[1].get_text()))
    except Exception as e:
        print 'Failed for this ' + dependency.name()

# We are now going to print all this to a file
with open("output.csv", "w") as out:
    writer = csv.writer(out, delimiter='\t')

    for dependency in dependencyList:
        if len(dependency.licenses) > 0:
            writer.writerow([dependency.groupId + ':' + dependency.artifactId, dependency.versionId, dependency.licenses[0].name, dependency.licenses[0].link])
        else:
            writer.writerow([dependency.groupId + ':' + dependency.artifactId, dependency.versionId, '', ''])
