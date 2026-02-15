import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import Home from './pages/Home'
import DiagramGenerator from './pages/DiagramGenerator'
import './App.css'

const router = createBrowserRouter([
  {
    path: "/",
    element: <Home />,
  },
  {
    path: "/diagram-generator",
    element: <DiagramGenerator />,
  },
])

function App() {
  return <RouterProvider router={router} />
}

export default App
