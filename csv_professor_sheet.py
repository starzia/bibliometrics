import csv
from professor import Professor

CSV_FILENAME = "professors.csv"


class SpreadSheet:

    def __init__(self):
        self.rows = []
        with open(CSV_FILENAME, 'rt', encoding="UTF-8") as csv_file:
            reader = csv.reader(csv_file, delimiter=',', quotechar='"')
            for row in reader:
                self.rows.append(row)
        print("read %d rows" % len(self.rows))

    def read_profs(self):
        """:return: a list of Professor objects"""
        profs = []
        saw_header = False;
        for row in self.rows:
            if not saw_header:
                saw_header = True
                continue
            profs.append(Professor.from_spreadsheet_row(row))
        return profs

    def save_file(self):
        with open(CSV_FILENAME, 'wt', encoding="UTF-8") as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for row in self.rows:
                writer.writerow(row)

    def save_prof(self, prof):
        new_row = prof.spreadsheet_row()
        row_idx = self.find_prof(prof)
        if row_idx is None:
            self.rows.append(new_row)
        else:
            # update row
            print("WARNING: %s not found, creating a new row" % prof.slug())
            self.rows[row_idx] = new_row
        self.save_file()

    def update_profs(self, profs):
        for p in profs:
            self.save_prof(p)

    def append_profs(self, profs):
        """!!!: only call this if all the profs are new.  It will not try to update any rows, just append to the bottom."""
        self.rows = [p.spreadsheet_row() for p in profs]
        self.save_file()

    def find_prof(self, prof):
        """:return the row number of a professor or none if he's not found."""
        for i, row in enumerate(self.rows):
            if (row[0] == prof.slug()):
                return i
        return None
