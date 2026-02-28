import React from 'react';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { Box, BottomNavigation, BottomNavigationAction, Paper, ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import FlightTakeoffIcon from '@mui/icons-material/FlightTakeoff';
import AirlinesIcon from '@mui/icons-material/Airlines';
import NotificationsIcon from '@mui/icons-material/Notifications';

import Deals from './pages/Deals';
import Airlines from './pages/Airlines';
import Notices from './pages/Notices';

import { requestForToken, onMessageListener } from './firebase';
import api from './api';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
  },
});

function App() {
  const navigate = useNavigate();
  const location = useLocation();

  React.useEffect(() => {
    // Request notification permissions and Firebase token
    const setupNotifications = async () => {
      const token = await requestForToken();
      if (token) {
        try {
          // Subscribe the token to the global 'all_users' topic via the backend
          await api.post('/admin/subscribe', { token, topic: 'all_users' });
          console.log('Successfully subscribed to all_users topic');
        } catch (error) {
          console.error('Failed to subscribe token:', error);
        }
      }
    };
    setupNotifications();

    // Foreground push listener
    onMessageListener()
      .then((payload: any) => {
        console.log('Foreground message received: ', payload);
        // We could show an in-app toast here if needed
      })
      .catch((err) => console.log('failed: ', err));
  }, []);

  const getNavValue = () => {
    if (location.pathname === '/notices') return 1;
    if (location.pathname === '/airlines') return 2;
    return 0; // Default /deals
  };

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Box sx={{ pb: 7, height: '100vh', display: 'flex', flexDirection: 'column' }}>
        <Box sx={{ flex: 1, overflowY: 'auto', backgroundColor: 'background.default' }}>
          <Routes>
            <Route path="/" element={<Deals />} />
            <Route path="/airlines" element={<Airlines />} />
            <Route path="/notices" element={<Notices />} />
          </Routes>
        </Box>

        <Paper sx={{ position: 'fixed', bottom: 0, left: 0, right: 0, zIndex: 1000 }} elevation={3}>
          <BottomNavigation
            showLabels
            value={getNavValue()}
            onChange={(event, newValue) => {
              if (newValue === 0) navigate('/');
              if (newValue === 1) navigate('/notices');
              if (newValue === 2) navigate('/airlines');
            }}
          >
            <BottomNavigationAction label="이벤트" icon={<FlightTakeoffIcon />} />
            <BottomNavigationAction label="공지" icon={<NotificationsIcon />} />
            <BottomNavigationAction label="항공사" icon={<AirlinesIcon />} />
          </BottomNavigation>
        </Paper>
      </Box>
    </ThemeProvider>
  );
}

export default App;
