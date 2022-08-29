from tkinter import *
from datetime import date
from datetime import datetime

today = date.today()
date = today.strftime("%B %d, %Y")
now = datetime.now()
time = now.strftime("%H:%M")

def part_1():
    root.destroy()
    import M2
    
def end():
    root.destroy()
    
    

root = Tk()
root.title('PV Cell Analysis Tool')
root.geometry('480x360')
logo = PhotoImage(file=r"C:\Users\mites\OneDrive\Desktop\Placement\Resume\File_icon.gif")
bgimg= PhotoImage(file = r"C:\Users\mites\OneDrive\Desktop\Placement\Resume\Background_icon.gif")
limg= Label(root, i=bgimg).place(x=-2,y=0)
root.iconphoto(False,logo)
root.config(bg='black')
Label1=Label(root,text="\nWelcome to PV Cell Analysis Tool",font=('Arial Bold',20),fg='Blue',bg='Black').place(x=15,y=25)
Label2=Label(root,justify=LEFT,text=f'Time: {time}',fg='red',bg='black').place(x=0,y=5)
Label3=Label(root,justify=RIGHT,text=f'Date: {date}',fg='red',bg='black').place(x=0,y=25)
Label_Heading=Label(root,text="Click Start to continue....",font=('Arial',12),fg='springgreen',bg='black').place(x=150,y=230)

Button1=Button(root,text="Start",fg='yellow',bg='green',command=part_1,font=('Arial Bold',12)).place(x=210,y=270)
Button5=Button(root,text='Exit!',command=end,bg='gray75').place(x=430,y=320)
root.mainloop()