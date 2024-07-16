import React, { useState, useEffect, useRef } from 'react';
import { fetchMessages, postMessage } from './api';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import {
  Container, Box, Typography, TextField, Button, List,
  ListItem, ListItemText, Paper, Divider, Chip
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import PersonIcon from '@mui/icons-material/Person';

function generateRandomUsername() {
  const adjectives = ["Cool", "Super", "Crazy", "Funny", "Happy"];
  const nouns = ["Cat", "Dog", "Fox", "Bear", "Tiger"];
  const adjective = adjectives[Math.floor(Math.random() * adjectives.length)];
  const noun = nouns[Math.floor(Math.random() * nouns.length)];
  return `${adjective}${noun}${Math.floor(Math.random() * 1000)}`;
}

const theme = createTheme({
  palette: {
    primary: {
      main: '#3f51b5',
    },
    secondary: {
      main: '#f50057',
    },
  },
});

function App() {
  const [messages, setMessages] = useState([]);
  const [username] = useState(generateRandomUsername());
  const [content, setContent] = useState('');
  const [onlineUsers, setOnlineUsers] = useState([]);
  const [status, setStatus] = useState('Connecting...');
  const ws = useRef(null);

  useEffect(() => {
    async function loadMessages() {
      const messages = await fetchMessages();
      if (Array.isArray(messages)) {
        setMessages(messages);
      } else {
        console.error("Fetched messages are not an array:", messages);
      }
    }
    loadMessages();

    ws.current = new WebSocket(`ws://${window.location.host}/ws`);
    ws.current.onopen = () => {
      setStatus('Connected');
      ws.current.send(JSON.stringify({ type: 'join', username }));
    };
    ws.current.onclose = () => {
      setStatus('Disconnected');
    };
    ws.current.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'message') {
        setMessages((prevMessages) => [...prevMessages, message.data]);
      } else if (message.type === 'users') {
        setOnlineUsers(message.data);
      } else if (message.type === 'clear') {
        setMessages([]);
      }
    };

    return () => {
      if (ws.current.readyState === WebSocket.OPEN) {
        ws.current.send(JSON.stringify({ type: 'leave', username }));
      }
      ws.current.close();
    };
  }, [username]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!username || !content) return;
    if (content.startsWith('/clear')) {
      await fetch('/api/messages', {
        method: 'DELETE',
      });
      setContent('');
      return;
    }
    const newMessage = await postMessage(username, content);
    if (newMessage) {
      setMessages([...messages, newMessage]);
      setContent('');
    } else {
      console.error("Failed to post new message");
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <Container maxWidth="lg" sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ textAlign: 'center', mt: 2 }}>
          Ephemeral Chat
          <Chip
            label={status}
            color={status === 'Connected' ? 'success' : 'error'}
            variant="outlined"
            size="small"
            sx={{ ml: 1 }}
          />
        </Typography>
        <Box sx={{ display: 'flex', flexGrow: 1, mb: 2 }}>
          <Paper elevation={3} sx={{ flexGrow: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
            <List sx={{ flexGrow: 1, overflow: 'auto', p: 2 }}>
              {Array.isArray(messages) ? messages.map((message) => (
                <ListItem key={message.id} alignItems="flex-start">
                  <ListItemText
                    primary={
                      <Typography component="div" variant="body1" color="text.primary">
                        <Box component="span" sx={{ fontWeight: 'bold', mr: 1 }}>
                          {message.username}
                        </Box>
                        <Typography component="span" variant="caption" color="text.secondary">
                          {new Date(message.timestamp).toLocaleString()}
                        </Typography>
                      </Typography>
                    }
                    secondary={
                      <Typography component="p" variant="body2" color="text.primary" sx={{ mt: 0.5 }}>
                        {message.content}
                      </Typography>
                    }
                  />
                </ListItem>
              )) : <Typography>Loading messages...</Typography>}
            </List>
            <Divider />
            <Box component="form" onSubmit={handleSubmit} sx={{ p: 2, backgroundColor: 'background.default' }}>
              <TextField
                fullWidth
                multiline
                rows={2}
                variant="outlined"
                placeholder="Type a message"
                value={content}
                onChange={(e) => setContent(e.target.value)}
                onKeyDown={handleKeyDown}
              />
              <Button
                type="submit"
                variant="contained"
                endIcon={<SendIcon />}
                sx={{ mt: 1 }}
              >
                Send
              </Button>
            </Box>
          </Paper>
          <Paper elevation={3} sx={{ width: 240, ml: 2, p: 2, overflow: 'auto' }}>
            <Typography variant="h6" gutterBottom>
              Online Users
            </Typography>
            <List dense>
              {onlineUsers.map((user, index) => (
                <ListItem key={index}>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <PersonIcon sx={{ mr: 1, fontSize: 'small' }} />
                        <Typography variant="body2">{user}</Typography>
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Box>
      </Container>
    </ThemeProvider>
  );
}

export default App;