import React, { useState } from 'react';
import { 
  Box, 
  Paper, 
  Typography, 
  TextField, 
  IconButton, 
  Fab, 
  Collapse, 
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Divider
} from '@mui/material';
import { styled } from '@mui/material/styles';
import ChatIcon from '@mui/icons-material/Chat';
import SendIcon from '@mui/icons-material/Send';
import CloseIcon from '@mui/icons-material/Close';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import PersonIcon from '@mui/icons-material/Person';

/**
 * Conversational Assistant component that provides natural language
 * interaction with the Overseer System.
 * 
 * This implements the Conversational Everywhere design principle by
 * providing a chat interface accessible from anywhere in the application.
 */
const ConversationalAssistant = () => {
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'assistant',
      text: 'Hello! I\'m your Overseer Assistant. How can I help you today?',
      timestamp: new Date().toISOString(),
    },
  ]);

  // Toggle chat window
  const toggleChat = () => {
    setOpen(!open);
  };

  // Handle input change
  const handleInputChange = (e) => {
    setInput(e.target.value);
  };

  // Handle message submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!input.trim()) return;
    
    // Add user message to chat
    const userMessage = {
      id: Date.now(),
      sender: 'user',
      text: input,
      timestamp: new Date().toISOString(),
    };
    
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    
    // Simulate assistant response (will be replaced with actual API call)
    setTimeout(() => {
      const assistantMessage = {
        id: Date.now() + 1,
        sender: 'assistant',
        text: 'I\'m processing your request. This is a placeholder response that will be replaced with actual AI-generated responses from the backend.',
        timestamp: new Date().toISOString(),
      };
      
      setMessages((prev) => [...prev, assistantMessage]);
    }, 1000);
  };

  // Styled components
  const ChatWindow = styled(Paper)(({ theme }) => ({
    width: 350,
    height: 500,
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden',
    borderRadius: 16,
    boxShadow: '0px 8px 20px rgba(0, 0, 0, 0.15)',
  }));

  const ChatHeader = styled(Box)(({ theme }) => ({
    padding: theme.spacing(2),
    backgroundColor: theme.palette.primary.main,
    color: theme.palette.primary.contrastText,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
  }));

  const ChatBody = styled(Box)(({ theme }) => ({
    flexGrow: 1,
    padding: theme.spacing(2),
    overflowY: 'auto',
    backgroundColor: theme.palette.background.default,
  }));

  const ChatFooter = styled(Box)(({ theme }) => ({
    padding: theme.spacing(2),
    borderTop: `1px solid ${theme.palette.divider}`,
    backgroundColor: theme.palette.background.paper,
  }));

  const MessageForm = styled('form')(({ theme }) => ({
    display: 'flex',
    alignItems: 'center',
  }));

  return (
    <>
      {/* Chat toggle button */}
      <Fab
        color="primary"
        aria-label="chat"
        onClick={toggleChat}
        sx={{ boxShadow: '0px 4px 12px rgba(0, 0, 0, 0.15)' }}
      >
        <ChatIcon />
      </Fab>
      
      {/* Chat window */}
      <Collapse
        in={open}
        sx={{
          position: 'absolute',
          bottom: 80,
          right: 0,
          transformOrigin: 'bottom right',
        }}
      >
        <ChatWindow>
          <ChatHeader>
            <Box display="flex" alignItems="center">
              <SmartToyIcon sx={{ mr: 1 }} />
              <Typography variant="subtitle1" fontWeight="bold">
                Overseer Assistant
              </Typography>
            </Box>
            <IconButton
              size="small"
              edge="end"
              color="inherit"
              onClick={toggleChat}
              aria-label="close"
            >
              <CloseIcon />
            </IconButton>
          </ChatHeader>
          
          <ChatBody>
            <List sx={{ width: '100%', p: 0 }}>
              {messages.map((message, index) => (
                <React.Fragment key={message.id}>
                  <ListItem
                    alignItems="flex-start"
                    sx={{
                      flexDirection: message.sender === 'user' ? 'row-reverse' : 'row',
                      px: 1,
                    }}
                  >
                    <ListItemAvatar sx={{ minWidth: 40 }}>
                      <Avatar
                        sx={{
                          width: 32,
                          height: 32,
                          bgcolor: message.sender === 'user' ? 'secondary.main' : 'primary.main',
                        }}
                      >
                        {message.sender === 'user' ? <PersonIcon /> : <SmartToyIcon />}
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={
                        <Paper
                          elevation={0}
                          sx={{
                            p: 1.5,
                            borderRadius: 2,
                            maxWidth: '85%',
                            display: 'inline-block',
                            bgcolor: message.sender === 'user' ? 'secondary.light' : 'primary.light',
                            color: message.sender === 'user' ? 'secondary.contrastText' : 'primary.contrastText',
                          }}
                        >
                          <Typography variant="body2">{message.text}</Typography>
                        </Paper>
                      }
                      secondary={
                        <Typography
                          variant="caption"
                          color="textSecondary"
                          sx={{
                            display: 'block',
                            mt: 0.5,
                            textAlign: message.sender === 'user' ? 'right' : 'left',
                          }}
                        >
                          {new Date(message.timestamp).toLocaleTimeString([], {
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </Typography>
                      }
                      sx={{
                        m: 0,
                        textAlign: message.sender === 'user' ? 'right' : 'left',
                      }}
                    />
                  </ListItem>
                  {index < messages.length - 1 && (
                    <Divider variant="inset" component="li" sx={{ my: 1 }} />
                  )}
                </React.Fragment>
              ))}
            </List>
          </ChatBody>
          
          <ChatFooter>
            <MessageForm onSubmit={handleSubmit}>
              <TextField
                fullWidth
                placeholder="Type your message..."
                variant="outlined"
                size="small"
                value={input}
                onChange={handleInputChange}
                sx={{ mr: 1 }}
              />
              <IconButton
                color="primary"
                type="submit"
                disabled={!input.trim()}
                aria-label="send message"
              >
                <SendIcon />
              </IconButton>
            </MessageForm>
          </ChatFooter>
        </ChatWindow>
      </Collapse>
    </>
  );
};

export default ConversationalAssistant;
