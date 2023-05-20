use zmq::{Context, REQ, PULL};
use serde::{Serialize, Deserialize};
use serde_json::{Value, from_str};

#[derive(Serialize, Deserialize, Debug)]
pub struct Command {
    pub action: String,
    pub action_type: Option<String>,
    pub symbol: Option<String>,
    pub chart_tf: Option<String>,
    pub from_date: Option<String>,
    pub to_date: Option<String>,
    pub id: Option<String>,
    pub magic: Option<String>,
    pub volume: Option<String>,
    pub price: Option<String>,
    pub stoploss: Option<String>,
    pub takeprofit: Option<String>,
    pub expiration: Option<String>,
    pub deviation: Option<String>,
    pub comment: Option<String>,
    pub chart_id: Option<String>,
    pub indicator_chart_id: Option<String>,
    pub chart_indicator_sub_window: Option<String>,
    pub style: Option<String>,
}

#[allow(dead_code)]
pub struct Functions {
    host: String,
    sys_socket: zmq::Socket,
    data_socket: zmq::Socket,
}


impl Functions {
    pub fn new(host: Option<String>) -> Self {
        let host = host.unwrap_or_else(|| String::from("192.168.1.153"));

        let context = Context::new();
        let sys_socket = context.socket(REQ).unwrap();
        sys_socket
            .connect(&format!("tcp://{}:{}", host, 15555))
            .unwrap();
        let data_socket = context.socket(PULL).unwrap();
        data_socket
            .connect(&format!("tcp://{}:{}", host, 15556))
            .unwrap();

        Functions {
            host,
            sys_socket,
            data_socket,
        }
    }

    pub fn send_json(&self, data: &Command) -> Result<(), Box<dyn std::error::Error>> {
        let json = serde_json::to_string(data)?;
        self.sys_socket.send(&json.as_bytes(), 0)?;
        Ok(())
    }

    pub fn recv_json(&self) -> Result<Value, Box<dyn std::error::Error>> {
        let msg = self.data_socket.recv_string(0)?;
        let data: Value = from_str(&msg.unwrap())?;
        Ok(data)
    }

    pub fn pull_reply(&self) -> Result<Value, Box<dyn std::error::Error>> {
        let reply = self.recv_json()?;
        Ok(reply)
    }

    pub fn command(&mut self, command: Command) -> Result<Value, Box<dyn std::error::Error>> {
        self.send_json(&command)?;
        self.pull_reply()
    }
}
