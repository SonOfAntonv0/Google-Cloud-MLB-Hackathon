import axios from 'axios';

const api = axios.create({
  baseURL: 'https://cloud-hackathon-venky.ue.r.appspot.com',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json'
  }
});

export default api;