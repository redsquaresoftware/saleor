# for accessing deep nested json data in a safer way
def safe_get(dct, *keys):
    for key in keys:
        try:
            dct = dct[key]
        except (KeyError, IndexError):
            return None
    return dct

