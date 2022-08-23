# Utility functions module.

# Returns the line at the given position in the given text.
def getLine(text, position):
    # Find the start of the line
    for startPosition in range(position, 0, -1):
        if text[startPosition] == "\n":
            break

    # Find the end of the line
    for endPosition in range(position, len(text)):
        if text[endPosition] == "\r":
            break

    return text[startPosition:endPosition]
