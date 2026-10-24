// Optional reference generator; Moment is a development tool, not a runtime dependency.
// node generate_datetime_formats.cjs /absolute/path/to/moment
const fs=require('fs');const path=require('path');
const moment=require(process.argv[2]);
if(moment.version!=='2.30.1')throw new Error('Reference version must be 2.30.1');
const root=path.resolve(__dirname,'..');
const source=JSON.parse(fs.readFileSync(path.join(root,'data/datetime_recovery.json'),'utf8'));
const vectors=[];
for(const [name,config] of Object.entries(source.locales)){
    const locale='recovered-'+name;
    moment.defineLocale(locale,{...config,meridiem:(hour,minute,lower)=>{
        let value=config.meridiem[0];
        for(const entry of config.meridiem)if(entry.startFrom<=hour*100+minute)value=entry;
        return lower?value.lowerCase:value.upperCase;
    }});
    const stamps=[];
    for(let month=0;month<12;month++)stamps.push(Date.UTC(2024,month,28,13,4,5,678));
    for(const entry of config.meridiem){
        const minute=Math.floor(entry.startFrom/100)*60+entry.startFrom%100;
        stamps.push(Date.UTC(2024,1,29,0,minute,5,123));
        if(minute>0)stamps.push(Date.UTC(2024,1,29,0,minute-1,59,999));
    }
    const formats=[source.tokens.slice(0,27).join(' '),...Object.keys(config.longDateFormat),'[literal YYYY] YYYY-MM-DDTHH:mm:ss.SSS'];
    for(const ms of stamps)for(const format of formats){
        vectors.push([ms,name,format,moment.utc(ms).locale(locale).format(format)]);
    }
}
const result={reference:'Moment.js 2.30.1 formatter with recovered Studio locale tables',
    source_locale_sha256:source.locale_file_sha256,vector_count:vectors.length,vectors,
    limits:'Does not validate native C++ stream execution, locale fallback selection, invalid ISO handling or timezone rules.'};
fs.writeFileSync(path.join(root,'tests/fixtures/datetime_format_vectors.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({reference:result.reference,vector_count:vectors.length}));
