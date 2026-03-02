import { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  CircularProgress,
  Chip,
  Select,
  MenuItem,
  FormControl,
} from '@mui/material';
import api from '../api';

interface Notice {
  id: string;
  title: string;
  airline?: string;
  airline_name?: string;
  is_special_deal?: boolean;
  source_url: string;
  created_at: string;
}

export default function Notices() {
  const [notices, setNotices] = useState<Notice[]>([]);
  const [filteredNotices, setFilteredNotices] = useState<Notice[]>([]);
  const [loading, setLoading] = useState(true);
  const [airlines, setAirlines] = useState<string[]>([]);

  const [filterType, setFilterType] = useState<'ALL' | 'DEAL' | 'AIRLINE'>('ALL');
  const [selectedAirline, setSelectedAirline] = useState<string>('');

  useEffect(() => {
    fetchNotices();
  }, []);

  useEffect(() => {
    let filtered = notices;
    if (filterType === 'DEAL') {
      filtered = notices.filter(n => n.is_special_deal);
    } else if (filterType === 'AIRLINE' && selectedAirline) {
      filtered = notices.filter(n => (n.airline || n.airline_name || '일반 공지') === selectedAirline);
    }
    setFilteredNotices(filtered);
  }, [filterType, selectedAirline, notices]);

  const fetchNotices = async () => {
    try {
      const res = await api.get('/notices');
      const items = res.data.items || res.data || [];
      setNotices(items);
      const uniqueAirlines = Array.from(new Set(items.map((n: Notice) => n.airline || n.airline_name || '일반 공지'))) as string[];
      uniqueAirlines.sort((a, b) => a.localeCompare(b));
      setAirlines(uniqueAirlines);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
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
      <Typography variant="h6" fontWeight="bold" sx={{ mb: 2 }}>항공사 공지사항</Typography>

      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
        <Chip
          label="전체"
          clickable
          color={filterType === 'ALL' ? 'primary' : 'default'}
          onClick={() => setFilterType('ALL')}
        />
        <Chip
          label="특가"
          clickable
          color={filterType === 'DEAL' ? 'primary' : 'default'}
          onClick={() => setFilterType('DEAL')}
        />
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <Select
            value={filterType === 'AIRLINE' ? selectedAirline : ''}
            displayEmpty
            onChange={(e) => {
              const val = e.target.value;
              if (val) {
                setFilterType('AIRLINE');
                setSelectedAirline(val);
              }
            }}
            renderValue={(selected) => {
              if (!selected || filterType !== 'AIRLINE') {
                return <em>항공사 선택</em>;
              }
              return selected;
            }}
            sx={{ bgcolor: 'background.paper', borderRadius: 1 }}
          >
            <MenuItem value="" disabled><em>항공사 선택</em></MenuItem>
            {airlines.map(al => (
              <MenuItem key={al} value={al}>{al}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

      {filteredNotices.length === 0 ? (
        <Typography variant="body2" sx={{ mt: 4, textAlign: 'center', color: 'text.secondary' }}>해당 조건의 공지사항이 없습니다.</Typography>
      ) : (
        filteredNotices.map((notice) => (
          <Card
            key={notice.id}
            sx={{ mb: 2, cursor: 'pointer', bgcolor: 'background.paper', transition: '0.2s', '&:hover': { transform: 'translateY(-2px)', boxShadow: 3 } }}
            onClick={() => window.open(notice.source_url, '_blank')}
          >
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Typography variant="overline" color="secondary">
                  {notice.airline || notice.airline_name || '일반 공지'}
                </Typography>
                {notice.is_special_deal && (
                  <Typography variant="caption" sx={{ bgcolor: 'error.main', color: 'white', px: 1, py: 0.5, borderRadius: 1, fontWeight: 'bold' }}>
                    특가
                  </Typography>
                )}
              </Box>
              <Typography variant="subtitle1" fontWeight="bold">
                {notice.title}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                {new Date(notice.created_at).toLocaleDateString()}
              </Typography>
            </CardContent>
          </Card>
        ))
      )}
    </Box>
  );
}
