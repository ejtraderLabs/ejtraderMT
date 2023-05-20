mod connection;
use connection::Functions; 
use connection::Command; 

fn main() {
    let mut functions = Functions::new(None);

    let command = Command {
        action: "ACCOUNT".to_string(),
        action_type: None,
        symbol: None,
        chart_tf: None,
        from_date: None,
        to_date: None,
        id: None,
        magic: None,
        volume: None,
        price: None,
        stoploss: None,
        takeprofit: None,
        expiration: None,
        deviation: None,
        comment: None,
        chart_id: None,
        indicator_chart_id: None,
        chart_indicator_sub_window: None,
        style: None,
    };
    
    
    match functions.command(command) {
        Ok(value) => println!("Value: {}", value),
        Err(e) => println!("Error: {}", e),
    }
}