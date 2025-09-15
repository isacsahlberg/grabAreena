# playground_2.py
from playground import fetch_schedule  # reuse your fetch+cache
from json_adapter import json_to_legacy_structs
from grabAreena_functions import getPieces, massagePieces, printAllPieces

if __name__ == "__main__":
    CHANNEL = "yle-klassinen"
    DATE = "2025-09-14"

    data = fetch_schedule(CHANNEL, DATE, force=False)
    programs, program_times, program_contents, endtime = json_to_legacy_structs(data)

    # Flatten all pieces for the day using your existing helpers
    pieces = []
    for content in program_contents:
        pieces.extend(getPieces(content))
    pieces = massagePieces(pieces, addMorningPlus=True)

    printAllPieces(pieces)
