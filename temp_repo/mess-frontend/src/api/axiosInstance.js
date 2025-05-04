import axios from 'axios';

const API = axios.create({
  baseURL: 'http://52.2.93.132:5000/api',
});

API.interceptors.request.use((req) => {
  const token = localStorage.getItem('token');
  if (token) {
    req.headers.Authorization = `Bearer ${token}`;
  }
  return req;
});

export default API;
