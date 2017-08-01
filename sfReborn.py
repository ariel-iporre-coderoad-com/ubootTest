import starflex

target = str(raw_input('Target IP : '))
patchPath = str(raw_input('Patch path : '))

client = starflex.star_client(target)
patchEndPoint = 'patch/'+patchPath.split('/')[-1]

if patchEndPoint.endswith('.patch'):
    client.post_file('file', patchPath)
    client.put_msg(end_point= patchEndPoint)
    client.put_msg(end_point= 'reboot')
else:
    print "ERROR: not a valid path file"

