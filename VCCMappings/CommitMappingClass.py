import git


class CommitMapping:
    """Class for abstraction of a mapping between cve and commit.
    Stores the commit and its identifier (sha) as well as the associated mapping type and a list of corresponding CVEs and VCCS"""
    def __init__(self, commit: git.Commit, mapping_type: str):
        self.id = commit.hexsha
        self.commit = commit
        self.cves = []
        self.vccs = []
        self.mapping_type = mapping_type
