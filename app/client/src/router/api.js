import axios from 'axios';

const host = 'http://localhost:5001/api';

const flaskApi = {
    get(path) {
        const url = host + path
        return axios.get(url)
            .then((res) => {
                return res.data
            })
            .catch((error) => {
                console.error(error);
            });
    },
    put(path) {
        const url = host + path
        return axios.put(url)
            .then((res) => {
                return res.data
            })
            .catch((error) => {
                console.error(error);
            });
    },
    post(path, data = {}) {
        const url = host + path

        return axios.post(url, data)
            .then((res) => {
                return res.data
            })
            .catch((error) => {
                console.error(error);
            });
    },
}

export default flaskApi