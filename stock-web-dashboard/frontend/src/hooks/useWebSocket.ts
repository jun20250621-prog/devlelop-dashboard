// WebSocket Hook

import { useEffect, useRef, useCallback } from 'react';
import { useStockStore } from '../store/stockStore';

export function useWebSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const { setQuotes, setWsConnected } = useStockStore();
  
  const connect = useCallback(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/quotes`;
    
    const ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
      console.log('WebSocket connected');
      setWsConnected(true);
    };
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'prices') {
          setQuotes(data.data);
        }
      } catch (e) {
        console.error('WS message error:', e);
      }
    };
    
    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setWsConnected(false);
      // 重新連線
      setTimeout(connect, 3000);
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    wsRef.current = ws;
  }, [setQuotes, setWsConnected]);
  
  useEffect(() => {
    connect();
    return () => {
      wsRef.current?.close();
    };
  }, [connect]);
  
  return wsRef;
}