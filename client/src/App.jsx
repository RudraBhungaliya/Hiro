import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import { GoogleOAuthProvider } from '@react-oauth/google'
import { UserProvider } from './context/UserContext'
import './App.css'

// pages
import Home from './pages/Home'
import DiagramGenerator from './pages/DiagramGenerator'

const router = createBrowserRouter([
  {
    path: "/",
    element: <Home />
  },
  {
    path: "/diagram-generator",
    element: <DiagramGenerator />
  },
])

function App() {
  return (
    <GoogleOAuthProvider clientId={import.meta.env.VITE_GOOGLE_CLIENT_ID}>
      <UserProvider>
        <RouterProvider router={router} />
      </UserProvider>
    </GoogleOAuthProvider>
  )
}

export default App
