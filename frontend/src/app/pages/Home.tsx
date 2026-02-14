import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router';
import { Send, Bot, User, LogIn, UserPlus, Sparkles } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';

interface Message {
  id: string;
  content: string;
  isBot: boolean;
  timestamp: Date;
}

export const Home: React.FC = () => {
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content:
        'Hello! 👋 I\'m your AI project assistant. I can help answer questions about our project management system. How can I assist you today?',
      isBot: true,
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = () => {
    if (!inputValue.trim()) return;

    // Check if user is logged in
    if (!currentUser) {
      const userMessage: Message = {
        id: Date.now().toString(),
        content: inputValue,
        isBot: false,
        timestamp: new Date(),
      };

      const botResponse: Message = {
        id: (Date.now() + 1).toString(),
        content:
          '🔒 I\'d love to help you, but you need to be logged in to use the chatbot. Please login or create an account to continue our conversation!',
        isBot: true,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMessage, botResponse]);
      setInputValue('');
      return;
    }

    // If logged in, redirect to dashboard chatbot
    navigate('/chatbot');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center">
              <Sparkles className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-800">ProjectFlow AI</h1>
              <p className="text-xs text-slate-500">Multi-Agent Project Management</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              onClick={() => navigate('/login')}
              className="border-slate-200"
            >
              <LogIn className="h-4 w-4 mr-2" />
              Login
            </Button>
            <Button
              onClick={() => navigate('/login?register=true')}
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
            >
              <UserPlus className="h-4 w-4 mr-2" />
              Sign Up
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-6 py-16 text-center">
        <div className="inline-block mb-4 px-4 py-2 bg-blue-100 text-blue-700 rounded-full text-sm font-semibold">
          ✨ AI-Powered Project Management
        </div>
        <h2 className="text-5xl font-bold text-slate-900 mb-6">
          Manage Projects with
          <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            {' '}
            Intelligence
          </span>
        </h2>
        <p className="text-xl text-slate-600 mb-12 max-w-2xl mx-auto">
          Connect your code, collaborate with teams, and deliver projects faster with our
          multi-agent AI system.
        </p>

        {/* Feature Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
          <Card className="border-slate-200 shadow-md hover:shadow-lg transition-shadow">
            <CardContent className="pt-8 text-center">
              <div className="h-12 w-12 rounded-lg bg-blue-100 flex items-center justify-center mx-auto mb-4">
                <Bot className="h-6 w-6 text-blue-600" />
              </div>
              <h3 className="font-semibold text-slate-800 mb-2">AI Assistant</h3>
              <p className="text-sm text-slate-600">
                24/7 intelligent chatbot to answer project questions
              </p>
            </CardContent>
          </Card>
          <Card className="border-slate-200 shadow-md hover:shadow-lg transition-shadow">
            <CardContent className="pt-8 text-center">
              <div className="h-12 w-12 rounded-lg bg-purple-100 flex items-center justify-center mx-auto mb-4">
                <User className="h-6 w-6 text-purple-600" />
              </div>
              <h3 className="font-semibold text-slate-800 mb-2">Role-Based Access</h3>
              <p className="text-sm text-slate-600">
                Admin, Employee, and Client interfaces
              </p>
            </CardContent>
          </Card>
          <Card className="border-slate-200 shadow-md hover:shadow-lg transition-shadow">
            <CardContent className="pt-8 text-center">
              <div className="h-12 w-12 rounded-lg bg-pink-100 flex items-center justify-center mx-auto mb-4">
                <Sparkles className="h-6 w-6 text-pink-600" />
              </div>
              <h3 className="font-semibold text-slate-800 mb-2">Real-time Tracking</h3>
              <p className="text-sm text-slate-600">
                Monitor progress across frontend, backend & database
              </p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Chatbot Section */}
      <section className="max-w-4xl mx-auto px-6 pb-16">
        <h3 className="text-3xl font-bold text-slate-900 text-center mb-8">
          Try Our AI Assistant
        </h3>
        <Card className="border-slate-200 shadow-xl">
          <CardHeader className="border-b border-slate-200 bg-gradient-to-r from-blue-50 to-purple-50">
            <CardTitle className="flex items-center gap-2 text-slate-800">
              <Bot className="h-5 w-5 text-blue-600" />
              AI Project Assistant
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {/* Messages */}
            <div className="h-96 overflow-y-auto p-6 space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex gap-3 ${message.isBot ? '' : 'flex-row-reverse'}`}
                >
                  <div
                    className={`h-8 w-8 rounded-full flex items-center justify-center shrink-0 ${
                      message.isBot
                        ? 'bg-gradient-to-br from-blue-500 to-purple-500'
                        : 'bg-slate-200'
                    }`}
                  >
                    {message.isBot ? (
                      <Bot className="h-5 w-5 text-white" />
                    ) : (
                      <User className="h-5 w-5 text-slate-600" />
                    )}
                  </div>
                  <div
                    className={`rounded-2xl px-4 py-3 max-w-[80%] ${
                      message.isBot
                        ? 'bg-slate-100 text-slate-800'
                        : 'bg-gradient-to-r from-blue-600 to-purple-600 text-white'
                    }`}
                  >
                    <p className="text-sm leading-relaxed">{message.content}</p>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="border-t border-slate-200 p-4 bg-slate-50">
              <div className="flex gap-2">
                <Input
                  placeholder="Ask me anything about our project management system..."
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  className="flex-1 border-slate-200 focus:border-blue-500"
                />
                <Button
                  onClick={handleSendMessage}
                  disabled={!inputValue.trim()}
                  className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </section>

      {/* Footer */}
      <footer className="border-t bg-white/80 backdrop-blur-sm py-8 mt-16">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <p className="text-slate-600">
            © 2026 ProjectFlow AI. Powered by Multi-Agent Intelligence.
          </p>
        </div>
      </footer>
    </div>
  );
};
