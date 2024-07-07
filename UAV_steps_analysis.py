import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from matplotlib.patches import Rectangle
from mplcursors import cursor
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from matplotlib.ticker import MultipleLocator
import json

def get_CSV_file(filename, index_col):
    df = pd.read_csv(filename, index_col=index_col, parse_dates=True)
    return df

def get_idxs_of_low_variance(df, ref_col, window_size, var_ths):
    a = df[ref_col]
    a_windows = np.lib.stride_tricks.sliding_window_view(a, window_shape=window_size)
    vars_are_small = np.where(a_windows.var(-1) < var_ths, 1, 0)
    d = np.diff(vars_are_small)
    starts = np.argwhere(d == 1)[:, 0] + 1
    ends = np.argwhere(d == -1)[:, 0] + window_size - 1

    if vars_are_small[0] == 1:
        starts = np.insert(starts, 0, 0)
    if vars_are_small[-1] == 1:
        ends = np.append(ends, len(a) - 1)
    
    if starts.size == 0 or ends.size == 0:
        return np.array([]), np.array([])
    if starts[0] > ends[0]: 
        starts = np.concatenate([np.array([0]), starts])
    if starts[-1] > ends[-1]: 
        ends = np.concatenate([ends, np.array([a.shape[-1] - 1])])
    return starts, ends

def suggested_steps(df, ref_col, var_ths, step_size):
    window_size = 10  # Fixed window size
    starts, ends = get_idxs_of_low_variance(df, ref_col, window_size, var_ths)
    if starts.size == 0 or ends.size == 0:
        return []
    starts = starts if step_size is None else [end - step_size for end in ends]
    selections = [[s, e] for s, e in zip(starts, ends)]
    return selections

def merge_intervals(df, ref_col, var_ths, step_size):
    intervals = suggested_steps(df, ref_col, var_ths, step_size)
    if not intervals:
        return []
    intervals.sort(key=lambda x: x[0])
    merged_intervals = []
    current_start, current_end = intervals[0]
    for i in range(1, len(intervals)):
        next_start, next_end = intervals[i]
        if current_end >= next_start:
            current_end = max(current_end, next_end)
        else:
            merged_intervals.append([current_start, current_end])
            current_start, current_end = next_start, next_end
    merged_intervals.append([current_start, current_end])
    return merged_intervals

def plot_and_select_intervals(df, ref_col, var_ths, step_size, x_is_time=False, invert_y=False, to_use_cursor=True):
    intervals = merge_intervals(df, ref_col, var_ths, step_size)
    idxs_to_plot = np.arange(len(df))
    fig, ax = plt.subplots(figsize=(10, 4))
    if x_is_time:
        x = df.index[idxs_to_plot]
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M, %d/%m'))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=-45, ha="left")
    else:
        x = np.arange(idxs_to_plot.shape[0])[idxs_to_plot]
    ax.plot(x, df[ref_col].to_numpy()[idxs_to_plot])
    if invert_y:
        ax.invert_yaxis()
    rectangles = []
    for i, selection in enumerate(intervals):
        rect = Rectangle((x[selection[0]], ax.get_ylim()[0]), x[selection[1]] - x[selection[0]], ax.get_ylim()[1] - ax.get_ylim()[0], alpha=0.2, color='green')
        ax.add_patch(rect)
        rectangles.append(rect)
        ax.text(x[selection[0]], ax.get_ylim()[1] * 0.8 + ax.get_ylim()[0] * 0.2, f"{i}", fontsize=10, rotation=0)
    if to_use_cursor:
        cursor(hover=True)

    selected_intervals = []
    def on_click(event):
        if event.inaxes != ax:
            return
        for i, rect in enumerate(rectangles):
            if rect.contains(event)[0]:
                if rect.get_alpha() == 0.2:
                    rect.set_alpha(0.5)
                    selected_intervals.append(intervals[i])
                else:
                    rect.set_alpha(0.2)
                    selected_intervals.remove(intervals[i])
                fig.canvas.draw()
                break

    fig.canvas.mpl_connect('button_press_event', on_click)
    def on_close(event):
        plt.close(fig)
    fig.canvas.mpl_connect('close_event', on_close)
    plt.show()
    while plt.fignum_exists(fig.number):
        plt.pause(0.1)
        
    
    if selected_intervals:
        subtract_intervals = messagebox.askyesno("Subtract Intervals", "Do you want to subtract the selected intervals?")
        if subtract_intervals:
            return [interval for interval in intervals if interval not in selected_intervals]
    return intervals

def get_selected_statistics(df, ref_col, var_ths, step_size, stats_col):
    selections = plot_and_select_intervals(df, ref_col, var_ths, step_size, x_is_time=False, invert_y=False, to_use_cursor=True)
    if not selections:
        return np.array([]), np.array([]), np.array([]), []
    
    plot_stats = messagebox.askyesno("Plot Statistics", "Do you want to plot the statistics for the selected intervals?")
    if not plot_stats:
        return np.array([]), np.array([]), np.array([]), []
    
    selection_idxs = [np.arange(selection[0], selection[1] + 1) for selection in selections]
    x = [df[stats_col].to_numpy()[idxs] for idxs in selection_idxs]
    y = [df[ref_col].to_numpy()[idxs] for idxs in selection_idxs]
    x_means = np.array([xi.mean(0) for xi in x])
    x_stds = np.array([xi.std(0) for xi in x])
    y_means = np.array([yi.mean(0) for yi in y])

    return x_means, x_stds, y_means, selections


