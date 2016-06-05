import re

def name_parts(name):
    prefix, first, middle, last, suffix = "", "", "", "", ""

    # if we got a name on the form "Hello There (Foo Bar)", get rid of
    # the paranthesized part
    name_with_paren_match = re.search("^([^(]+)\s*\(.*\)$", name)
    if name_with_paren_match:
        name = name_with_paren_match.group(1)

    parts = name.split()
    if len(parts) > 2 and parts[0] in ["M", "M.", "Sri", ] and "." not in parts[1]:
        prefix = parts[0];
        parts = parts[1:]
    if parts[0] in ["Mr", "Mr.", "Mrs", "Mrs.", "Ms", "Ms.", "Miss", "Dr", "Dr.", "Doctor", "Prof", "Prof.", "Professor", "Sir", "Lady", "Dame", ]:
        prefix = parts[0];
        parts = parts[1:]
    if len(parts) > 2:
        if parts[-1] in ["Jr", "Jr.", "II", "2nd", "III", "3rd", "Ph.D."]:
            suffix = parts[-1]
            parts = parts[:-1]
    if len(parts) > 2:
        name = " ".join(parts)
        compound = re.search(" (de|hadi|van|ver|von|el|le|st\.?) ", name.lower())
        if compound:
            pos = compound.start()
            parts = name[:pos].split() + [name[pos+1:]]
    if len(parts) > 2:
        first = parts[0]
        last = parts[-1]
        # Handle reverse-order names with uppercase surname correctly
        if re.search("^[A-Z-]+$", first):
            first, last = last, first
        middle = " ".join(parts[1:-1])
    elif len(parts) == 2:
        first, last = parts
    else:
        last = parts[0]
    return prefix, first, middle, last, suffix
    
def initials(name):
    prefix, first, middle, last, suffix = name_parts(name)
    given = first
    if middle:
        given += " "+middle
    initials = " ".join([ n[0]+'.' for n in given.split() ])
    return initials

if __name__ == "__main__":
    import sys
    name = " ".join(sys.argv[1:])
    print name_parts(name)
    print initials(name)
    
