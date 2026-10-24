-- Semantic reconstruction of WebParser's Lua bridge. Runtime feature-flag
-- variants and RapidJSON's exact shortest-decimal spelling are not restored.
return function(R)
    local MAX_DEPTH,MAX_BUFFER=128,50*1024*1024
    local alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    local reverse={}
    for i=1,64 do reverse[string.byte(alphabet,i)]=i-1 end
    local function validUtf8(text)
        assert(utf8.len(text)~=nil,"Can't convert invalid UTF-8 to JSON")
        for _,code in utf8.codes(text) do assert(code<0xD800 or code>0xDFFF,"Invalid Unicode surrogate") end
    end
    local escapes={['"']='\\"',['\\']='\\\\',['\b']='\\b',['\f']='\\f',['\n']='\\n',['\r']='\\r',['\t']='\\t'}
    local function quote(text)
        validUtf8(text)
        return '"'..string.gsub(text,'[%z\1-\31\\"]',function(c) return escapes[c] or string.format('\\u%04x',string.byte(c)) end)..'"'
    end
    local function base64(text)
        local out={}
        for i=1,#text,3 do
            local a,b,c=string.byte(text,i,i+2);b=b or 0;c=c or 0
            local n=a*65536+b*256+c
            table.insert(out,string.sub(alphabet,math.floor(n/262144)+1,math.floor(n/262144)+1)..
                string.sub(alphabet,math.floor(n/4096)%64+1,math.floor(n/4096)%64+1)..
                (if i+1<=#text then string.sub(alphabet,math.floor(n/64)%64+1,math.floor(n/64)%64+1) else '=')..
                (if i+2<=#text then string.sub(alphabet,n%64+1,n%64+1) else '='))
        end
        return table.concat(out)
    end
    local function unbase64(text)
        assert(type(text)=="string" and #text%4==0,"Malformed buffer base64")
        assert(#text/4*3<=MAX_BUFFER+2,"Buffer exceeds 50 MiB")
        local out={}
        for i=1,#text,4 do
            local a,b,c,d=string.byte(text,i,i+3)
            local x,y,z,w=reverse[a],reverse[b],reverse[c],reverse[d]
            assert(x and y and (z or c==61) and (w or d==61),"Malformed buffer base64")
            assert((c~=61 and d~=61) or i+3==#text,"Malformed buffer padding")
            assert(c~=61 or d==61,"Malformed buffer padding")
            local n=x*262144+y*4096+(z or 0)*64+(w or 0)
            table.insert(out,string.char(math.floor(n/65536))..
                (if c~=61 then string.char(math.floor(n/256)%256) else '')..
                (if d~=61 then string.char(n%256) else ''))
        end
        local bytes=table.concat(out);assert(#bytes<=MAX_BUFFER,"Buffer exceeds 50 MiB")
        return buffer.fromstring(bytes)
    end
    function R.jsonEncode(value)
        local active={}
        local function encode(v,depth)
            assert(depth<=MAX_DEPTH,"JSON nesting exceeds host limit 128")
            local kind=type(v)
            if kind=="nil" then return 'null' end
            if kind=="boolean" then return if v then 'true' else 'false' end
            if kind=="string" then return quote(v) end
            if kind=="number" then
                -- Nonfinite values take the original bridge's null path. The
                -- alternative tagged-numeric path is controlled by fast flags.
                if v~=v or math.abs(v)==math.huge then return 'null' end
                return string.format('%.17g',v)
            end
            if kind=="buffer" then
                assert(buffer.len(v)<=MAX_BUFFER,"Buffer exceeds 50 MiB")
                return '{"m":null,"t":"buffer","base64":'..quote(base64(buffer.tostring(v)))..'}'
            end
            if kind~="table" then return 'null' end
            assert(not active[v],"tables cannot be cyclic");active[v]=true
            local out={}
            -- Raw length/raw reads: metatable __len/__index/__iter must not run.
            local length=rawlen(v)
            if length>0 then
                for i=1,length do table.insert(out,encode(rawget(v,i),depth+1)) end
                active[v]=nil;return '['..table.concat(out,',')..']'
            end
            for key,item in next,v do
                if type(key)=="number" then key=string.format('%.6f',key)
                else assert(type(key)=="string","Unsupported JSON table key type") end
                table.insert(out,quote(key)..':'..encode(item,depth+1))
            end
            active[v]=nil
            return if #out==0 then '[]' else '{'..table.concat(out,',')..'}'
        end
        return encode(value,0)
    end
    function R.jsonDecode(text)
        assert(type(text)=="string","JSONDecode expects a string");validUtf8(text)
        local p,n=1,#text
        local function fail() error("Can't parse JSON at byte "..p,3) end
        local function skip()
            while p<=n do local b=string.byte(text,p);if b~=32 and b~=9 and b~=10 and b~=13 then break end;p+=1 end
        end
        local function hex4()
            local h=string.sub(text,p,p+3)
            if #h~=4 or not string.match(h,'^%x%x%x%x$') then fail() end
            p+=4;return tonumber(h,16)
        end
        local function stringValue()
            if string.byte(text,p)~=34 then fail() end
            p+=1;local start=p;local parts={}
            while p<=n do
                local b=string.byte(text,p)
                if b==34 then table.insert(parts,string.sub(text,start,p-1));p+=1;return table.concat(parts) end
                if b<32 then fail() end
                if b==92 then
                    table.insert(parts,string.sub(text,start,p-1));p+=1
                    local escape=string.sub(text,p,p);p+=1
                    local simple={['"']='"',['\\']='\\',['/']='/',b='\b',f='\f',n='\n',r='\r',t='\t'}
                    if escape=='u' then
                        local code=hex4()
                        if code>=0xD800 and code<=0xDBFF then
                            if string.sub(text,p,p+1)~='\\u' then fail() end;p+=2
                            local low=hex4();if low<0xDC00 or low>0xDFFF then fail() end
                            code=0x10000+(code-0xD800)*1024+low-0xDC00
                        elseif code>=0xDC00 and code<=0xDFFF then fail() end
                        table.insert(parts,utf8.char(code))
                    elseif simple[escape] then table.insert(parts,simple[escape]) else fail() end
                    start=p
                else p+=1 end
            end
            fail()
        end
        local parse
        parse=function(depth)
            assert(depth<=MAX_DEPTH,"JSON nesting exceeds host limit 128");skip()
            local b=string.byte(text,p)
            if b==34 then return stringValue() end
            if b==123 or b==91 then
                local object=b==123;local close=if object then 125 else 93
                p+=1;skip();local result={};local index=1;local marker=false
                if string.byte(text,p)==close then p+=1;return result end
                while true do
                    local key=index
                    if object then key=stringValue();skip();if string.byte(text,p)~=58 then fail() end;p+=1 end
                    local value,isNull=parse(depth+1)
                    if object and key=='m' then marker=isNull or false end
                    -- The original bridge skips JSON null rather than deleting
                    -- an earlier duplicate property. Array positions still count.
                    if value~=nil then result[key]=value end
                    index+=1;skip();local separator=string.byte(text,p);p+=1
                    if separator==close then break end
                    if separator~=44 then fail() end;skip()
                end
                if not object then
                    -- Native parse reserves the full JSON array capacity before
                    -- skipping nulls. Preserve that layout for VM rawlen on holes.
                    local array=table.create(index-1)
                    for i=1,index-1 do array[i]=rawget(result,i) end
                    return array
                end
                if object and marker then
                    if result.t=='buffer' then
                        if result.zbase64~=nil then
                            local compressed=unbase64(result.zbase64)
                            return buffer.fromstring((R.encodingTransform('decompress',buffer.tostring(compressed),'Zstd')))
                        end
                        return unbase64(result.base64)
                    end
                    if result.t=='numeric' then
                        if result.v=='inf' then return math.huge elseif result.v=='-inf' then return -math.huge
                        elseif result.v=='nan' then return 0/0 end
                        error('Unknown numeric value',2)
                    end
                    error('Unknown engine type',2)
                end
                return result
            end
            for literal,value in {['true']=true,['false']=false} do
                if string.sub(text,p,p+#literal-1)==literal then p+=#literal;return value end
            end
            if string.sub(text,p,p+3)=='null' then p+=4;return nil,true end
            local start=p
            if string.byte(text,p)==45 then p+=1 end
            local digit=string.byte(text,p)
            if digit==48 then p+=1
            elseif digit and digit>=49 and digit<=57 then
                repeat p+=1;digit=string.byte(text,p) until not digit or digit<48 or digit>57
            else fail() end
            local function digits()
                local first=p
                while p<=n do local c=string.byte(text,p);if c<48 or c>57 then break end;p+=1 end
                if p==first then fail() end
            end
            if string.byte(text,p)==46 then p+=1;digits() end
            digit=string.byte(text,p)
            if digit==69 or digit==101 then
                p+=1;digit=string.byte(text,p);if digit==43 or digit==45 then p+=1 end;digits()
            end
            local number=tonumber(string.sub(text,start,p-1))
            if not number or math.abs(number)==math.huge then fail() end
            return number
        end
        local value=parse(0);skip();if p<=n then fail() end;return value
    end
end
