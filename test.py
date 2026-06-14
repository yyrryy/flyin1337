string = "ABCD"
# lower the string
lowered = string.lower()


#Revers the stringl
length= len(string)
reversed = ""
reversed += lowered[length-1]
reversed += lowered[length-2]
reversed += lowered[length-3]
reversed += lowered[length-4]
l = ["start"]
{
    "start": None,
}
while l:
    e = l.pop(0)
    n = data[e]["connected_to"]
    for i in n:
        