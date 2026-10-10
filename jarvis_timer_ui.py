
import tkinter as tk
import os

root = tk.Tk()
root.title('Jarvis')
root.geometry('220x80')
root.attributes('-topmost', True) 
root.configure(bg='#1c1c1e') 

time_left = 1 * 60

label = tk.Label(root, text='', font=('Menlo', 40, 'bold'), fg='#0a84ff', bg='#1c1c1e')
label.pack(expand=True)

def update():
    global time_left
    if time_left > 0:
        m, s = divmod(time_left, 60)
        label.config(text=f'{m:02d}:{s:02d}')
        time_left -= 1
        root.after(1000, update)
    else:
        label.config(text='00:00', fg='#ff453a')
        os.system('osascript -e \'display notification "Time is up!" with title "Jarvis Timer" sound name "Glass"\'')
        root.after(4000, root.destroy)

update()
root.mainloop()
