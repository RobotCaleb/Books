# coding=utf-8
import re
import datetime
from collections import OrderedDict

good_star = "★"
bad_star = "☆"


class PrependOrderedDict(OrderedDict):
    def prepend(self, key, value, dict_setitem=dict.__setitem__):

        root = self._OrderedDict__root
        first = root[1]

        if key in self:
            link = self._OrderedDict__map[key]
            link_prev, link_next, _ = link
            link_prev[1] = link_next
            link_next[0] = link_prev
            link[0] = root
            link[1] = first
            root[1] = first[0] = link
        else:
            root[1] = first[0] = self._OrderedDict__map[key] = [root, first, key]
            dict_setitem(self, key, value)


class BookData:
    def __init__(self):
        self.comments = []
        self.sections = PrependOrderedDict()

    def __str__(self):
        ret = "# Books\n"
        for c in self.comments:
            ret += c
            ret += "\n"
        ret += "\n"
        for s in self.sections:
            ret += self.sections[s].__str__()
        return ret

    def append_section(self, section):
        self.sections[section.title] = section
        return self.get_section(section.title)

    def prepend_section(self, section):
        self.sections.prepend(section.title, section)
        return self.get_section(section.title)

    def get_section(self, title):
        return self.sections[title]

    def append_comment(self, comment):
        self.comments.append(comment)


class Section:
    def __init__(self, title):
        self.title = title
        self.books = []
        self.comments = []

    def __str__(self):
        ret = "### " + self.title
        ret += "\n"
        for b in self.comments:
            ret += b
            ret += "\n"
        ret += "\n"
        print_book = False
        for b in self.books:
            ret += b.__str__()
            print_book = True
        if print_book:
            ret += "\n"
        return ret

    def append_book(self, book):
        self.books.append(book)

    def prepend_book(self, book):
        self.books.insert(0, book)

    def append_comment(self, comment):
        self.comments.append(comment)


class Book:
    def __init__(self):
        self.title = ""
        self.author = ""
        self.rating = 0
        self.comments = []

    def __str__(self):
        ret = "* `" + self.author + "` "
        ret += self.title
        ret += " ("
        ret += good_star * self.rating
        ret += bad_star * (5 - self.rating)
        ret += ")\n"

        for c in self.comments:
            ret += "    * "
            ret += c
            ret += "\n"
        return ret


def new_book(cur_section=None, bi=None):
    if bi and bi.title != "":
        cur_section.append_book(bi)
    return Book()


class Loader:
    def __init__(self):
        self.cur_section = None
        self.sections = {}

        self.book_instance = None
        self.data = BookData()

    def process(self):
        books_file = open("Readme.md")

        auth_title_rating_regex = ur"\*\ \`(.*)\`\ (.*)\ \((.*)\)"

        while True:
            line = books_file.readline()
            if not line:
                break

            line = line.rstrip()

            if line == "":
                continue

            # start
            elif line.startswith("# Books"):
                self.data = BookData()

            # section
            elif line.startswith("### "):
                self.book_instance = new_book(self.cur_section, self.book_instance)
                section_name = line.split("### ")[1]
                self.cur_section = self.data.append_section(Section(section_name))

            # book
            elif line.startswith("* "):
                self.book_instance = new_book(self.cur_section, self.book_instance)
                matches = re.match(auth_title_rating_regex, line)
                author = matches.group(1)
                cur_title = matches.group(2)
                rating = matches.group(3).count(good_star)
                self.book_instance.title = cur_title
                self.book_instance.author = author
                self.book_instance.rating = rating

            # comment on book
            elif line.startswith("    *"):
                comment = line.split("    * ")[1]
                self.book_instance.comments.append(comment)

            # comment on section
            elif self.cur_section is not None and line != "":
                self.cur_section.append_comment(line)

            # comment on all
            elif self.cur_section is None and line != "":
                self.data.append_comment(line)

        books_file.close()

        new_book(self.cur_section, self.book_instance)

        return self.data


def get_updates(book_data):
    update = raw_input("Would you like to add a book? [y/n]: ")
    if update == "y" or update == "Y":
        while True:
            year = datetime.datetime.now().year.__str__()
            section = raw_input("Which section [" + year + "]: ")
            if not section:
                section = year
            cur_section = None
            if section in book_data.sections:
                cur_section = book_data.get_section(section)
            else:
                cur_section = book_data.prepend_section(Section(section))
            title = raw_input("Title: ")
            author = raw_input("Author: ")
            rating = raw_input("Rating (0-5): ")
            if title and author and rating:
                comments = []
                while True:
                    c = raw_input("Comments (blank line to end): ")
                    if not c:
                        break
                    comments.append(c)
                book = Book()
                book.title = title
                book.author = author
                book.rating = int(rating)
                if len(comments):
                    book.comments = comments
                print("\n")
                print("Section: " + section)
                print("-------------------------")
                print(book.__str__())
                print("\n")
                right = raw_input("Would you like to redo this book? [y/n]")
                if right == "y" or right == "Y":
                    continue
                else:
                    cur_section.prepend_book(book)
                another = raw_input("Would you like to add another book? [y/n]")
                if another == "y" or another == "Y":
                    continue
                else:
                    return


def save(book_data, file):
    f = open(file, "w")
    f.write(book_data.__str__())
    f.close()


m = Loader()
data = m.process()
get_updates(data)
save(data, "Readme.md")
