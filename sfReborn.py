import starflex
import sys

print "This is the name of the script: ", sys.argv[0]
print "Number of arguments: ", len(sys.argv)
print "The arguments are: " , str(sys.argv)

#target = str(raw_input('Target IP : '))
#patchPath = str(raw_input('Patch path : '))
target = sys.argv[1]
patchPath = sys.argv[2]


client = starflex.star_client(target)
patchEndPoint = 'patch/'+patchPath.split('/')[-1]

if patchEndPoint.endswith('.patch'):
    client.post_file('file', patchPath)
    client.put_msg(end_point= patchEndPoint)
    client.put_msg(end_point= 'reboot')
else:
    print "ERROR: not a valid path file"

