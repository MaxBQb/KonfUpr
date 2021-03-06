import os
from xml.etree import ElementTree
from urllib.request import urlopen
from urllib.parse import quote
DEBUG = False


def get_package_link(name,
                     version='latest',
                     simple_index='https://pypi.org/simple/'):
    try:
        with urlopen(simple_index + name + '/', timeout=25) as f:
            tree = ElementTree.parse(f)
    except:
        if DEBUG:
            print("ERROR LINK - - - - - :", name)
        return None
    packages = {a.text: a.attrib['href'] for a
                in tree.iter('a')
                if a.text.endswith(".whl")}
    if version == 'latest':
        packages = list(packages.values())
        if not len(packages):
            return ""
        return packages[-1]
    for full_package_name in packages:
        if version in full_package_name:
            return packages[full_package_name]
    return ""


def get_dependencies(package_link: str):
    from zipfile import ZipFile
    from io import BytesIO

    try:
        with urlopen(package_link, timeout=25) as f:
            package_whl = f.read()
    except:
        return []
    package_whl = ZipFile(BytesIO(package_whl))
    with package_whl.open([e for e in package_whl.namelist()
                           if 'METADATA' in e][0]) as f:
        package_info = f.read().decode('utf-8')

    return list({e.replace(';', ' ')
                  .replace('<', ' ')
                  .replace('=', ' ')
                  .replace('>', ' ').split(' ')[1].split('[')[0]
                 for e in package_info.split('\n')
                 if e.startswith("Requires-Dist:")
                 and " extra " not in e
                 })


def build_dependency_graph(package_name):
    packages = set()
    graph = []
    max_lvl = [0, 0]

    def get_tree(package_name, lvl=1):
        package_link = get_package_link(package_name)
        if package_link is None:
            return
        packages.add(package_name)
        deps = get_dependencies(package_link)
        max_lvl[1] += len(deps)
        if deps:
            graph.append(''.join(['"{}"->"{}";'.format(package_name, e)
                                  for e in deps]))
        if DEBUG:
            if deps:
                print(lvl, package_name, f"({len(deps)})")
            else:
                print(lvl, package_name)
            max_lvl[0] = max(max_lvl[0], lvl)
        for e in deps:
            if e not in packages:
                get_tree(e, lvl+1)
    get_tree(package_name)
    if DEBUG:
        print("Самая длинная зависимость:", max_lvl[0])
        print("Всего пакетов:", len(packages))
        print("Всего связей:", max_lvl[1])
    if len(packages) == 1:
        graph.append(package_name)
    return 'digraph G {'+'\n'.join(graph)+'}', len(packages)


def main():
    package_name = input("Введите название пакета: ")
    package_graph, packages_count = build_dependency_graph(package_name)
    if not packages_count:
        print('Пакет не найден')
        return
    print("<--------------------------------------------------->")
    if packages_count < 130 \
            and 'Y' == input('Получить файлом? [Y/N]: ').upper():
        package_graph = quote(package_graph)
        package_graph = 'https://quickchart.io/graphviz?graph=' + package_graph
        fname = package_name + "_dependencies_graph.svg"
        with open(fname, "wb") as f:
            with urlopen(package_graph) as f2:
                f.write(f2.read())
        os.startfile(fname, 'open')
    else:
        if packages_count > 60:
            print('[https://dreampuf.github.io/GraphvizOnline/] <-- Загрузить текст сюда')
        print(package_graph)
        print('[https://dreampuf.github.io/GraphvizOnline/] <-- Загрузить текст сюда')


if __name__ == '__main__':
    main()
