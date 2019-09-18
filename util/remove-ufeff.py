import csv


def main():
    file_name = 'files/sp500_constituents.csv'
    file_as_string = ''

    with open(file_name, 'r') as file:
        file_as_string = file.read()

    file_replaced = file_as_string.replace('\ufeff', '')

    with open(file_name, 'w') as file:
        file.write(file_replaced)


if __name__ == '__main__':
    main()