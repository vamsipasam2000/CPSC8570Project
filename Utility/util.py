import re
import warnings
import xml.etree.ElementTree as ET
from typing import List

class ConfigParse:
    """Class for parsing the config XML file"""

    @staticmethod
    def id_extraktion(regex_node: ET.Element, text: str) -> List[str]:
        """
        Extracts a list of IDs from the specified text
        :param regex_node: a regex of the config.xml
        :param text: the text from which to extract an id
        :return: list of ids that were extracted
        """

        type = regex_node.find('./id-extraktion/type').text

        # No extraction need simply return text as is
        if type == "None":
            return [text]

        # Use provided regex to extract the ID(s)
        if type == "Regex":
            res = []
            bug_regex = regex_node.find('./id-extraktion/regex').text
            for bud_ID in re.finditer(bug_regex, text):
                res.append(bud_ID.group(0))
            return res

        # Cutoff part of the result to obtain the ID
        elif type == 'Cut':
            regex = regex_node.find('./id-extraktion/regex').text
            search = re.search(regex, text)
            if search:
                f = search.group(0)
                return [text.replace(f, '')]
        else:
            warnings.warn("ID Extraktion type {0} not supported".format(regex_node.find('./id-extraktion/type').text))

        return None
