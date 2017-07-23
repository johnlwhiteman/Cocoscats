import ast
import re

class Text():

    @staticmethod
    def getTextOnly(something):
        if Text.isNothing(something):
            return ""
        return something.strip()

    @staticmethod
    def isNothing(something):
        return something is None or str(something).strip() == ""

    @staticmethod
    def isValidPathName(something):
         return not re.search(r'[^A-Za-z0-9_\-\\]', something)

    @staticmethod
    def isTrue(something):
        if Text.isNothing(something):
            return False
        return Text.toTrueOrFalse(something) == True

    @staticmethod
    def toTrueOrFalse(something):
        return ast.literal_eval(something)