text=str(input("Enter the text: ")).lower()
key=str(input("Enter the key: ")).lower()
alp=list('абвгдеёжзийклмнопрстуфхцчшщъыьэюя')
textcodes=list()
keycodes=list()

# веко запаскарманнетянет

for l in text:
    counter=1
    for i in alp:
        if i == l:
            textcodes.append(counter)
            continue
        counter+=1

for l in key:
    counter=1
    for i in alp:
        if i == l:
            keycodes.append(counter)
            continue
        counter+=1

counter_t=0
counter_k=0
for i in textcodes:
    if (textcodes[counter_t]-keycodes[counter_k]<1):
        textcodes[counter_t]=(textcodes[counter_t]-keycodes[counter_k])+33
        counter_k+=1
        counter_t+=1
        if counter_k==len(keycodes):
            counter_k=0
    else:
        textcodes[counter_t]=(textcodes[counter_t]-keycodes[counter_k])
        counter_k += 1
        counter_t += 1
        if counter_k==len(keycodes):
            counter_k=0

output=""
for i in textcodes:
    output+=alp[int(i)-1]
print(output)