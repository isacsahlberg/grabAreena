# %%
import json
from pathlib import Path
from datetime import date

# from grabAreena.parsing import parse_programs
from parsing import parse_programs

    # # pick a cached file
    # path = Path.home() / ".cache" / "grabareena" / "yle-klassinen" / "2025-09-14.json"
    # # path = Path.home() / ".cache" / "grabareena" / "yle-klassinen" / "2025-09-15.json"
    # data = json.loads(path.read_text(encoding="utf-8"))

# 1. Decide the date (default: today)
# chosen_date = date.today()  # e.g. 2025-09-16
chosen_date = date(2025, 9, 14)

# 2. Format YYYY-MM-DD for the cache path
date_str = chosen_date.isoformat()  # "2025-09-16"

# 3. Construct the cache path
cache_file = Path.home() / ".cache" / "grabareena" / "yle-klassinen" / f"{date_str}.json"

# 4. Load JSON
with cache_file.open(encoding="utf-8") as f:
    data = json.load(f)

programs = parse_programs(data, chosen_date)

for prog in programs:
    print(f"\n{prog}")
    for piece in prog.pieces:
        print(piece)

# %%
