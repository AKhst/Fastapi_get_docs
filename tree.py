import os


def print_directory_structure(root_dir, indent=""):
    for item in os.listdir(root_dir):
        item_path = os.path.join(root_dir, item)
        print(indent + item)
        if os.path.isdir(item_path):
            print_directory_structure(item_path, indent + "    ")


project_root = (
    "/Users/admin/PycharmProjects/Fastapi_get_docs/"  # Укажите путь к вашему проекту
)
print_directory_structure(project_root)
