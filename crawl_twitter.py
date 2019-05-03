import csv


def main():
    # [(name, symbol)]
    sp500 = []

    with open('sp500.csv', 'r') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=';')
        for row in csv_reader:
           assert len(row) == 2
           sp500.append((row[0].replace('\ufeff', ''), row[1]))

    #next


if __name__ == '__main__':
    main()