import struct
def read_wad(path):
    d=open(path,'rb').read()
    t,n,o=struct.unpack('<4sii',d[:12]); L=[]
    for i in range(n):
        p,s,nm=struct.unpack('<ii8s',d[o+16*i:o+16*i+16]); L.append((nm.rstrip(b'\0').decode('latin1'),d[p:p+s]))
    return L
def get(L,name): return [b for n,b in L if n==name][-1]
def palette(L):
    p=get(L,'PLAYPAL'); return [tuple(p[i*3:i*3+3]) for i in range(256)]
def decode_patch(b):
    w,h,lo,to=struct.unpack('<hhhh',b[:8]); cols=struct.unpack('<%di'%w,b[8:8+4*w])
    px={}
    for x,c in enumerate(cols):
        while b[c]!=255:
            top=b[c]; ln=b[c+1]
            for i in range(ln): px[(x,top+i)]=b[c+3+i]
            c+=ln+4
    return w,h,lo,to,px
def recolor_patch(b,remap):
    # in-place index remap, keeps structure
    b=bytearray(b); w=struct.unpack('<h',b[:2])[0]; cols=struct.unpack('<%di'%w,b[8:8+4*w])
    for c in cols:
        while b[c]!=255:
            ln=b[c+1]
            for i in range(ln): b[c+3+i]=remap[b[c+3+i]]
            c+=ln+4
    return bytes(b)
def write_wad(path,lumps,kind=b'PWAD'):
    data=b''; dirs=[]; off=12
    for n,b in lumps:
        dirs.append(struct.pack('<ii8s',off,len(b),n.encode())); data+=b; off+=len(b)
    open(path,'wb').write(struct.pack('<4sii',kind,len(lumps),off)+data+b''.join(dirs))
