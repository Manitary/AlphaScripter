import tkinter as tk

from main import backup
from src.models import AI


def write_from_csv(file: str) -> None:
    # parses csv
    with open(file + ".csv", encoding="utf-8") as f:
        data = f.read()

    ai = AI.from_csv(data)
    backup()
    ai.export("best")
    ai.save_to_file("best")


def read(string: str) -> None:
    with open("edittable.csv", "w+", encoding="utf-8") as f:
        f.write(AI.from_file(string).to_csv())


def swap(name1: str, name2: str) -> None:
    ai1 = AI.from_file(name1)
    ai2 = AI.from_file(name2)
    ai1.rules = ai2.rules
    ai1.export("best")
    ai1.save_to_file("best")


# a = generate_ai()
# save_ai(a,"test")
# read("test")
# write_from_csv("edittable")


def create_app() -> tk.Tk:
    root = tk.Tk()

    input_txt = tk.Text(root, height=1, width=15)
    input_txt.pack()

    button1 = tk.Button(
        root, text="edit", command=lambda: read(input_txt.get(1.0, "end-1c"))
    )
    button1.pack()

    input_txt2 = tk.Text(root, height=1, width=15)
    input_txt2.pack()

    button2 = tk.Button(
        root,
        text="commit ai",
        command=lambda: write_from_csv(input_txt2.get(1.0, "end-1c")),
    )
    button2.pack()

    input_txt3 = tk.Text(root, height=1, width=15)
    input_txt3.pack()
    input_txt4 = tk.Text(root, height=1, width=15)
    input_txt4.pack()

    button2 = tk.Button(
        root,
        text="swap complex",
        command=lambda: swap(
            input_txt3.get(1.0, "end-1c"), input_txt4.get(1.0, "end-1c")
        ),
    )
    button2.pack()
    return root


def main() -> None:
    app = create_app()
    app.mainloop()


if __name__ == "__main__":
    main()
