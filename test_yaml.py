import yaml
import json

data = {}


def print_yaml_formatted_json_style(file_path):
    global data
    with open(file_path, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    # 使用 json.dumps 格式化输出，支持缩进和排序
    print(json.dumps(data, indent=2, ensure_ascii=False))


print_yaml_formatted_json_style("config.yaml")


# print(data["root"][0]["root1"])
