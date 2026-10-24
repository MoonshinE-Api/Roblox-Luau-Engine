return function(R)
    local native=__host_datetime
    local minimum,maximum=-17987443200,253402300799
    local methods,library={},{}
    local function truncate(n)
        local value=if n<0 then math.ceil(n) else math.floor(n)
        return if value==0 then 0 else value
    end
    local function numeric(value)
        local n=if type(value)=="number" then value elseif type(value)=="string" then tonumber(value) else nil
        assert(n~=nil,"Expected number");return n
    end
    local function int32(value)
        value=truncate(numeric(value))
        return if value~=value or value< -2147483648 or value>=2147483648 then -2147483648 else value
    end
    local function valid(seconds)
        assert(seconds==seconds and seconds>=minimum and seconds<=maximum,"DateTime fields out of range (1400 to 9999)")
        return seconds
    end
    local function days(year,month,day)
        local y=year-(if month<=2 then 1 else 0)
        local era=math.floor(y/400);local within=y-era*400
        local shifted=month+(if month>2 then -3 else 9)
        return era*146097+within*365+math.floor(within/4)-math.floor(within/100)+math.floor((153*shifted+2)/5)+day-1-719468
    end
    local function civil(seconds,micro)
        valid(seconds)
        local z=math.floor(seconds/86400)+719468;local era=math.floor(z/146097)
        local doe=z-era*146097
        local yoe=math.floor((doe-math.floor(doe/1460)+math.floor(doe/36524)-math.floor(doe/146096))/365)
        local y=yoe+era*400;local doy=doe-(365*yoe+math.floor(yoe/4)-math.floor(yoe/100))
        local mp=math.floor((5*doy+2)/153);local day=doy-math.floor((153*mp+2)/5)+1
        local month=mp+(if mp<10 then 3 else -9);y+=if month<=2 then 1 else 0
        local t=seconds%86400
        return {Year=y,Month=month,Day=day,Hour=math.floor(t/3600),Minute=math.floor(t/60)%60,Second=t%60,Millisecond=math.floor(micro/1000)}
    end
    local function data(self) assert(typeof(self)=="DateTime","Expected DateTime");return R.values[self] end
    local function millis(d)
        local value=d.seconds*1000+math.floor(d.micro/1000)
        if d.seconds<0 and d.micro%1000~=0 then value+=1 end
        return value
    end
    local function make(seconds,micro,localSeconds)
        local carry=math.floor(micro/1000000);seconds+=carry;micro-=carry*1000000
        valid(seconds)
        local d={seconds=seconds,micro=micro,localSeconds=localSeconds or native(1,seconds)}
        assert(d.localSeconds,"Host local time conversion failed")
        return R.makeValue("DateTime",d,function(_,key,value)
            if key=="UnixTimestampMillis" then return millis(value) end
            if key=="UnixTimestamp" then return value.seconds+(if value.seconds<0 and value.micro>0 then 1 else 0) end
            if methods[key] then return methods[key] end
            error(tostring(key).." is not a valid member of DateTime",2)
        end,{
            __tostring=function(self) return string.format("%.0f",millis(data(self))) end,
            __eq=function(a,b)
                if typeof(a)~="DateTime" or typeof(b)~="DateTime" then return false end
                local x,y=data(a),data(b);return x.seconds==y.seconds and x.micro==y.micro
            end,
        })
    end
    function library.fromUnixTimestamp(...)
        local n=if select("#",...)==0 then 0 else numeric(...)
        return make(valid(truncate(n)),0)
    end
    function library.fromUnixTimestampMillis(...)
        local n=if select("#",...)==0 then 0 else truncate(numeric(...))
        assert(n==n and n>=minimum*1000 and n<=maximum*1000+999,"UnixTimestampMillis out of range")
        local seconds=math.floor(n/1000)
        return make(seconds,(n-seconds*1000)*1000)
    end
    function library.now() return library.fromUnixTimestampMillis(native(0)) end
    local function componentSeconds(args)
        local defaults={1970,1,1,0,0,0,0};local values={}
        for i=1,7 do values[i]=if i>args.n then defaults[i] else int32(args[i]) end
        local year,month,day=values[1]%65536,values[2]%65536,values[3]%65536
        assert(year>=1400 and year<=9999 and month>=1 and month<=12,"Invalid DateTime year or month")
        local leap=year%4==0 and (year%100~=0 or year%400==0)
        local monthDays=({31,if leap then 29 else 28,31,30,31,30,31,31,30,31,30,31})[month]
        assert(day>=1 and day<=monthDays,"Invalid DateTime day")
        local h,m,s=values[4],values[5],values[6]
        local fraction=(values[7]*1000)%4294967296
        if fraction>=2147483648 then fraction-=4294967296 end
        -- Boost to_tick_count treats any negative unit as a negative duration.
        local sign=if h<0 or m<0 or s<0 or fraction<0 then -1 else 1
        local seconds=days(year,month,day)*86400+sign*(math.abs(h)*3600+math.abs(m)*60+math.abs(s))
        local micro=sign*math.abs(fraction)
        local carry=math.floor(micro/1000000)
        return valid(seconds+carry),micro-carry*1000000
    end
    function library.fromUniversalTime(...)
        local seconds,micro=componentSeconds(table.pack(...))
        return make(seconds,micro)
    end
    function library.fromLocalTime(...)
        local seconds,micro=componentSeconds(table.pack(...))
        local utc=native(2,seconds);assert(utc,"Host local time conversion failed")
        return make(utc,micro,seconds)
    end
    function methods:ToUniversalTime() local d=data(self);return civil(d.seconds,d.micro) end
    function methods:ToLocalTime() local d=data(self);return civil(d.localSeconds,d.micro) end
    function methods:ToIsoDate()
        local d=data(self);local t=civil(d.seconds,d.micro)
        local fraction=if d.micro==0 then "" else string.format(".%06d",d.micro)
        return string.format("%04d-%02d-%02dT%02d:%02d:%02d%sZ",t.Year,t.Month,t.Day,t.Hour,t.Minute,t.Second,fraction)
    end
    function library.fromIsoDate(value)
        assert(type(value)=="string" or type(value)=="number","Expected ISO 8601 string")
        value=tostring(value):match("^[^%z]*")
        local year,month,day,hour,minute,second,tail=value:match("^(%d%d%d%d)%-(%d%d)%-(%d%d)[Tt ](%d%d):(%d%d):(%d%d)(.*)$")
        assert(year,"Invalid ISO 8601 date")
        local fraction=""
        if tail:sub(1,1)=="." then
            fraction,tail=tail:match("^%.(%d+)(.*)$");assert(fraction,"Invalid ISO fraction")
        end
        local offset=0
        if tail~="Z" and tail~="z" and tail~="" then
            local sign,oh,om=tail:match("^([+-])(%d%d):(%d%d)$")
            if not sign then sign,oh,om=tail:match("^([+-])(%d%d)(%d%d)$") end
            assert(sign and tonumber(oh)<=23 and tonumber(om)<=59,"Invalid ISO timezone")
            offset=(tonumber(oh)*3600+tonumber(om)*60)*(if sign=="-" then -1 else 1)
        end
        hour,minute,second=tonumber(hour),tonumber(minute),tonumber(second)
        assert(hour<=23 and minute<=59 and second<=59,"Invalid ISO time")
        local base=library.fromUniversalTime(tonumber(year),tonumber(month),tonumber(day),hour,minute,second)
        local micro=tonumber((fraction.."000000"):sub(1,6))
        return make(data(base).seconds-offset,micro)
    end
    local tokens=table.clone(R.dateTimeTokens)
    table.sort(tokens,function(a,b) return if #a==#b then a>b else #a>#b end)
    local function format(seconds,micro,pattern,locale,depth)
        assert(depth<12,"DateTime format recursion limit")
        local config=R.dateTimeLocales[locale] or R.dateTimeLocales["en-us"]
        local t=civil(seconds,micro);local dayNumber=math.floor(seconds/86400)
        local weekday=(dayNumber+4)%7+1;local yearDay=dayNumber-days(t.Year,1,1)+1
        local meridiem=config.meridiem or R.dateTimeLocales["en-us"].meridiem
        local selected=meridiem[1];local clock=t.Hour*100+t.Minute
        for _,entry in meridiem do if entry.startFrom<=clock then selected=entry end end
        local values={YYYY=string.format("%04d",t.Year),YY=string.format("%02d",t.Year%100),
            MMMM=config.months[t.Month],MMM=config.monthsShort[t.Month],MM=string.format("%02d",t.Month),M=t.Month,
            DDDD=string.format("%03d",yearDay),DDD=yearDay,DD=string.format("%02d",t.Day),D=t.Day,
            dddd=config.weekdays[weekday],ddd=config.weekdaysShort[weekday],dd=config.weekdaysMin[weekday],d=weekday-1,
            HH=string.format("%02d",t.Hour),H=t.Hour,hh=string.format("%02d",(t.Hour+11)%12+1),h=(t.Hour+11)%12+1,
            mm=string.format("%02d",t.Minute),m=t.Minute,ss=string.format("%02d",t.Second),s=t.Second,
            SSS=string.format("%03d",t.Millisecond),SS=string.format("%02d",math.floor(t.Millisecond/10)),S=math.floor(t.Millisecond/100),
            A=selected.upperCase,a=selected.lowerCase}
        local result={};local i=1
        while i<=#pattern do
            if pattern:sub(i,i)=="[" then
                local last=pattern:find("]",i+1,true) or #pattern+1
                table.insert(result,pattern:sub(i+1,last-1));i=last+1
            else
                local matched
                for _,token in tokens do
                    if pattern:sub(i,i+#token-1)==token then
                        local replacement=values[token]
                        if replacement==nil then
                            local composite=config.longDateFormat[token] or R.dateTimeLocales["en-us"].longDateFormat[token]
                            replacement=format(seconds,micro,composite,locale,depth+1)
                        end
                        table.insert(result,tostring(replacement));i+=#token;matched=true;break
                    end
                end
                if not matched then table.insert(result,pattern:sub(i,i));i+=1 end
            end
        end
        return table.concat(result)
    end
    local function formatted(self,pattern,locale,localTime)
        assert((type(pattern)=="string" or type(pattern)=="number") and (type(locale)=="string" or type(locale)=="number"),"Expected format and locale strings")
        pattern=tostring(pattern):match("^[^%z]*")
        locale=tostring(locale):match("^[^%z]*"):lower():gsub("_","-")
        if not R.dateTimeLocales[locale] then locale=R.dateTimeFallbacks[locale] or "en-us" end
        local d=data(self)
        return format(if localTime then d.localSeconds else d.seconds,d.micro,pattern,locale,0)
    end
    function methods:FormatUniversalTime(pattern,locale) return formatted(self,pattern,locale,false) end
    function methods:FormatLocalTime(pattern,locale) return formatted(self,pattern,locale,true) end
    R.datatypes.DateTime=table.freeze(library)
end
