import { io } from 'socket.io-client';

export const createSocket = () => {
  return io('wss://cloud-hackathon-venky.ue.r.appspot.com', {
    transports: ['polling', 'websocket'],
    reconnection: true,
    reconnectionAttempts: 10,
    reconnectionDelay: 1000,
    reconnectionDelayMax: 5000,
    timeout: 20000,
    forceNew: true,
    path: '/socket.io/'
  });
};