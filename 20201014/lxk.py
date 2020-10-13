#encoding:utf-8

def maopao(lista):
    num = len(lista)
    for i in range(num):
        for j in range(i,num):
            if lista[j]>lista[i]:
                lista[j],lista[i] = lista[i],lista[j]
                
a = maopao([1,3,2,4,5,6,2,1])
print(a)