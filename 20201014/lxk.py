#encoding:utf-8

def maopao(lista):
    num = len(lista)
    for i in range(num):
        for j in range(i,num):
            if lista[j]>lista[i]:
                lista[j],lista[i] = lista[i],lista[j]
a = 1
if a == 1:
    print("付费")
# 1014 最后一次更新
list = [1,5,7,2,6,1,5,3]
list = maopao(list)
print(list)


