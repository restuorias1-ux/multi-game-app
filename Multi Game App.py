import tkinter as tk
from tkinter import messagebox
import random

# Multi-game app: Ular Tangga, Tic Tac Toe, Soal Hitung
# Fitur:
# - Navigasi antar permainan tanpa menutup program (game lama di-destroy, tidak numpuk)
# - Fullscreen (F11 untuk toggle, Esc untuk keluar)
# - Background gradasi warna yang memenuhi layar dan tidak tembus saat fullscreen
# - Ular Tangga responsif: papan otomatis menyesuaikan ukuran agar bagian bawah tidak tertutup
# - Saat pemain selesai lempar dadu, ada penanda visual di token pemain (highlight) selama singkat

APP_W, APP_H = 900, 650

# ---------------------------
# Shared UI helpers
# ---------------------------

def paint_gradient(canvas):
    colors = ["#ff6b6b", "#ff9f43", "#feca57", "#1dd1a1", "#54a0ff", "#5f27cd", "#ee5253"]
    h = canvas.winfo_height() or APP_H
    w = canvas.winfo_width() or APP_W
    stripe_h = max(1, h // len(colors))
    canvas.delete("all")
    for i, color in enumerate(colors):
        y0 = i * stripe_h
        y1 = (i + 1) * stripe_h if i < len(colors) - 1 else h
        canvas.create_rectangle(0, y0, w, y1, fill=color, width=0)
    canvas.create_rectangle(0, 0, w, h, fill="#000000", width=0, stipple="gray25")
    for (x, y, r) in [(80, 90, 60), (760, 140, 48), (460, 360, 90), (150, 500, 40)]:
        canvas.create_oval(x - r, y - r, x + r, y + r, outline="", fill="#ffffff")

def fancy_label(parent, text, font=("Helvetica", 22, "bold"), fg="#ffffff", bg="#000000"):
    return tk.Label(parent, text=text, font=font, fg=fg, bg=bg, padx=10, pady=6)

def fancy_button(parent, text, cmd, bg="#34495e", fg="#ffffff"):
    return tk.Button(parent, text=text, command=cmd, font=("Helvetica", 12, "bold"),
                     fg=fg, bg=bg, activebackground="#2c3e50", activeforeground="#ecf0f1",
                     padx=16, pady=10, bd=0)

# ---------------------------
# Main App
# ---------------------------

class MultiGameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi Game App - Colorful")
        self.root.geometry(f"{APP_W}x{APP_H}")
        self.root.resizable(True, True)

        self.fullscreen = False
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.exit_fullscreen)

        self.bg = tk.Canvas(self.root, highlightthickness=0)
        self.bg.pack(fill="both", expand=True)
        self.bg.bind("<Configure>", lambda e: paint_gradient(self.bg))

        self.container = tk.Frame(self.root, bg="#222222")
        self.container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.95, relheight=0.92)

        self.header = fancy_label(self.container, "Multi Game App")
        self.header.pack(pady=(6, 10), fill="x")

        self.status = tk.Label(self.container, text="Selamat datang!",
                               font=("Helvetica", 13, "bold"),
                               fg="#1b1b1b", bg="#ffdd77", padx=10, pady=6)
        self.status.pack(pady=(0, 12), fill="x")

        self.current_view = None
        self.show_menu()

        self.footer = tk.Label(self.container, text="F11: Fullscreen, Esc: Keluar Fullscreen",
                               font=("Helvetica", 10), fg="#ffffff", bg="#333333", padx=8, pady=4)
        self.footer.pack(side="bottom", fill="x")

    def show_menu(self):
        self.clear_view()
        menu = tk.Frame(self.container, bg="#222222")
        menu.pack(expand=True, fill="both")

        fancy_label(menu, "Pilih Permainan").pack(pady=10, fill="x")

        btn_wrap = tk.Frame(menu, bg="#222222")
        btn_wrap.pack(pady=12)
        fancy_button(btn_wrap, "Ular Tangga", self.open_snakes).grid(row=0, column=0, padx=10, pady=10)
        fancy_button(btn_wrap, "Tic Tac Toe", self.open_ttt).grid(row=0, column=1, padx=10, pady=10)
        fancy_button(btn_wrap, "Soal Hitung", self.open_quiz).grid(row=0, column=2, padx=10, pady=10)

        util_wrap = tk.Frame(menu, bg="#222222")
        util_wrap.pack(pady=8)
        fancy_button(util_wrap, "Fullscreen", self.toggle_fullscreen).grid(row=0, column=0, padx=8)
        fancy_button(util_wrap, "Keluar Fullscreen", self.exit_fullscreen).grid(row=0, column=1, padx=8)

        self.current_view = menu
        self.status.config(text="Pilih salah satu permainan.")

    def clear_view(self):
        if self.current_view:
            try:
                self.current_view.destroy()
            except Exception:
                pass
            self.current_view = None

    def open_snakes(self):
        self.status.config(text="Ular Tangga: lempar dadu, naik tangga, turun ular!")
        self.clear_view()
        view = SnakesAndLadders(self.container, self.show_menu, self.open_ttt, self.open_quiz)
        self.current_view = view.frame
        self.current_view.pack(fill="both", expand=True)

    def open_ttt(self):
        self.status.config(text="Tic Tac Toe: tiga sejajar menang!")
        self.clear_view()
        view = TicTacToe(self.container, self.show_menu, self.open_snakes, self.open_quiz)
        self.current_view = view.frame
        self.current_view.pack(fill="both", expand=True)

    def open_quiz(self):
        self.status.config(text="Soal Hitung: jawab cepat dan tepat!")
        self.clear_view()
        view = MathQuiz(self.container, self.show_menu, self.open_snakes, self.open_ttt)
        self.current_view = view.frame
        self.current_view.pack(fill="both", expand=True)

    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)

    def exit_fullscreen(self, event=None):
        self.fullscreen = False
        self.root.attributes("-fullscreen", False)

