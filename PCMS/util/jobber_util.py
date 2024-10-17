ITEM_MAP = {
    "1ft straight bracket": "1S",
    "2ft straight bracket": "2S",
    "2ft wwe": "2W",
    "3ft straight bracket": "3S",
    "3ft wwe": "3W",
    "3.5ft straight bracket": "3.5S",
    "4ft straight bracket": "4S",
    "4ft wwe": "4W",
    "4.5ft straight bracket": "4.5S",
    "5ft straight bracket": "5S",
    "5ft wwe": "5W",
    "6ft straight bracket": "6S",
    "7ft straight bracket": "7S",
    "8ft straight bracket": "8S",
    "9ft straight bracket": "9S",
    "10ft straight bracket": "10S",
    "2ft corner bracket": "2C",
    "3ft corner bracket": "3C",
    "4ft corner bracket": "4C",
    "5ft corner bracket": "5C",
    "6ft corner bracket": "6C",
    "7ft corner bracket": "7C",
    "6ft garage bracket": "6G",
    "7ft garage bracket": "7G",
    "8ft garage bracket": "8G",
    "7ft hd bracket": "7HD",
    "8ft hd bracket": "8HD",
    "9ft hd bracket": "9HD",
    "10ft hd bracket": "10HD",
    "4ft hump": "4H"
}


def valid_job_item(line: str) -> bool:
    ft_list = ["1ft", "2ft", "3ft", "3.5ft", "4ft", "4.5ft", "5ft", "6ft", "7ft", "8ft", "9ft", "10ft"]
    if not any(ft in line.replace(" ", "") for ft in ft_list):
        return False
    else:
        return True
