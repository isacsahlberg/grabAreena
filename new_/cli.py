import argparse
from .parsing import parse_programs

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pattern", "-p", help="search for this string")
    args = parser.parse_args()

    programs = parse_programs("yle-klassinen", "2025-09-14")  # demo
    for prog in programs:
        matches = prog.matches(args.pattern or "Bach")
        for piece in matches:
            print(piece.start, "-", piece.text)

if __name__ == "__main__":
    main()
