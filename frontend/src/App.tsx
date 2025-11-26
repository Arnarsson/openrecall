import { Routes, Route, Navigate } from 'react-router-dom'
import MainLayout from './components/layout/MainLayout'
import TimelinePage from './pages/TimelinePage'
import SearchPage from './pages/SearchPage'
import StatsPage from './pages/StatsPage'
import GraphPage from './pages/GraphPage'
import EntitiesPage from './pages/EntitiesPage'

function App() {
  return (
    <MainLayout>
      <Routes>
        <Route path="/" element={<Navigate to="/timeline" replace />} />
        <Route path="/timeline" element={<TimelinePage />} />
        <Route path="/search" element={<SearchPage />} />
        <Route path="/graph" element={<GraphPage />} />
        <Route path="/entities" element={<EntitiesPage />} />
        <Route path="/stats" element={<StatsPage />} />
      </Routes>
    </MainLayout>
  )
}

export default App
