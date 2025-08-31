import re


def find_matches(text):
    pattern = r'^(?!.*唐三.*“.*”).*“(.*?)”.*$(?<!唐三)'
    return re.findall(pattern, text)

if __name__ == "__main__":
    text = [
        '突然，唐三脸色骤然一变，但很快又释然了，有些苦涩的自言自语道：“该来的终究还是来了。”',
        '“等一下。”唐大先生终于反应了过来，但是，此时他再说什么都已经晚了。',
        '二长老一呆，“可是，他偷学了本门……”啊阿斯顿唐三'
    ]

    for item in text:
        matches = find_matches(item)
        if matches:
            print(f"Matches found in '{item}': {matches}")
