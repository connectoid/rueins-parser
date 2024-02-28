s= open('pr.txt').readline()

k=0

for i in range (len(s)):

    if s[i].isdigit():

        k+=1

print (k)