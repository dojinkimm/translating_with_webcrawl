from tkinter import *
import json


class AddJson:
    def __init__(self):
        self.tk = Tk()
        self.K1 = Label(self.tk, text="한글")
        self.K2 = Entry(self.tk, bd=2, width=30)
        self.E1 = Label(self.tk, text="English")
        self.E2 = Entry(self.tk, bd=2, width=30)
        with open('app_name.json', "r", encoding="utf-8-sig") as f:
            self.data = json.load(f)
        return

    def open_gui(self):
        self.tk.title("Add Kor-Eng Definition")

        self.K1.pack()
        self.K2.pack(expand=True)
        # fill = X, padx = 5, expand = True

        self.E1.pack()
        self.E2.pack(expand=True)

        self.E2.bind("<Return>", self.get_value)
        self.K2.bind("<Return>", self.get_value)

        draw_button = Button(self.tk, text="Quit", command=self.close_window)
        draw_button.pack()

        self.tk.mainloop()
        return

    def get_value(self, event):
        if self.K2.get() != 0 or self.E2.get() != 0:
            self.data[self.K2.get()] = self.E2.get()
            with open("app_name.json", "w", encoding="utf-8") as f:
                f.write(json.dumps(self.data, ensure_ascii=False, indent=4))
            self.K2.delete(0, END)
            self.E2.delete(0, END)
        return

    def close_window(self):
        self.tk.destroy()
        sys.exit()


if __name__ == "__main__":
    addjson = AddJson()
    addjson.open_gui()
