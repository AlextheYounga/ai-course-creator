import axios from 'axios';

const host = 'http://localhost:5001/api';

const flaskApi = {
    get(path: string) {
        const url = host + path
        return axios.get(url)
            .then((res) => {
                return res.data
            })
            .catch((error) => {
                console.error(error);
            });
    },
    post(path: string, data: any = {}) {
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