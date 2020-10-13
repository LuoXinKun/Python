#encoding:utf-8

def maopao(lista):
    num = len(lista)
    for i in range(num):
        for j in range(i,num):
            if lista[j]>lista[i]:
                lista[j],lista[i] = lista[i],lista[j]
                
<<<<<<< HEAD
list = [1,5,7,2,6,1,5,3]
list = maopao(list)
print(list)

if 1:
    print(1)
=======
a = maopao([1,3,2,4,5,6,2,1])
print(a)
>>>>>>> e1cf19eb79516a4dc873312905b40ae27c25f01e
