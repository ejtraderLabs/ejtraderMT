mod connection;

use connection::{Command, Functions};
use std::env;

fn main() {
    let args: Vec<String> = env::args().collect();
    let host = args.get(1).cloned().unwrap_or_else(|| String::from("192.168.1.153"));

    let mut functions = Functions::new(host);
    let mut command = Command::default();
    command.action = "ACCOUNT".to_string();

    match functions.command(command) {
        Ok(value) => println!("Value: {}", value),
        Err(e) => println!("Error: {}", e),
    }
}
