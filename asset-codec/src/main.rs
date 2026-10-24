//! Data-only Roblox model conversion. This executable never evaluates scripts.
use std::{env,fs,io::{BufReader,Read,Write},process};
fn main() {
    let args:Vec<_>=env::args_os().collect();
    if args.len()!=4 {eprintln!("usage: recovery-asset-codec to-xml|to-binary|blake3 input output");process::exit(2);}
    let result=(|| -> Result<(),Box<dyn std::error::Error>> {
        let mut file=BufReader::new(fs::File::open(&args[2])?);
        let mut output=fs::File::create(&args[3])?;
        if args[1]=="to-xml" {
            let model=rbx_binary::from_reader(file)?;
            rbx_xml::to_writer_default(output,&model,model.root().children())?;
        }else if args[1]=="to-binary" {
            let model=rbx_xml::from_reader_default(file)?;
            rbx_binary::to_writer(output,&model,model.root().children())?;
        }else if args[1]=="blake3" {
            let mut hash=blake3::Hasher::new();
            let mut block=[0u8;65536];
            loop {let length=file.read(&mut block)?;if length==0 {break;}hash.update(&block[..length]);}
            output.write_all(hash.finalize().as_bytes())?;
        }else{return Err("Unknown conversion direction".into());}
        Ok(())
    })();
    if let Err(error)=result {eprintln!("{error}");process::exit(1);}
}
