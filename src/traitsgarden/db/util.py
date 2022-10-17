"""Utility functions"""
import re

def convert_to_inches(entry):
    """Convert a str representation into numerical inches."""
    num = float(re.findall(r"^\d*[.,]?\d*", entry)[0])
    if ("'" in entry) or ("ft" in entry):
        num = num * 12
    return num

def increment_char(c):
    """Increment an uppercase character, returning 'A' if 'Z' is given
    """
    return chr(ord(c) + 1) if c != 'Z' else 'A'

def increment_str(s):
    """Increment alphabetically.
    A -> B
    Z -> AA
    AA -> AB
    """
    lpart = s.rstrip('Z')
    num_replacements = len(s) - len(lpart)
    new_s = lpart[:-1] + increment_char(lpart[-1]) if lpart else 'A'
    new_s += 'A' * num_replacements
    return new_s

def sort_incremented(strlist):
    """Sort the list of strings in the incremented order.
    A, B, C, AA, AB, CA,
    """
    strlist = list(strlist)
    strlist.sort()
    strlist.sort(key=len)
    return strlist
