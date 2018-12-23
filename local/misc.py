


def get_unique_name(names_list, name_template):
    pattern = re.compile(r"\w+_(\d+)")
    num = 0
    for name in names_list:
        if name_template in name:
            match = pattern.search(name)
            if match:
                num = int(match.group(1))

    unique_name = f"{name_template}_{num+1}"
    return unique_name
