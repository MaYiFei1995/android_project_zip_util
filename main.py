import fnmatch
import time
import zipfile
import os

import sys

ignore_rule = {}


def init_ignore_rule():
    global ignore_rule
    ignore_rule["dir"] = [".git", ".gradle", ".idea", "build", "captures", ".externalNativeBuild", ".cxx"]
    ignore_rule["file"] = ["*.iml", ".gitignore", "local.properties", ".DS_Store"]


def __start(project_dir: str):
    # 输出文件
    zip_file = zipfile.ZipFile(
        os.path.join(os.getcwd(), "{}_{}".format(os.path.basename(project_dir), int(time.time()))) + ".zip", "w")

    # 开始压缩
    __on_directory(zip_file, os.path.dirname(project_dir), project_dir)

    # 关闭文件
    zip_file.close()


def __on_directory(zip_file: zipfile.ZipFile, base_dir: str, directory: str):
    ignore_config_file = os.path.join(directory, '.gitignore')
    local_ignore_rules = None
    if os.path.exists(ignore_config_file):
        local_ignore_rules = {"dir": [], "file": []}
        print("读取 {}\\.gitignore".format(directory))
        for line in open(ignore_config_file).readlines():
            line = line.replace("\n", "")
            if not line == "":
                if line.endswith("/"):
                    rule = line[0:len(line) - 1]
                    if rule.startswith("/"):
                        rule = rule[1:len(rule)]
                    local_ignore_rules["dir"].append(rule)
                else:
                    local_ignore_rules["file"].append(line)

    for dir_or_file in os.listdir(directory):
        file_path = os.path.join(directory, dir_or_file)
        if os.path.isfile(file_path):
            # 匹配当前目录的忽略规则
            is_skip = False
            if local_ignore_rules is not None:
                for rule in local_ignore_rules["file"]:
                    if fnmatch.fnmatch(dir_or_file, rule):
                        # 匹配为忽略文件，跳过
                        print("skip file:{}".format(file_path))
                        is_skip = True
                        break
            # 匹配全局的忽略规则
            if not is_skip:
                global ignore_rule
                for rule in ignore_rule["file"]:
                    if fnmatch.fnmatch(dir_or_file, rule):
                        # 匹配为忽略文件，跳过
                        print("skip file:{}".format(file_path))
                        is_skip = True
                        break

            # 添加到压缩文件中
            if not is_skip:
                zip_file.write(file_path, __trim_path(base_dir, file_path))

        else:
            # 匹配当前目录的忽略规则
            is_skip = False
            if local_ignore_rules is not None:
                for rule in local_ignore_rules["dir"]:
                    if file_path.__contains__(rule):
                        # 匹配为忽略目录，跳过
                        print("skip dir:{}".format(file_path))
                        is_skip = True
                        break
            if not is_skip:
                for rule in ignore_rule["dir"]:
                    if file_path.__contains__(rule):
                        # 匹配为忽略目录，跳过
                        print("skip dir:{}".format(file_path))
                        is_skip = True
                        break

            # 遍历子目录
            if not is_skip:
                __on_directory(zip_file, base_dir, file_path)


def __trim_path(base_dir: str, path: str):
    """
    zipfile.write的第2个参数需要为相对路径，所以需要转换
    :param base_dir:
    :param path:
    :return:
    """
    # 获取目录名称，前面带有\
    archive_path = path.replace(base_dir, "", 1)
    if base_dir:
        # 去掉第一个字符
        archive_path = archive_path.replace(os.path.sep, "", 1)
    return archive_path


if __name__ == '__main__':
    try:
        target_dir = sys.argv[1]
        print("target dir: {}".format(target_dir))
        if not os.path.exists(target_dir):
            print("路径不存在")
            exit(1)
        init_ignore_rule()
        __start(target_dir)
    except IndexError:
        print("参数解析失败，退出")
        exit(1)
