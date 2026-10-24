return function(R)
    local M={};R.classMethods.HttpService=M
    local pending={}
    function M:JSONEncode(input) return R.jsonEncode(input) end
    function M:JSONDecode(input) return R.jsonDecode(input) end
    function M:UrlEncode(input)
        assert(type(input)=="string" or type(input)=="number","UrlEncode expects a string")
        return (string.gsub(tostring(input),'[^A-Za-z0-9]',function(c) return string.format('%%%02X',string.byte(c)) end))
    end
    function M:GenerateGUID(braces)
        if braces==nil then braces=true end
        assert(type(braces)=="boolean","GenerateGUID expects a boolean")
        local bytes=buffer.create(16)
        assert(__host_guid(bytes)>=0,"OS random generation failed")
        local parts={}
        for i=0,15 do
            if i==4 or i==6 or i==8 or i==10 then table.insert(parts,'-') end
            table.insert(parts,string.format('%02x',buffer.readu8(bytes,i)))
        end
        local guid=table.concat(parts);return if braces then '{'..guid..'}' else guid
    end
    function R.pollExternal()
        for id,signal in pending do
            local body,metadata=__host_http(1,id)
            if metadata then
                -- Release before parsing: malformed host metadata must not pin
                -- a response permanently. Native allocation failure is cleaned
                -- by Runtime.close even if the script cannot continue.
                __host_http(2,id);pending[id]=nil
                local response=R.jsonDecode(metadata);response.Body=body
                R.fireSignal(signal,response)
            end
        end
    end
    function R.externalPending() return next(pending)~=nil end
    function R.waitExternal(milliseconds) __host_http(3,milliseconds) end
    function R.hostRequest(options,body)
        local id=__host_http(0,R.jsonEncode(options),body or '')
        assert(id>0,"Unable to start host request")
        local signal=R.newSignal();pending[id]=signal
        local response=signal:Wait()
        if response.Error then error(response.Error,2) end
        return response
    end
    local methods={GET=true,HEAD=true,POST=true,PUT=true,DELETE=true,PATCH=true,OPTIONS=true}
    function M:RequestAsync(options)
        assert(self.HttpEnabled,"Http requests are not enabled. Set HttpService.HttpEnabled = true")
        assert(R.current().side=="server","Http requests can only be executed by the server")
        assert(type(options)=="table","RequestAsync expects a dictionary")
        assert(type(options.Url)=="string","RequestAsync.Url must be a string")
        local method=options.Method or 'GET'
        assert(type(method)=="string" and methods[method],"Unsupported HTTP method")
        assert(options.Body==nil or type(options.Body)=="string","RequestAsync.Body must be a string")
        assert((method~='GET' and method~='HEAD') or options.Body==nil,"GET and HEAD cannot have a request body")
        local headers=options.Headers or {}
        assert(type(headers)=="table","RequestAsync.Headers must be a dictionary")
        for key,value in next,headers do assert(type(key)=="string" and type(value)=="string","Headers require string keys and values") end
        local timeout=options.Timeout or 30
        assert(type(timeout)=="number" and timeout>0 and timeout<=30,"Timeout must be greater than 0 and no greater than 30 seconds (host limit)")
        local compression=options.Compress or R.Enum.HttpCompression.None
        assert(compression==R.Enum.HttpCompression.None or compression==R.Enum.HttpCompression.Gzip,"Invalid HTTP compression")
        local metadata={Url=options.Url,Method=method,Headers=headers,Timeout=timeout,
            Gzip=compression==R.Enum.HttpCompression.Gzip,HasBody=options.Body~=nil}
        return R.hostRequest(metadata,options.Body)
    end
    local function bodyOnly(response)
        if not response.Success then error('HTTP '..response.StatusCode..' ('..response.StatusMessage..')',3) end
        return response.Body
    end
    function M:GetAsync(url,nocache,headers)
        assert(nocache==nil or type(nocache)=="boolean","nocache must be a boolean")
        headers=table.clone(headers or {})
        if nocache then headers['Cache-Control']='no-cache' end
        return bodyOnly(self:RequestAsync({Url=url,Headers=headers}))
    end
    local contentTypes={ApplicationJson='application/json',ApplicationXml='application/xml',ApplicationUrlEncoded='application/x-www-form-urlencoded',
        TextPlain='text/plain',TextXml='text/xml'}
    function M:PostAsync(url,data,contentType,compress,headers)
        contentType=contentType or R.Enum.HttpContentType.ApplicationJson
        assert(typeof(contentType)=='EnumItem' and contentType.EnumType==R.Enum.HttpContentType,"Invalid HttpContentType")
        local mime=contentTypes[contentType.Name];assert(mime,"Unsupported HttpContentType")
        assert(compress==nil or type(compress)=="boolean","compress must be a boolean")
        headers=table.clone(headers or {})
        local hasType=false;for key in headers do if string.lower(key)=='content-type' then hasType=true end end
        if not hasType then headers['Content-Type']=mime end
        return bodyOnly(self:RequestAsync({Url=url,Method='POST',Body=data,Headers=headers,
            Compress=if compress then R.Enum.HttpCompression.Gzip else R.Enum.HttpCompression.None}))
    end
end
