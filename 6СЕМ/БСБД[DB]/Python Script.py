file=open("file.txt", "w")
file.close()
for x in range(-27, 28):
    if x>0:
        f=(x**2)/3
    else:
        f=3*(x**2)
    file=open("file.txt", "a")
    file.write("x="+str(x)+"; f="+str(f)+"\n")
    file.close()
file=open("file.txt", "r")
print(file.read())
