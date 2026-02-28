import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Card,
  Switch,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
} from '@mui/material';
import api from '../api';

interface Airline {
  id: string;
  name: string;
}

export default function Airlines() {
  const [airlines, setAirlines] = useState<Airline[]>([]);
  const [loading, setLoading] = useState(true);
  const [prefs, setPrefs] = useState<Record<string, boolean>>({});
  const [masterToggle, setMasterToggle] = useState<boolean>(true);

  useEffect(() => {
    // Load master toggle
    const master = localStorage.getItem('app_notification_enabled');
    if (master !== null) {
      setMasterToggle(master === 'true');
    }

    // Load per-airline prefs
    const savedPrefs = localStorage.getItem('airline_notification_prefs');
    if (savedPrefs) {
      try {
        setPrefs(JSON.parse(savedPrefs));
      } catch (e) { }
    }

    fetchAirlines();
  }, []);

  const fetchAirlines = async () => {
    try {
      const res = await api.get('/airlines');
      setAirlines(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const isAirlineEnabled = (id: string) => {
    return prefs[id] !== false; // Default to true if not set
  };

  const handleToggleAirline = (id: string, currentStatus: boolean) => {
    const newPrefs = { ...prefs, [id]: !currentStatus };
    setPrefs(newPrefs);
    localStorage.setItem('airline_notification_prefs', JSON.stringify(newPrefs));
  };

  const handleMasterToggle = (checked: boolean) => {
    setMasterToggle(checked);
    localStorage.setItem('app_notification_enabled', String(checked));
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100%">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box p={2}>
      <Typography variant="h6" fontWeight="bold" sx={{ mb: 2 }}>추적 항공사 관리</Typography>

      <Card sx={{ mb: 3, bgcolor: 'background.paper' }}>
        <List>
          <ListItem>
            <ListItemText primary="앱 전체 알림 켜기" primaryTypographyProps={{ fontWeight: 'bold' }} />
            <ListItemSecondaryAction>
              <Switch
                edge="end"
                checked={masterToggle}
                onChange={(e) => handleMasterToggle(e.target.checked)}
                color="primary"
              />
            </ListItemSecondaryAction>
          </ListItem>
        </List>
      </Card>

      <Typography variant="subtitle2" sx={{ mb: 1, color: 'text.secondary' }}>개별 항공사 설정</Typography>
      <Card sx={{ bgcolor: 'background.paper', opacity: masterToggle ? 1 : 0.5, pointerEvents: masterToggle ? 'auto' : 'none' }}>
        <List>
          {airlines.map((airline, idx) => (
            <React.Fragment key={airline.id}>
              <ListItem divider={idx !== airlines.length - 1}>
                <ListItemText primary={airline.name} />
                <ListItemSecondaryAction>
                  <Switch
                    edge="end"
                    checked={isAirlineEnabled(airline.id)}
                    onChange={() => handleToggleAirline(airline.id, isAirlineEnabled(airline.id))}
                    color="primary"
                  />
                </ListItemSecondaryAction>
              </ListItem>
            </React.Fragment>
          ))}
        </List>
      </Card>
      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 2, textAlign: 'center' }}>
        알림을 받을 항공사를 켜고 끌 수 있습니다.
      </Typography>
    </Box>
  );
}
