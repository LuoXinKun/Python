#encoding:utf-8

def maopao(lista):
    num = len(lista)
    for i in range(num):
        for j in range(i,num):
            if lista[j]>lista[i]:
                lista[j],lista[i] = lista[i],lista[j]
                
list = [1,5,7,2,6,1,5,3]
list = maopao(list)
print(list)