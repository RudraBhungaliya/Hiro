import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import './App.css'

// pages
import Home from './pages/Home'
import DiagramGenerator from './pages/DiagramGenerator'
import LoginSuccess from './pages/LoginSuccess'

const router = createBrowserRouter([
  {
    path: "/",
    element: <Home />
  },
  {
    path: "/diagram-generator",
    element: <DiagramGenerator />
  },
  {
    path: "/login-success",
    element: <LoginSuccess />
  },
])

function App() {
  return (
    <RouterProvider router={router} />
  )
}

export default App