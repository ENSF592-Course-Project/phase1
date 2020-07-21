import tkinter as tk
from tkinter import ttk
from tkinter import *
from db_operation import * 

# initializing global variables
dbname = ''
collectionName = ''
db = db_operation("","","")
yearList = []
yearVolumeList = []
MaxAccdentCountsList = []
MaxVolumeList = []

# build parent object
window = tk.Tk()
window.iconbitmap('icon.ico')
window.title("Traffic Statistics of Calgary City")
window.geometry("1200x600")

# add left frames using frame widget
frame_left = tk.Frame(master=window, width=200, height=600, bg="grey")
frame_left.pack(fill=tk.BOTH, side=tk.LEFT, expand=False)

# build 3 notebook tabs at right, and one frame for each tab
note = ttk.Notebook(window)
tab1 = ttk.Frame(note)
tab2 = ttk.Frame(note)
tab3 = ttk.Frame(note)
note.add(tab1, text = "Database")
note.add(tab2, text = "Figures")
note.add(tab3, text = "Map")
note.pack()

# add a text widget to display query result in tab 1 frame
def addTextBox():
    text_display = tk.Text(tab1, width=800, height=600)
    text_display.grid(row = 0, column = 1, sticky = "nsew")
    return text_display

def addComboBox(text, row, options):
    comboItems = ttk.Combobox(frame_left, width = 27) 
    comboItems.set(text)
    comboItems['values'] = options
    comboItems.grid(column = 40, row = row, pady=5) 
    style = ttk.Style()

    style.map('comboItems', fieldbackground=[('readonly','white')])
    style.map('comboItems', selectbackground=[('readonly', 'white')])
    style.map('comboItems', selectforeground=[('readonly', 'black')])
    return comboItems


def addButton(text, row, func, clr):
    button = tk.Button(master = frame_left, text = text, width = 25, command = func, bg = clr, bd = 2)
    button.grid(column = 40, row = row, pady = 5)
    return button

def addLabel(text, row, height):
    lbl_value = tk.Label(master = frame_left, text = text, width = 25, height = height, bg = 'grey')
    lbl_value.grid(column = 40, row = row, pady = 5)
    return lbl_value


type_combobox = addComboBox('select a type', 1, ('Traffic Vol','Traffic Accident'))
year_combobox = addComboBox('select a year', 2, (' 2016',' 2017',' 2018', ' 2019', ' 2020'))
read_button = addButton("Read",     3, lambda: onclick(msg, type = "Read"),"#A8EDF3")
sort_button = addButton("Sort",     4, lambda: onclick(msg, type = "Sort"),"#A8EDF3")
analysis_button = addButton("Analysis", 5, lambda: onclick(msg, type = "Analysis"),"#A8EDF3")
map_button = addButton("Map",      6, lambda:onclick(msg, type = "Map"),"#A8EDF3")
lable_title = addLabel("Status", 7, 1)

# add a text widget to display message in left frame
msg = tk.Text(frame_left, width = 36, height = 5)
msg.grid(row = 8, column = 40)

# construct a Matplotlib figure
figure, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(50,100))

def onclick(msg, type):
    # assign mangoDB database name and collection name
    if(type_combobox.get().strip() == 'Traffic Vol'):
        dbname = 'Volumes'
        year = str(year_combobox.get().strip())
        collectionName = dbname + "_" + year
    elif(type_combobox.get().strip() == 'Traffic Accident'):
        dbname = 'Incidents'
        collectionName = dbname + "_" + "proj" # the file containing 2016-2020 incident data
        year = str(year_combobox.get().strip())
    else:
        dbname = ''
        collectionName = ''
        year = ''
        msg_display(dbname, year, '')
    
    # instantiate db_operation class object, passing database name and collection name
    db = db_operation(dbname.strip(), collectionName.strip(), year)
    
    # parse which button has been clicked
    if  (type == 'Read'):
        for child in tab2.winfo_children():
            child.destroy()
        for child in tab3.winfo_children():
            child.destroy()    
        read_display = addTextBox()
        read_display.insert(tk.END, db.read_db(False))
        msg_display(dbname, year, type)
        note.select(tab1)
    elif(type == 'Sort'):
        for child in tab2.winfo_children():
            child.destroy()
        for child in tab3.winfo_children():
            child.destroy()
        sort_display = addTextBox()
        sort_display.insert(tk.END, db.read_db(True))
        msg_display(dbname, year, type)
        note.select(tab1)
    elif(type == 'Analysis'):
        for child in tab1.winfo_children():
            child.destroy()
        for child in tab2.winfo_children():
            child.destroy()
        for child in tab3.winfo_children():
            child.destroy()    
        if dbname == 'Volumes':
            volume_plot(db.analyze_top_volumes(), ax1)
        if dbname == 'Incidents':
            accident_plot(db.analyze_top_accidents(), ax2)
        # attach plot onto tab2
        canvas = FigureCanvasTkAgg(figure, master = tab2)
        canvas.get_tk_widget().pack()
        msg_display(dbname, year, type)
        note.select(tab2)
    elif(type == 'Map'):
        db.map_display()
        msg.delete('1.0', 'end')
        msg_display(dbname, year, type)
        note.select(tab3)


