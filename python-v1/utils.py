def format_duration(seconds):
    minutes = int(seconds / 60)
    seconds = seconds - minutes * 60
    hours = int(minutes / 60)
    minutes = minutes - hours * 60
    result = "%ds" % seconds
    if minutes > 0:
        result = ("%dm" % minutes) + " " + result
    if hours > 0:
        result = ("%dh" % hours) + " " + result
    return result
