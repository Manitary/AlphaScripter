import tkinter as tk

from src.config import CONFIG
from src import main as m
from src.models import AI


def read_and_write(ai_name: str) -> None:
    a = AI.from_file(ai_name)
    a.export("best")


def create_app() -> tk.Tk:
    root = tk.Tk()

    input_txt = tk.Text(root, height=1, width=15)
    input_txt.pack()

    input_txt_2 = tk.Text(root, height=1, width=15)
    input_txt_2.pack()

    button1 = tk.Button(
        root,
        text="Self train infinite",
        command=lambda: m.run_vs_self(
            0, True, int(input_txt_2.get(1.0, "end-1c")), True
        ),
    )
    button1.pack()

    button1 = tk.Button(
        root,
        text="Self train one round",
        command=lambda: m.run_vs_self(
            0, True, int(input_txt_2.get(1.0, "end-1c")), False
        ),
    )
    button1.pack()

    button1 = tk.Button(
        root,
        text="Other train infinite",
        command=lambda: m.run_vs_other(
            0,
            True,
            input_txt.get(1.0, "end-1c"),
            [CONFIG.civ, CONFIG.civ],
            int(input_txt_2.get(1.0, "end-1c")),
            True,
        ),
    )
    button1.pack()

    button1 = tk.Button(
        root,
        text="Other train one round",
        command=lambda: m.run_vs_other(
            0,
            True,
            input_txt.get(1.0, "end-1c"),
            [CONFIG.civ, "huns"],
            int(input_txt_2.get(1.0, "end-1c")),
            False,
        ),
    )
    button1.pack()

    button1 = tk.Button(
        root, text="FFA new start", command=lambda: m.run_ffa(5000, False)
    )
    button1.pack()

    button1 = tk.Button(root, text="FFA load", command=lambda: m.run_ffa(0, True))
    button1.pack()

    button1 = tk.Button(root, text="Save AI", command=m.backup)
    button1.pack()

    button1 = tk.Button(
        root,
        text="Benchmark",
        command=lambda: m.benchmarker(
            "best", input_txt.get(1.0, "end-1c"), 100, [CONFIG.civ, "huns"]
        ),
    )
    button1.pack()

    button1 = tk.Button(
        root,
        text="Ladder",
        command=lambda: m.group_train(
            CONFIG.ai_ladder, True, int(input_txt_2.get(1.0, "end-1c"))
        ),
    )
    button1.pack()

    input_txt_3 = tk.Text(root, height=1, width=15)
    input_txt_3.pack()

    button1 = tk.Button(
        root,
        text="Write AI",
        command=lambda: read_and_write(input_txt_3.get(1.0, "end-1c")),
    )
    button1.pack()

    button1 = tk.Button(
        root,
        text="Speed score",
        command=lambda: m.speed_train(input_txt.get(1.0, "end-1c")),
    )
    button1.pack()

    button1 = tk.Button(root, text="ELO Train", command=m.elo_train)
    button1.pack()

    button1 = tk.Button(
        root,
        text="Other train slow",
        command=lambda: m.run_vs_other_slow(
            0, True, input_txt.get(1.0, "end-1c"), ["huns", "huns"], 40, True
        ),
    )
    button1.pack()

    button1 = tk.Button(
        root,
        text="Self train slow",
        command=lambda: m.run_vs_self_slow2(
            0, True, int(input_txt_2.get(1.0, "end-1c")), True
        ),
    )
    button1.pack()

    button1 = tk.Button(
        root,
        text="Run Robin",
        command=lambda: m.run_robin(int(input_txt_2.get(1.0, "end-1c"))),
    )
    button1.pack()

    button1 = tk.Button(
        root,
        text="Run vs selfs",
        command=lambda: m.run_vs_selfs(
            0, True, int(input_txt_2.get(1.0, "end-1c")), True
        ),
    )
    button1.pack()
    return root


def main() -> None:
    root = create_app()
    root.mainloop()


if __name__ == "__main__":
    main()
