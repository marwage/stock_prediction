import argparse


def remove_ufeff(path):
    with open(path, "r") as file:
        file_as_string = file.read()

    file_replaced = file_as_string.replace("\ufeff", "")

    with open(path, "w") as file:
        file.write(file_replaced)


def main():
    remove_ufeff(args.path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remove unicode ufeff")
    parser.add_argument("path", type=str,
                        help="Path to file")
    args = parser.parse_args()

    main()
