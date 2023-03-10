import re
from git import GitCommandError
from .HeuristicInterface import HeuristicInterface


class LiPaxsonHeuristic(HeuristicInterface):

    def use_heuristic(self, commit, cve):

        blames_frequencies = {}
        # diff with each parent. Merges might have multiple parents
        for parent in commit.parents:
            diffs = parent.diff(commit, create_patch=True, unified=0)

            for diff in diffs:
                if not (self.is_code_file(diff.a_path) or self.is_code_file(diff.b_path)):
                    continue

                local_changes = str(diff).split("@@ -")
                local_changes.pop(0)
                for local_change in local_changes:
                    lines_and_offset = re.search(r'(.*?) \+(.*?) @@', local_change)
                    deletion_anchor = int(lines_and_offset.group(1).split(",")[0])

                    if diff.a_path:
                        parent_file = self.repo.git.show(parent.hexsha + ":" + diff.a_path).split("\n")
                        parent_comments_and_whitespaces = self.get_comments_and_whitespaces(parent_file)

                    try:
                        deletion_offset = int(lines_and_offset.group(1).split(",")[1])
                    except IndexError:
                        deletion_offset = 1

                    # Blame deletions
                    for i in range(deletion_offset):
                        # check if deleted line was comment/whitespace
                        if (deletion_anchor + i - 1) in parent_comments_and_whitespaces:
                            continue

                        self.blame(blames_frequencies, parent, diff.a_path, deletion_anchor + i)

        return blames_frequencies

    def blame(self, blames, commit, path, line):
        try:
            blamed_commit = self.repo.blame(commit.hexsha, path, L=str(line)+",+1")[0][0]
            if blamed_commit in blames:
                blames[blamed_commit] += 1
            else:
                blames[blamed_commit] = 1
        except GitCommandError:
            print('Blame unsuccessful, line does not exist')
        except KeyError as e:
            print('Key error during blame: {}'.format(str(e)))

    @staticmethod
    def get_comments_and_whitespaces(file):
        comments_and_whitespaces = []
        comment = False
        for line_number, line in enumerate(file):
            # Check for single line comments or empty lines
            stripped_line = line.strip().rstrip()
            if stripped_line == '' or stripped_line[:2] == '//':
                comments_and_whitespaces.append(line_number)

            contains_code = not (comment or stripped_line[:2] == "/*")
            for indx, l in enumerate(stripped_line[:-1]):
                ll = l + stripped_line[indx+1]
                if ll == '/*':
                    comment = True
                if ll == '*/':
                    comment = False
                    if not (indx == len(stripped_line) - 2):
                        contains_code = True

            if not contains_code:
                comments_and_whitespaces.append(line_number)
        return comments_and_whitespaces
