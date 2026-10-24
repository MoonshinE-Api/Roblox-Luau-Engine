//! Source-to-bytecode compiler only. Execution is performed by the recovered VM.
use std::{env,fs,process};
use std::path::Path;
fn compile(input:&Path,output:&Path,label:&str)->Result<(),Box<dyn std::error::Error>> {
    let source=fs::read(input)?;
    let bytecode=mlua::chunk::Compiler::new().set_optimization_level(1).set_debug_level(1)
        .compile(source).map_err(|error|format!("{label}: {error}"))?;
    fs::write(output,bytecode)?;
    Ok(())
}
fn main() {
    let args: Vec<_> = env::args_os().collect();
    if args.len()!=3 { eprintln!("usage: recovery-luau-compile source.luau output.luauc | --batch manifest");process::exit(2); }
    let result=(|| -> Result<(),Box<dyn std::error::Error>> {
        if args[1]=="--batch" {
            // NUL-separated input/output/diagnostic-label triples avoid command
            // line size limits and quoting ambiguities for large Windows projects.
            let manifest=fs::read_to_string(&args[2])?;
            if !manifest.ends_with('\0') {return Err("Invalid batch manifest terminator".into());}
            let fields:Vec<_>=manifest[..manifest.len()-1].split('\0').collect();
            if fields.len()%3!=0 {return Err("Invalid batch manifest fields".into());}
            for job in fields.chunks_exact(3) {compile(Path::new(job[0]),Path::new(job[1]),job[2])?;}
        }else{compile(Path::new(&args[1]),Path::new(&args[2]),&args[1].to_string_lossy())?;}
        Ok(())
    })();
    if let Err(error)=result {eprintln!("{error}");process::exit(1);}
}
