import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  CircularProgress,
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
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchNotices();
  }, []);

  const fetchNotices = async () => {
    try {
      const res = await api.get('/notices');
      setNotices(res.data.items || res.data || []);
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
      {notices.length === 0 ? (
        <Typography variant="body2">등록된 공지사항이 없습니다.</Typography>
      ) : (
        notices.map((notice) => (
          <Card
            key={notice.id}
            sx={{ mb: 2, cursor: 'pointer', bgcolor: 'background.paper' }}
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