# ---------------------------
# Snakes & Ladders (responsif, highlight pemain setelah lempar dadu)
# ---------------------------

class SnakesAndLadders:
    def __init__(self, parent, back_cb, goto_ttt, goto_quiz):
        self.frame = tk.Frame(parent, bg="#222222")

        header = fancy_label(self.frame, "Ular Tangga")
        header.pack(pady=(6, 10), fill="x")

        nav = tk.Frame(self.frame, bg="#222222")
        nav.pack(pady=8)
        fancy_button(nav, "Main Tic Tac Toe", goto_ttt).grid(row=0, column=0, padx=5)
        fancy_button(nav, "Main Soal Hitung", goto_quiz).grid(row=0, column=1, padx=5)
        fancy_button(nav, "Kembali Menu", back_cb).grid(row=0, column=2, padx=5)

        self.info = tk.Label(self.frame, text="Giliran: Merah", font=("Helvetica", 13, "bold"),
                             fg="#1b1b1b", bg="#ffdd77", padx=10, pady=6)
        self.info.pack(pady=(0, 8), fill="x")

        # Wrapper untuk canvas agar kita bisa hitung ukuran tersedia
        self.board_wrap = tk.Frame(self.frame, bg="#222222")
        self.board_wrap.pack(pady=8, fill="both", expand=True)

        # Canvas papan (akan di-resize dinamis)
        self.board = tk.Canvas(self.board_wrap, bg="#000000", highlightthickness=0)
        self.board.pack(expand=True, fill="both")

        # Kontrol
        controls = tk.Frame(self.frame, bg="#222222")
        controls.pack(pady=8)
        fancy_button(controls, "Lempar Dadu", self.roll).grid(row=0, column=0, padx=8)
        fancy_button(controls, "Reset", self.reset).grid(row=0, column=1, padx=8)

        # State game
        self.board_size = 10
        self.margin = 12
        self.cell_px = 44  # nilai awal, akan dihitung ulang saat resize
        self.players = ["Merah", "Biru"]
        self.colors = {"Merah": "#e74c3c", "Biru": "#3498db"}
        self.positions = {p: 1 for p in self.players}
        self.turn_idx = 0
        self.game_over = False
        self.ladders = {3: 22, 5: 8, 11: 26, 20: 29, 27: 56, 36: 44}
        self.snakes = {32: 10, 48: 26, 62: 18, 88: 24, 95: 56, 97: 78}
        self.tokens = {}
        self.highlight_item = None  # canvas item id untuk highlight

        # Redraw saat ukuran berubah agar papan selalu muat
        self.board.bind("<Configure>", self.on_resize)
        # Gambar pertama kali
        self.draw_board()

    def on_resize(self, event):
        # Hitung cell_px berdasarkan ruang tersedia agar seluruh papan terlihat
        avail_w = max(1, event.width - self.margin * 2)
        avail_h = max(1, event.height - self.margin * 2)
        self.cell_px = max(20, min(avail_w // self.board_size, avail_h // self.board_size))
        # Set ukuran canvas minimum supaya tidak collapse
        desired_w = self.margin * 2 + self.cell_px * self.board_size
        desired_h = self.margin * 2 + self.cell_px * self.board_size
        # Pastikan canvas cukup besar agar bagian bawah tidak tertutup oleh footer/container
        self.board.config(width=desired_w, height=desired_h)
        # Redraw board dan token
        self.draw_board()

    def idx_to_xy(self, idx):
        idx -= 1
        row = idx // self.board_size
        col = idx % self.board_size
        if row % 2 == 0:
            x = col
        else:
            x = self.board_size - 1 - col
        y = self.board_size - 1 - row
        px = self.margin + x * self.cell_px
        py = self.margin + y * self.cell_px
        return px, py

    def draw_board(self):
        self.board.delete("all")
        palette = ["#2a9d8f", "#e76f51", "#264653", "#f4a261", "#1d3557", "#a8dadc", "#e63946", "#457b9d"]
        # Sel
        for i in range(1, self.board_size**2 + 1):
            x, y = self.idx_to_xy(i)
            color = palette[i % len(palette)]
            self.board.create_rectangle(x, y, x + self.cell_px, y + self.cell_px,
                                        fill=color, width=1, outline="#ffffff")
            self.board.create_text(x + self.cell_px/2, y + self.cell_px/2,
                                   text=str(i), fill="#ffffff", font=("Helvetica", max(8, self.cell_px//5), "bold"))
        # Tangga dan ular
        for s, e in self.ladders.items():
            x1, y1 = self.idx_to_xy(s)
            x2, y2 = self.idx_to_xy(e)
            self.board.create_line(x1+self.cell_px/2, y1+self.cell_px/2,
                                   x2+self.cell_px/2, y2+self.cell_px/2,
                                   fill="#00c853", width=max(2, self.cell_px//8))
        for s, e in self.snakes.items():
            x1, y1 = self.idx_to_xy(s)
            x2, y2 = self.idx_to_xy(e)
            self.board.create_line(x1+self.cell_px/2, y1+self.cell_px/2,
                                   x2+self.cell_px/2, y2+self.cell_px/2,
                                   fill="#ff1744", width=max(2, self.cell_px//8))
        # Token pemain
        # recreate tokens so coords reference valid canvas items after delete
        self.tokens = {}
        for p in self.players:
            self.tokens[p] = self.board.create_oval(0, 0, 0, 0, fill=self.colors[p], outline="")
        self.update_tokens()
        # recreate highlight (if exists) so it's on top
        if self.highlight_item:
            self.board.lift(self.highlight_item)

    def update_tokens(self):
        offset_map = {"Merah": (-8, -8), "Biru": (8, 8)}
        for p in self.players:
            x, y = self.idx_to_xy(self.positions[p])
            dx, dy = offset_map[p]
            r = max(8, self.cell_px // 4)
            self.board.coords(self.tokens[p],
                              x + self.cell_px/2 + dx - r, y + self.cell_px/2 + dy - r,
                              x + self.cell_px/2 + dx + r, y + self.cell_px/2 + dy + r)
        # If highlight exists, move it to the currently highlighted player (if any)
        if self.highlight_item and self.highlight_target in self.players:
            self._position_highlight(self.highlight_target)

    def _position_highlight(self, player):
        # Place an outline (bigger oval) around the player's token
        if player not in self.players:
            return
        # remove old highlight if exists
        try:
            if self.highlight_item:
                self.board.delete(self.highlight_item)
        except Exception:
            pass
        x, y = self.idx_to_xy(self.positions[player])
        r = max(12, self.cell_px // 3)
        hx0 = x + self.cell_px/2 - r
        hy0 = y + self.cell_px/2 - r
        hx1 = x + self.cell_px/2 + r
        hy1 = y + self.cell_px/2 + r
        color = "#ffffff" if player == "Merah" else "#ffffff"
        self.highlight_item = self.board.create_oval(hx0, hy0, hx1, hy1, outline=self.colors[player],
                                                     width=max(3, self.cell_px//12))
        self.highlight_target = player
        # Ensure highlight is below token so token color is visible on top
        self.board.lift(self.tokens[player])
        # keep highlight for a short time then remove (handled by roll)

    def _clear_highlight(self):
        if self.highlight_item:
            try:
                self.board.delete(self.highlight_item)
            except Exception:
                pass
            self.highlight_item = None
            self.highlight_target = None

    def roll(self):
        if self.game_over:
            return
        player = self.players[self.turn_idx]
        d = random.randint(1, 6)
        new_pos = self.positions[player] + d
        if new_pos > 100:
            new_pos = self.positions[player]  # harus tepat di 100
        if new_pos in self.ladders:
            new_pos = self.ladders[new_pos]
        elif new_pos in self.snakes:
            new_pos = self.snakes[new_pos]
        self.positions[player] = new_pos
        self.update_tokens()

        # Visual mark: highlight player token and flash info bg with player's color
        self._clear_highlight()
        self._position_highlight(player)
        old_bg = self.info.cget("bg")
        self.info.config(bg=self.colors[player], fg="#ffffff")
        # schedule removal of highlight and restore info bg after 900 ms
        def restore_mark():
            self._clear_highlight()
            try:
                self.info.config(bg=old_bg, fg="#1b1b1b")
            except Exception:
                pass
        self.board.after(900, restore_mark)

        msg = f"{player} lempar dadu: {d}. Posisi: {new_pos}."
        if new_pos == 100:
            self.info.config(text=f"Pemenang: {player}")
            self.game_over = True
            messagebox.showinfo("Selesai", f"{player} menang!")
        else:
            self.turn_idx = (self.turn_idx + 1) % len(self.players)
            self.info.config(text=f"{msg} Giliran: {self.players[self.turn_idx]}")

    def reset(self):
        self.positions = {p: 1 for p in self.players}
        self.turn_idx = 0
        self.game_over = False
        self._clear_highlight()
        self.update_tokens()
        self.info.config(text="Giliran: Merah", bg="#ffdd77", fg="#1b1b1b")

# ---------------------------
# Tic Tac Toe
# ---------------------------

class TicTacToe:
    def __init__(self, parent, back_cb, goto_snakes, goto_quiz):
        self.frame = tk.Frame(parent, bg="#222222")
        header = fancy_label(self.frame, "Tic Tac Toe")
        header.pack(pady=(6, 10), fill="x")

        nav = tk.Frame(self.frame, bg="#222222")
        nav.pack(pady=8)
        fancy_button(nav, "Main Ular Tangga", goto_snakes).grid(row=0, column=0, padx=5)
        fancy_button(nav, "Main Soal Hitung", goto_quiz).grid(row=0, column=1, padx=5)
        fancy_button(nav, "Kembali Menu", back_cb).grid(row=0, column=2, padx=5)

        self.status = tk.Label(self.frame, text="Giliran: X", font=("Helvetica", 13, "bold"),
                               fg="#1b1b1b", bg="#ffdd77", padx=10, pady=6)
        self.status.pack(pady=(0, 8), fill="x")

        board_wrap = tk.Frame(self.frame, bg="#000000")
        board_wrap.pack(pady=8)

        self.current_player = "X"
        self.board = [""] * 9
        self.game_over = False
        self.winning_line = None

        self.buttons = []
        for r in range(3):
            for c in range(3):
                idx = r * 3 + c
                btn = tk.Button(board_wrap, text="", font=("Helvetica", 28, "bold"),
                                width=4, height=2, bd=0, relief="ridge",
                                activeforeground="#ffffff", activebackground="#444444",
                                fg="#ffffff", bg=self.cell_color(r, c),
                                command=lambda i=idx: self.handle(i))
                btn.grid(row=r, column=c, padx=6, pady=6)
                self.buttons.append(btn)

        controls = tk.Frame(self.frame, bg="#222222")
        controls.pack(pady=8)
        fancy_button(controls, "Reset", self.reset).grid(row=0, column=0, padx=8)

    def cell_color(self, r, c):
        palette = ["#2a9d8f", "#e76f51", "#264653", "#f4a261", "#1d3557", "#a8dadc"]
        return palette[(r * 3 + c) % len(palette)]

    def handle(self, idx):
        if self.game_over or self.board[idx] != "":
            return
        self.board[idx] = self.current_player
        self.buttons[idx].config(text=self.current_player)

        winner = self.check_winner()
        if winner:
            self.status.config(text=f"Pemenang: {winner}")
            self.game_over = True
            self.highlight()
            return

        if "" not in self.board:
            self.status.config(text="Seri!")
            self.game_over = True
            return

        self.current_player = "O" if self.current_player == "X" else "X"
        self.status.config(text=f"Giliran: {self.current_player}")

    def check_winner(self):
        lines = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),
            (0, 3, 6), (1, 4, 7), (2, 5, 8),
            (0, 4, 8), (2, 4, 6)
        ]
        for a, b, c in lines:
            if self.board[a] and self.board[a] == self.board[b] == self.board[c]:
                self.winning_line = (a, b, c)
                return self.board[a]
        self.winning_line = None
        return None

    def highlight(self):
        if not self.winning_line:
            return
        for i in self.winning_line:
            self.buttons[i].config(bg="#00c853")

    def reset(self):
        self.board = [""] * 9
        self.current_player = "X"
        self.game_over = False
        self.winning_line = None
        self.status.config(text="Giliran: X")
        for i, btn in enumerate(self.buttons):
            btn.config(text="", state="normal", bg=self.cell_color(i // 3, i % 3))

# ---------------------------
# Math Quiz
# ---------------------------

class MathQuiz:
    def __init__(self, parent, back_cb, goto_snakes, goto_ttt):
        self.frame = tk.Frame(parent, bg="#222222")
        header = fancy_label(self.frame, "Soal Hitung")
        header.pack(pady=(6, 10), fill="x")

        nav = tk.Frame(self.frame, bg="#222222")
        nav.pack(pady=8)
        fancy_button(nav, "Main Ular Tangga", goto_snakes).grid(row=0, column=0, padx=5)
        fancy_button(nav, "Main Tic Tac Toe", goto_ttt).grid(row=0, column=1, padx=5)
        fancy_button(nav, "Kembali Menu", back_cb).grid(row=0, column=2, padx=5)

        self.status = tk.Label(self.frame, text="Jawab pertanyaan matematika sederhana.",
                               font=("Helvetica", 13, "bold"),
                               fg="#1b1b1b", bg="#ffdd77", padx=10, pady=6)
        self.status.pack(pady=(0, 8), fill="x")

        body = tk.Frame(self.frame, bg="#222222")
        body.pack(pady=10)

        self.question_label = tk.Label(body, text="", font=("Helvetica", 28, "bold"),
                                       fg="#ffffff", bg="#34495e", padx=18, pady=12)
        self.question_label.pack(pady=8)

        ans_frame = tk.Frame(body, bg="#222222")
        ans_frame.pack(pady=8)
        self.answer_var = tk.StringVar()
        self.answer_entry = tk.Entry(ans_frame, textvariable=self.answer_var, font=("Helvetica", 18),
                                     width=10, fg="#2c3e50")
        self.answer_entry.grid(row=0, column=0, padx=8)
        fancy_button(ans_frame, "Kirim", self.submit).grid(row=0, column=1, padx=8)

        stats = tk.Frame(body, bg="#222222")
        stats.pack(pady=6)
        self.score = 0
        self.total = 0
        self.score_label = tk.Label(stats, text="Skor: 0/0", font=("Helvetica", 12, "bold"),
                                    fg="#ffffff", bg="#2c3e50", padx=10, pady=6)
        self.score_label.pack()

        controls = tk.Frame(self.frame, bg="#222222")
        controls.pack(pady=8)
        fancy_button(controls, "Soal Baru", self.new_question).grid(row=0, column=0, padx=8)
        fancy_button(controls, "Reset", self.reset).grid(row=0, column=1, padx=8)

        self.current_answer = None
        self.new_question()

    def new_question(self):
        ops = ["+", "-", "×", "÷"]
        op = random.choice(ops)
        a = random.randint(2, 20)
        b = random.randint(2, 20)
        if op == "÷":
            b = random.randint(2, 10)
            a = b * random.randint(2, 10)
            self.current_answer = a // b
        elif op == "×":
            self.current_answer = a * b
        elif op == "+":
            self.current_answer = a + b
        else:
            a, b = max(a, b), min(a, b)
            self.current_answer = a - b
        self.question_label.config(text=f"{a} {op} {b} = ?")
        self.answer_var.set("")
        self.answer_entry.focus_set()

    def submit(self):
        val = self.answer_var.get().strip()
        if not val or not val.lstrip("-").isdigit():
            messagebox.showinfo("Info", "Masukkan angka yang valid.")
            return
        user = int(val)
        self.total += 1
        if user == self.current_answer:
            self.score += 1
            self.status.config(text="Benar!")
        else:
            self.status.config(text=f"Salah. Jawaban: {self.current_answer}")
        self.score_label.config(text=f"Skor: {self.score}/{self.total}")
        self.new_question()

    def reset(self):
        self.score = 0
        self.total = 0
        self.score_label.config(text="Skor: 0/0")
        self.status.config(text="Jawab pertanyaan matematika sederhana.")
        self.new_question()

# ---------------------------
# Run
# ---------------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = MultiGameApp(root)
    root.mainloop()