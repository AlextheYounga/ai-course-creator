import axios from 'axios';

const host = 'http://localhost:5002';

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
    }
}

export default flaskApi