def plot_default_stats(df, ref_col, var_ths, step_size, stats_col):
    x_means, x_stds, y_means, selections = get_selected_statistics(df, ref_col, var_ths, step_size, stats_col)
    if x_means.size == 0:
        return

    fig, axs = plt.subplots(figsize=(12, 7))
    axs.plot(x_means, y_means, label=stats_col, color='skyblue')
    axs.fill_betweenx(y_means, x_means - x_stds, x_means + x_stds, alpha=.2, label = 'Standard deviation', color='skyblue')
    axs.set_ylabel(ref_col)
    axs.set_ylim([min(y_means), max(y_means)])
    axs.set_xlabel(stats_col)
    
    axs.xaxis.set_major_locator(ticker.MaxNLocator(nbins=20))
    axs.xaxis.set_minor_locator(ticker.AutoMinorLocator())
    
    axs.yaxis.set_major_locator(ticker.MaxNLocator(nbins=10))
    axs.yaxis.set_minor_locator(ticker.AutoMinorLocator())

    for tick in axs.get_xticklabels():
        tick.set_rotation(45)
        tick.set_fontsize(10)

    for tick in axs.get_yticklabels():
        tick.set_rotation(0)
        tick.set_fontsize(10)

    axs.invert_yaxis()
    fig.suptitle(f"{stats_col} vs {ref_col}")
    fig.tight_layout()
    fig.legend(loc='upper right')
    plt.subplots_adjust(right=0.85)
    plt.show()

    save_intervals_prompt(selections)

def save_intervals_prompt(selections):
    save = messagebox.askyesno("Save Intervals", "Do you want to save the selected intervals as JSON?")
    if save:
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            selections_native = [[int(start), int(end)] for start, end in selections]
            with open(file_path, 'w') as f:
                json.dump(selections_native, f)
            messagebox.showinfo("Saved", "Intervals saved successfully!")

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Data Plotter")
        self.filename = None
        self.df = None

        self.label_file = tk.Label(root, text="CSV File:")
        self.label_file.grid(row=0, column=0, padx=10, pady=10)
        self.entry_file = tk.Entry(root, width=50)
        self.entry_file.grid(row=0, column=1, padx=10, pady=10)
        self.button_browse = tk.Button(root, text="Browse", command=self.browse_file)
        self.button_browse.grid(row=0, column=2, padx=10, pady=10)

        self.label_index = tk.Label(root, text="Index Column:")
        self.label_index.grid(row=1, column=0, padx=10, pady=10)
        self.combobox_index = ttk.Combobox(root, state='readonly')
        self.combobox_index.grid(row=1, column=1, padx=10, pady=10)

        self.label_ref_col = tk.Label(root, text="Analysis Column:")
        self.label_ref_col.grid(row=2, column=0, padx=10, pady=10)
        self.combobox_ref_col = ttk.Combobox(root, state='readonly')
        self.combobox_ref_col.grid(row=2, column=1, padx=10, pady=10)

        self.label_stats_col = tk.Label(root, text="X Stats Column:")
        self.label_stats_col.grid(row=3, column=0, padx=10, pady=10)
        self.combobox_stats_col = ttk.Combobox(root, state='readonly')
        self.combobox_stats_col.grid(row=3, column=1, padx=10, pady=10)

        self.label_step_size = tk.Label(root, text="Step Size:")
        self.label_step_size.grid(row=4, column=0, padx=10, pady=10)
        self.entry_step_size = tk.Entry(root)
        self.entry_step_size.grid(row=4, column=1, padx=10, pady=10)

        self.label_var_ths = tk.Label(root, text="Variance Threshold:")
        self.label_var_ths.grid(row=5, column=0, padx=10, pady=10)
        self.entry_var_ths = tk.Entry(root)
        self.entry_var_ths.grid(row=5, column=1, padx=10, pady=10)

        self.button_stats = tk.Button(root, text="Select intervals & Plot Statistics", command=self.plot_statistics)
        self.button_stats.grid(row=7, column=0, columnspan=2, pady=10)

    def browse_file(self):
        self.filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        self.entry_file.insert(0, self.filename)
        self.load_csv_columns()

    def load_csv_columns(self):
        if self.filename:
            self.df = pd.read_csv(self.filename)
            self.combobox_index['values'] = list(self.df.columns)
            self.combobox_index.current(0)
            self.combobox_ref_col['values'] = list(self.df.columns)
            self.combobox_ref_col.current(0)
            self.combobox_stats_col['values'] = list(self.df.columns)
            self.combobox_stats_col.current(0)

    def plot_statistics(self):
        if not self.filename:
            messagebox.showerror("Error", "Please select a CSV file.")
            return
        stats_col = self.combobox_stats_col.get().strip()
        ref_col = self.combobox_ref_col.get().strip()
        step_size = int(self.entry_step_size.get())
        var_ths = float(self.entry_var_ths.get())

        try:
            self.df = get_CSV_file(self.filename, self.combobox_index.get().strip())

            if ref_col not in self.df.columns:
                raise KeyError(f"Column '{ref_col}' not found in the CSV file.")
            if stats_col not in self.df.columns:
                raise KeyError(f"Column '{stats_col}' not found in the CSV file.")
            
            plot_default_stats(self.df, ref_col, var_ths, step_size, stats_col)
        except KeyError as e:
            messagebox.showerror("Error", str(e))
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid value: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
