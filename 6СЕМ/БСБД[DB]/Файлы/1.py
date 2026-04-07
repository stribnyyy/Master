print("Введите колво элементов ", end="")
k=int(input())
print("Введите начальное значение ", end="")
n=int(input())
print("Введите шаг ", end="")
h=int(input())
suml=0
a=0
for a in range(k):
    suml=suml+n
    n=n+h
print("Сумма элементов = ", suml)
