"""Run Urva.

    python main.py            # voice mode ("Hey Urva ...")
    python main.py --text     # type commands instead (no mic needed)
"""
import argparse

from urva.assistant import Urva


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--text", action="store_true", help="keyboard mode")
    args = p.parse_args()
    urva = Urva()
    if not args.text:
        from urva.voice import run
        run(urva)
        return
    print("Urva (text mode). Try: analyze sample_data/sales.csv · make a presentation · "
          "add review the budget · what's pending · quit")
    while (cmd := input("you> ").strip()).lower() not in {"quit", "exit"}:
        if cmd:
            print("urva>", urva.handle(cmd))


if __name__ == "__main__":
    main()
