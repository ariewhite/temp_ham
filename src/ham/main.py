import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ControlSystemApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.bind("<space>", lambda event: self.update_plot())
        self.title("Моделирование системы управления второго порядка")
        self.geometry("1250x900")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # left frame
        self.left_frame = ctk.CTkFrame(self, width=340, corner_radius=15)
        self.left_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ns")
        self.left_frame.grid_propagate(False)

        # title
        ctk.CTkLabel(self.left_frame, text="Параметры моделирования", 
                     font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, pady=(20, 30))

        row = 1

        def add_param(label_text, default_value):
            nonlocal row
            ctk.CTkLabel(self.left_frame, text=label_text).grid(row=row, column=0, sticky="w", padx=25, pady=(10, 5))
            entry = ctk.CTkEntry(self.left_frame, width=220)
            entry.insert(0, default_value)
            entry.grid(row=row+1, column=0, padx=25, pady=(0, 15))
            row += 2
            return entry

        self.kp_entry     = add_param("K_p (номинальный):", "1.0")
        self.percent_entry = add_param("Увеличение K_p (%):", "30")
        self.xi_entry     = add_param("ξ (демпфирование):", "0.7")
        self.h_entry      = add_param("Шаг h:", "0.02")
        self.t_end_entry  = add_param("Время моделирования (с):", "10")

        # checkboxes frame
        self.checkbox_frame = ctk.CTkFrame(self.left_frame, fg_color=("gray85", "gray20"), corner_radius=10)
        self.checkbox_frame.grid(row=row, column=0, padx=25, pady=20, sticky="ew")
        self.checkbox_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.checkbox_frame, text="Отображаемые сигналы", 
                     font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, pady=(15, 10), sticky="w", padx=20)

        cb_row = 1
        self.show_ref = ctk.CTkCheckBox(self.checkbox_frame, text="Задающее воздействие x(t)", text_color='black')
        self.show_ref.grid(row=cb_row, column=0, sticky="w", padx=30, pady=8); self.show_ref.select(); cb_row += 1

        self.show_out = ctk.CTkCheckBox(self.checkbox_frame, text="Выход y(t)", text_color='blue')
        self.show_out.grid(row=cb_row, column=0, sticky="w", padx=30, pady=8); self.show_out.select(); cb_row += 1

        self.show_error = ctk.CTkCheckBox(self.checkbox_frame, text="Сигнал ошибки e(t)", text_color='red')
        self.show_error.grid(row=cb_row, column=0, sticky="w", padx=30, pady=8); self.show_error.select(); cb_row += 1

        self.show_feedback = ctk.CTkCheckBox(self.checkbox_frame, text="Сигнал обратной связи f(t)", text_color='green')
        self.show_feedback.grid(row=cb_row, column=0, sticky="w", padx=30, pady=(8, 15)); cb_row += 1

        # upd btn
        self.update_button = ctk.CTkButton(self.left_frame, text="Обновить график", 
                                           command=self.update_plot, fg_color="green", height=40,
                                           font=ctk.CTkFont(size=14, weight="bold"))
        self.update_button.grid(row=row+1, column=0, padx=40, pady=30, sticky="ew")

        # graph frame
        self.plot_frame = ctk.CTkFrame(self)
        self.plot_frame.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="nsew")
        self.plot_frame.grid_rowconfigure(0, weight=1)
        self.plot_frame.grid_columnconfigure(0, weight=1)

        self.figure, self.ax = plt.subplots(figsize=(10, 7))
        self.canvas = FigureCanvasTkAgg(self.figure, self.plot_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        self.update_plot()

    def simulate(self, Kp, xi, t_end, h):
        N = int(t_end / h) + 1
        t = np.linspace(0, t_end, N)
        y = np.zeros(N)
        dy = np.zeros(N)
        e = np.zeros(N)
        f = np.zeros(N)
        x_val = 1.0

        for n in range(N-1):
            f[n] = y[n] + 2 * xi * dy[n]
            e[n] = x_val - f[n]

            y[n+1] = y[n] + h * dy[n]
            dy[n+1] = dy[n] + h * (-Kp * y[n] - 2*xi * dy[n] + Kp * x_val)

        # last point
        f[-1] = y[-1] + 2 * xi * dy[-1]
        e[-1] = x_val - f[-1]

        return t, y, dy, e, f

    def update_plot(self):
        try:
            Kp = float(self.kp_entry.get())
            percent = float(self.percent_entry.get())
            Kp_plot = Kp * (1 + percent / 100)
            xi = float(self.xi_entry.get())
            h = float(self.h_entry.get())
            t_end = float(self.t_end_entry.get())
        except ValueError:
            return

        # да чтоб так в плюсах можно было
        t, y, dy, e, f = self.simulate(Kp_plot, xi, t_end, h)

        self.ax.clear()

        if self.show_ref.get():
            self.ax.plot(t, np.ones_like(t), 'k-', linewidth=2, label='Задающее x(t) = 1')

        if self.show_out.get():
            self.ax.plot(t, y, 'b-', linewidth=3, label=f'Выход y(t) (K_p = {Kp_plot:.3f})')

        if self.show_error.get():
            self.ax.plot(t, e, 'r--', linewidth=2.5, label='Ошибка e(t)')

        if self.show_feedback.get():
            self.ax.plot(t, f, 'g:', linewidth=2, label='Обратная связь f(t) = y + 2ξ⋅dy/dt')

        self.ax.set_title(f'Сигналы в системе (ξ = {xi}, метод Эйлера)', fontsize=16)
        self.ax.set_xlabel('Время t, с', fontsize=12)
        self.ax.set_ylabel('Амплитуда', fontsize=12)
        self.ax.grid(True, alpha=0.5)
        self.ax.legend(fontsize=11)
        self.ax.set_ylim(-0.6, 1.8)

        self.canvas.draw()

def main() -> int:
    app = ControlSystemApp()
    app.mainloop()
    return 0

if __name__ == "__main__":
    main()