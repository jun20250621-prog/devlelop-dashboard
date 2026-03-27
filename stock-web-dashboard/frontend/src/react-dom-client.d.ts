declare module 'react-dom/client' {
  import { ReactElement } from 'react';
  export function createRoot(container: Element): { render: (element: ReactElement) => void };
}