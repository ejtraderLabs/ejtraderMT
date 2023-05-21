use pyo3::prelude::*;
use zmq::{Context, REQ, PULL};
use serde::{Serialize, Deserialize};
use serde_json::{Value, from_str};
use pyo3::PyErr;
use pyo3::types::PyDict;


#[derive(Serialize, Deserialize, Debug, Default, Clone)]
#[serde(rename_all = "camelCase")]
#[pyclass]
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
}


#[pymethods]
impl Command {
    #[new]
    fn new(action: String) -> Self {
        Command {
            action,
            ..Default::default()
        }
    }
}

#[pyclass]
pub struct Functions {
    #[allow(dead_code)]
    host: String,
    sys_socket: zmq::Socket,
    data_socket: zmq::Socket,
}

#[pymethods]
impl Functions {
    #[new]
    fn new(host: String) -> PyResult<Self> {
        let context = Context::new();
        let sys_socket = context.socket(REQ).expect("Failed to create subscriber socket");
        sys_socket
            .connect(&format!("tcp://{}:{}", &host, 15555))
            .unwrap();
        // Aqui nós configuramos o timeout para recebimento e envio em milissegundos
        sys_socket.set_rcvtimeo(60000).unwrap(); // 1 minuto
        sys_socket.set_sndtimeo(60000).unwrap(); // 1 minuto

        let data_socket = context.socket(PULL).unwrap();
        data_socket
            .connect(&format!("tcp://{}:{}", &host, 15556))
            .unwrap();
        data_socket.set_rcvtimeo(60000).unwrap(); // 1 minuto
        data_socket.set_sndtimeo(60000).unwrap(); // 1 minuto
        Ok(Functions {
            host,
            sys_socket,
            data_socket,
        })
    }

    fn send_json(&self, data: Command) -> PyResult<()> {
        let json = serde_json::to_string(&data)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyException, _>(format!("{}", e)))?;
        self.sys_socket.send(&json.as_bytes(), 0)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyException, _>(format!("{}", e)))?;
        let msg = self.sys_socket.recv_string(0)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyException, _>(format!("{:?}", e)))?;
        match msg {
            Ok(message) => {
                assert_eq!(message, "OK", "Something wrong on server side");
                Ok(())
            },
            Err(_) => Err(PyErr::new::<pyo3::exceptions::PyException, _>("Received message could not be converted to string")),
        }
    }
    


    fn recv_json(&self) -> PyResult<String> {
        match self.data_socket.recv_string(0) {
            Ok(Ok(msg_str)) => {
                let data: Value = from_str(&msg_str)
                    .map_err(|e| PyErr::new::<pyo3::exceptions::PyException, _>(format!("{}", e)))?;
                Ok(data.to_string())
            },
            Ok(Err(_)) => Err(PyErr::new::<pyo3::exceptions::PyException, _>("Received message could not be converted to string")),
            Err(_) => Err(PyErr::new::<pyo3::exceptions::PyException, _>("Failed to receive string")),
        }
    }
    

    
    fn command(&self, action: String, kwargs: Option<&PyDict>) -> PyResult<String> {
        let mut command = Command::new(action);
        if let Some(kwargs) = kwargs {
            for (key, value) in kwargs {
                let key = key.to_string();
                let value: String = value.extract()?;
                match key.as_str() {
                    "actionType" => command.action_type = Some(value),
                    "symbol" => command.symbol = Some(value),
                    "chartTF" => command.chart_tf = Some(value),
                    "fromDate" => command.from_date = Some(value),
                    "toDate" => command.to_date = Some(value),
                    "id" => command.id = Some(value),
                    "magic" => command.magic = Some(value),
                    "volume" => command.volume = Some(value),
                    "price" => command.price = Some(value),
                    "stoploss" => command.stoploss = Some(value),
                    "takeprofit" => command.takeprofit = Some(value),
                    "expiration" => command.expiration = Some(value),
                    "deviation" => command.deviation = Some(value),
                    "comment" => command.comment = Some(value),
                    _ => return Err(PyErr::new::<pyo3::exceptions::PyException, _>(format!("Unknown key in **kwargs ERROR"))),
                }
            }
        }
        self.send_json(command)?;
        let reply = self.recv_json()?;
        Ok(reply)
    }
    
    
    
    
}

#[pymodule]
fn ejtradermtlib(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<Command>()?;
    m.add_class::<Functions>()?;
    Ok(())
}


#[cfg(test)]
mod tests {
    use super::*;
    use pyo3::types::IntoPyDict;

    #[test]
    fn test_command() {
        let gil = Python::acquire_gil();
        let py = gil.python();
        let command = Command::new(String::from("ACCOUNT"));
        let locals = [("command", command)].into_py_dict(py);
        let value: String = py
            .eval("command.action", Some(locals), None)
            .unwrap()
            .extract()
            .unwrap();
        assert_eq!(value, "ACCOUNT");
    }
}
