import axios from "axios";

const api = axios.create({
    baseURL:"http://127.0.0.1:5000/estoque",
    headers: {
        "Content-Type": "application/json"
    },
    timeout: 30000,
});

export default api