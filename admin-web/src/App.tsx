import { Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import AirlineDetail from './pages/AirlineDetail'
import AddAirline from './pages/AddAirline'
import NoticeList from './pages/NoticeList'
import PushNotification from './pages/PushNotification'
import './App.css'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/add" element={<AddAirline />} />
      <Route path="/airline/:id" element={<AirlineDetail />} />
      <Route path="/notices" element={<NoticeList />} />
      <Route path="/push" element={<PushNotification />} />
    </Routes>
  )
}

export default App
