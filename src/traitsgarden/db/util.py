"""Utility functions"""
import re

def convert_to_inches(entry):
    """Convert a str representation into numerical inches."""
    num = float(re.findall(r"^\d*[.,]?\d*", entry)[0])
    if ("'" in entry) or ("ft" in entry):
        num = num * 12
    return num
