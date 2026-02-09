#!env python3
import argparse
import random

def add_text(f):
    text = "Lorem ipsum dolor sit amet, \
consectetur adipiscing elit, sed do \
eiusmod tempor incididunt ut labore \
et dolore magna aliqua. Ut enim ad\n\
minim veniam, quis nostrud exercitation \
ullamco laboris nisi ut aliquip ex ea \
commodo consequat. Duis aute irure dolor \
in reprehenderit in voluptate velit esse\n\
cillum dolore eu fugiat nulla pariatur. \
Excepteur sint occaecat cupidatat non \
proident, sunt in culpa qui officia \
deserunt mollit anim id est laborum.\n<p>\n"
    f.write(text)

def add_headers(f):
    f.write("<!DOCTYPE html>\n<html>\n<body>\n")

def add_footers(f):
    f.write("</body>\n</html>\n")

def add_link(f, lnk):
    f.write(f"<a HREF=\"{lnk}.html\"> This is a link </a>\n<p>\n")

def generate_file(idx, max_refs, num_files):
    fname = str(idx) + ".html"
    with open(fname, 'w', encoding="utf-8") as f:
        add_headers(f)

        # 🔧 FIX: ensure at least 1 outgoing link (no dangling nodes)
        num_refs = random.randrange(1, max_refs)

        for _ in range(num_refs):
            add_text(f)
            lnk = random.randrange(0, num_files)
            add_link(f, lnk)

        add_footers(f)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--num_files', type=int, default=10000)
    parser.add_argument('-m', '--max_refs', type=int, default=250)
    args = parser.parse_args()

    random.seed(0)
    print("Generating", args.num_files, "files")

    for i in range(args.num_files):
        generate_file(i, args.max_refs, args.num_files)

if __name__ == "__main__":
    main()
