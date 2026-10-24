local encoding=game:GetService('EncodingService')
local raw=buffer.fromstring('hello, chatgpt\0Roblox buffers')
local encoded=encoding:Base64Encode(raw)
assert(buffer.tostring(encoding:Base64Decode(encoded))==buffer.tostring(raw))
print('Base64:',buffer.tostring(encoded))

local compressed=encoding:CompressBuffer(raw,Enum.CompressionAlgorithm.Zstd,3)
assert(encoding:GetDecompressedBufferSize(compressed,Enum.CompressionAlgorithm.Zstd)==buffer.len(raw))
assert(buffer.tostring(encoding:DecompressBuffer(compressed,Enum.CompressionAlgorithm.Zstd))==buffer.tostring(raw))
print('Buffer bytes:',buffer.len(raw),'compressed:',buffer.len(compressed))

for _,algorithm in Enum.HashAlgorithm:GetEnumItems() do
    local digest=encoding:ComputeStringHash(buffer.tostring(raw),algorithm)
    local hexadecimal=digest:gsub('.',function(byte) return string.format('%02x',byte:byte()) end)
    print(algorithm.Name,hexadecimal)
end
print('ENCODING EXAMPLE PASSED')