def msg_display(data_type, year, action_type):
    msg.delete('1.0', 'end')
    if data_type == 'Volumes':
        if year == 'select a year':
            msg.insert(tk.END, 'Please select year\n')
            msg.config(bg = "red")
        elif int(year) > 2018:
            msg.insert(tk.END, 'No Volume Data available after 2018\n')
            msg.config(bg = "red")
        else:
            if action_type == 'Read':
                msg.insert(tk.END, 'Successfully read from DB\n')
                msg.config(bg = "#76FB06")
            elif action_type == 'Sort':
                msg.insert(tk.END, 'Successfully sorted\n')
                msg.config(bg = "#76FB06")
            elif action_type == 'Analysis':
                msg.insert(tk.END, 'Successfully analyzed\n')
                msg.config(bg = "#76FB06")
            elif action_type == 'Map':
                msg.insert(tk.END, 'Successfully written map, opened in browser\n')
                msg.config(bg = "#76FB06")
            else:
                msg.insert(tk.END, 'Please select data type and year\n')
                msg.config(bg = "red")
    elif data_type == 'Incidents':
        if year == 'select a year':
            return 'Please select year\n'
        else:
            if action_type == 'Read':
                msg.insert(tk.END, 'Successfully read from DB\n')
                msg.config(bg = "#76FB06")
            elif action_type == 'Sort':
                msg.insert(tk.END, 'Successfully sorted\n')
                msg.config(bg = "#76FB06")
            elif action_type == 'Analysis':
                msg.insert(tk.END, 'Successfully analyzed\n')
                msg.config(bg = "#76FB06")
            elif action_type == 'Map':
                msg.insert(tk.END, 'Successfully written map, opened in browser\n')
                msg.config(bg = "#76FB06")
            else:
                msg.insert(tk.END, 'Please select data type and year\n')
                msg.config(bg = "red")
    else:
        msg.insert(tk.END, 'Please select both data type and year\n')
        msg.config(bg = "red")


def volume_plot(volume, ax1):
    # plot DataFrame volume vs. year
    YearList = [2016,2017,2018]
    Data = {'Year': YearList, 'Max_Volume': volume}
    df = pd.DataFrame(Data,columns=['Year','Max_Volume'])
    ax1.set_xticks(YearList)
    ax1.set_ylabel("Max Volume")
    df = df[['Year','Max_Volume']].groupby('Year').sum()    
    df.plot(kind = 'line', marker='o', title = 'Volume vs. Year', legend = False, ax = ax1, color = 'blue') 


def accident_plot(Max_Accident_List, ax2):
    # plot DataFrame highest accident count vs. year
    YearList = [2016,2017,2018, 2019, 2020]
    Data = {'Year': YearList, 'Max_Accident_Counts': Max_Accident_List}
    df = pd.DataFrame(Data, columns = ['Year','Max_Accident_Counts'])
    ax2.set_xticks(YearList) 
    ax2.set_ylabel("Number of accidents")
    df = df[['Year','Max_Accident_Counts']].groupby('Year').sum()    
    df.plot(kind = 'line', marker='o', title = 'Accident Count vs. Year', legend = False, ax = ax2, color = 'red')
    
window.mainloop()