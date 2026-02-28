import { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  CircularProgress,
  Collapse,
  IconButton,
} from '@mui/material';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import api from '../api';

interface Deal {
  id: string;
  title: string;
  airline: string;
  url: string;
  event_start: string | null;
  event_end: string | null;
}

export default function Deals() {
  const [ongoing, setOngoing] = useState<Deal[]>([]);
  const [upcoming, setUpcoming] = useState<Deal[]>([]);
  const [expired, setExpired] = useState<Deal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [ongoingExpanded, setOngoingExpanded] = useState(true);
  const [upcomingExpanded, setUpcomingExpanded] = useState(true);
  const [expiredExpanded, setExpiredExpanded] = useState(true);

  useEffect(() => {
    fetchDeals();
  }, []);

  const fetchDeals = async () => {
    try {
      setLoading(true);
      const res = await api.get('/deals');
      const allDeals: Deal[] = res.data;

      const now = new Date();
      now.setHours(0, 0, 0, 0);

      const ongoingDeals = allDeals.filter(d => {
        if (!d.event_start && !d.event_end) return true;
        const start = d.event_start ? new Date(d.event_start) : null;
        const end = d.event_end ? new Date(d.event_end) : null;
        if (start) start.setHours(0, 0, 0, 0);
        if (end) end.setHours(23, 59, 59, 999);

        if (start && start > now) return false; // Upcoming
        if (end && end < now) return false; // Expired
        return true;
      });

      const upcomingDeals = allDeals.filter(d => {
        if (!d.event_start) return false;
        const start = new Date(d.event_start);
        start.setHours(0, 0, 0, 0);
        return start > now;
      });

      const expiredDeals = allDeals.filter(d => {
        if (!d.event_end) return false;
        const end = new Date(d.event_end);
        end.setHours(23, 59, 59, 999);

        const sevenDaysAgo = new Date(now);
        sevenDaysAgo.setDate(now.getDate() - 7);

        return end < now && end >= sevenDaysAgo;
      });

      setOngoing(ongoingDeals);
      setUpcoming(upcomingDeals);
      setExpired(expiredDeals);
    } catch (err: any) {
      setError(err.message || 'Error parsing deals');
    } finally {
      setLoading(false);
    }
  };

  const formatPeriod = (start: string | null, end: string | null) => {
    if (!start && !end) return '기간 미정';
    if (!start) return `~ ${end?.substring(0, 10)}`;
    if (!end) return `${start.substring(0, 10)} ~`;
    return `${start.substring(0, 10)} ~ ${end.substring(0, 10)}`;
  };

  if (loading && ongoing.length === 0 && upcoming.length === 0 && expired.length === 0) {
    return (
      <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" height="100%" p={4}>
        <CircularProgress />
        <Typography mt={2}>로딩 중...</Typography>
      </Box>
    );
  }

  return (
    <Box p={2}>
      {error && <Typography color="error">오류: {error}</Typography>}

      {/* Ongoing */}
      <Box
        display="flex"
        justifyContent="space-between"
        alignItems="center"
        onClick={() => setOngoingExpanded(!ongoingExpanded)}
        sx={{ cursor: 'pointer', py: 1 }}
      >
        <Typography variant="h6" fontWeight="bold">진행 중인 이벤트 ({ongoing.length})</Typography>
        <IconButton size="small">
          {ongoingExpanded ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
        </IconButton>
      </Box>
      <Collapse in={ongoingExpanded}>
        {ongoing.length === 0 ? (
          <Typography variant="body2" sx={{ mb: 2 }}>진행 중인 이벤트가 없습니다.</Typography>
        ) : (
          ongoing.map((deal) => (
            <Card
              key={deal.id}
              sx={{ mb: 2, bgcolor: 'rgba(144, 202, 249, 0.12)', border: 1, borderColor: 'primary.dark', cursor: 'pointer' }}
              onClick={() => window.open(deal.url, '_blank')}
            >
              <CardContent>
                <Typography variant="overline" color="primary.light" fontWeight="bold">{deal.airline}</Typography>
                <Typography variant="subtitle1" fontWeight="bold" color="text.primary">{deal.title}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {formatPeriod(deal.event_start, deal.event_end)}
                </Typography>
              </CardContent>
            </Card>
          ))
        )}
      </Collapse>

      {/* Upcoming */}
      <Box
        display="flex"
        justifyContent="space-between"
        alignItems="center"
        onClick={() => setUpcomingExpanded(!upcomingExpanded)}
        sx={{ cursor: 'pointer', py: 1, mt: 1 }}
      >
        <Typography variant="h6" fontWeight="bold">진행 예정인 이벤트 ({upcoming.length})</Typography>
        <IconButton size="small">
          {upcomingExpanded ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
        </IconButton>
      </Box>
      <Collapse in={upcomingExpanded}>
        {upcoming.length === 0 ? (
          <Typography variant="body2" sx={{ mb: 2 }}>진행 예정인 이벤트가 없습니다.</Typography>
        ) : (
          upcoming.map((deal) => (
            <Card
              key={deal.id}
              sx={{ mb: 2, bgcolor: 'background.paper', cursor: 'pointer', opacity: 0.7 }}
              onClick={() => window.open(deal.url, '_blank')}
            >
              <CardContent>
                <Typography variant="overline" color="text.secondary">{deal.airline}</Typography>
                <Typography variant="subtitle1" fontWeight="bold" color="text.primary">{deal.title}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {formatPeriod(deal.event_start, deal.event_end)}
                </Typography>
              </CardContent>
            </Card>
          ))
        )}
      </Collapse>

      {/* Expired */}
      <Box
        display="flex"
        justifyContent="space-between"
        alignItems="center"
        onClick={() => setExpiredExpanded(!expiredExpanded)}
        sx={{ cursor: 'pointer', py: 1, mt: 1 }}
      >
        <Typography variant="h6" fontWeight="bold" color="text.secondary">종료된 이벤트 ({expired.length})</Typography>
        <IconButton size="small">
          {expiredExpanded ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
        </IconButton>
      </Box>
      <Collapse in={expiredExpanded}>
        {expired.length === 0 ? (
          <Typography variant="body2" sx={{ mb: 2 }}>최근 종료된 이벤트가 없습니다.</Typography>
        ) : (
          expired.map((deal) => (
            <Card
              key={deal.id}
              sx={{ mb: 2, bgcolor: 'background.default', cursor: 'pointer', opacity: 0.5, border: '1px dashed grey' }}
              onClick={() => window.open(deal.url, '_blank')}
            >
              <CardContent>
                <Typography variant="overline" color="text.disabled">{deal.airline}</Typography>
                <Typography variant="subtitle1" fontWeight="bold" color="text.disabled" sx={{ textDecoration: 'line-through' }}>{deal.title}</Typography>
                <Typography variant="body2" color="text.disabled">
                  {formatPeriod(deal.event_start, deal.event_end)}
                </Typography>
              </CardContent>
            </Card>
          ))
        )}
      </Collapse>
    </Box>
  );
}
