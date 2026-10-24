return function(R)
    local M={};R.classMethods.EncodingService=M
    local LIMIT=50*1024*1024
    local function transform(action,bytes,algorithm,level)
        assert(#bytes<=LIMIT,'EncodingService input exceeds host limit 50 MiB')
        local options={Action=action,Algorithm=algorithm,Level=level}
        local id=__host_http(4,R.jsonEncode(options),bytes)
        assert(id>0,'Unable to start host encoding operation')
        local ok,body,metadata=pcall(__host_http,1,id)
        __host_http(2,id)
        if not ok then error(body,3) end
        assert(metadata,'Missing synchronous encoding result')
        local result=R.jsonDecode(metadata)
        if result.Error then error(result.Error,3) end
        return body,result
    end
    local function bytes(input)
        assert(type(input)=='buffer','EncodingService expects a buffer')
        assert(buffer.len(input)<=LIMIT,'EncodingService input exceeds host limit 50 MiB')
        return buffer.tostring(input)
    end
    local function compression(algorithm)
        assert(algorithm==R.Enum.CompressionAlgorithm.Zstd,'Expected Enum.CompressionAlgorithm.Zstd')
        return 'Zstd'
    end
    local function hashAlgorithm(algorithm)
        for _,value in R.Enum.HashAlgorithm:GetEnumItems() do if algorithm==value then return value.Name end end
        error('Expected Enum.HashAlgorithm',3)
    end
    function M:Base64Encode(input) return buffer.fromstring((transform('base64-encode',bytes(input)))) end
    function M:Base64Decode(input) return buffer.fromstring((transform('base64-decode',bytes(input)))) end
    function M:CompressBuffer(input,algorithm,level)
        if level==nil then level=1 end
        assert(type(level)=='number' and level%1==0 and level>=-7 and level<=22,'Unsupported Zstd compression level')
        return buffer.fromstring((transform('compress',bytes(input),compression(algorithm),level)))
    end
    function M:DecompressBuffer(input,algorithm)
        return buffer.fromstring((transform('decompress',bytes(input),compression(algorithm))))
    end
    function M:GetDecompressedBufferSize(input,algorithm)
        local _,result=transform('size',bytes(input),compression(algorithm));return result.Size
    end
    function M:ComputeBufferHash(input,algorithm)
        return buffer.fromstring((transform('hash',bytes(input),hashAlgorithm(algorithm))))
    end
    function M:ComputeStringHash(input,algorithm)
        assert(type(input)=='string','ComputeStringHash expects a string')
        return (transform('hash',input,hashAlgorithm(algorithm)))
    end
    -- Older scripts used explicit Zstd method names; modern API takes an enum.
    function M:CompressBufferZstd(input,level) return self:CompressBuffer(input,R.Enum.CompressionAlgorithm.Zstd,level) end
    function M:DecompressBufferZstd(input) return self:DecompressBuffer(input,R.Enum.CompressionAlgorithm.Zstd) end
    function M:GetDecompressedBufferSizeZstd(input) return self:GetDecompressedBufferSize(input,R.Enum.CompressionAlgorithm.Zstd) end
    R.encodingTransform=transform
end
