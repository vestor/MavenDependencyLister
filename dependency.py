class License(object):
    def __init__(self, name, link):
        self.name = name
        self.link = link


class Dependency(object):
    def __init__(self, groupId, artifactId, versionId, scope):
        self.licenses = []
        self.groupId = groupId
        self.artifactId = artifactId
        self.versionId = versionId
        self.scope = scope

    def addLicense(self, license):
        self.licenses.append(license)

    def addLicenseWithName(self, lName, lLink):
        self.licenses.append(License(name=lName, link=lLink))

    def name(self):
        return self.groupId + ':' + self.artifactId + ':' + self.versionId

    def __repr__(self):
        return "Dependency(%s, %s, %s)" % (self.groupId, self.artifactId, self.versionId)

    def __hash__(self):
        return hash(self.__repr__())

    def __eq__(self, other):
        if isinstance(other, Dependency):
            return (self.versionId == other.versionId) and (self.groupId == other.groupId) and (self.artifactId == other.artifactId)
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


