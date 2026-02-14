import React, { useState } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router';
import {
  LayoutDashboard,
  FolderKanban,
  Users,
  MessageSquare,
  Settings,
  Menu,
  X,
  ChevronDown,
  MessageCircle,
  LogOut,
  Sparkles,
  Bell,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from './ui/dropdown-menu';
import { Avatar, AvatarFallback } from './ui/avatar';

export const Layout: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { currentUser, logout } = useAuth();
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  // Safety check - should not happen due to ProtectedRoute
  if (!currentUser) {
    navigate('/login');
    return null;
  }

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const getInitials = (name?: string) => {
    try {
      if (name && name.trim() !== '') {
        return name
          .split(' ')
          .map((n) => n[0])
          .join('')
          .toUpperCase();
      }
      // Fallback to email initials if name is not provided
      const email = String(currentUser?.email || '').trim();
      if (!email) return 'U'; // Final fallback if email is also missing
      const emailName = email.split('@')[0];
      return (emailName || 'U').substring(0, 2).toUpperCase();
    } catch (e) {
      return 'U'; // Ultimate fallback on any error
    }
  };

  const navigationItems = [
    {
      name: 'Dashboard',
      path: '/dashboard',
      icon: LayoutDashboard,
      roles: ['admin', 'employee', 'client'],
    },
    {
      name: 'My Projects',
      path: '/projects',
      icon: FolderKanban,
      roles: ['client'],
    },
    {
      name: 'Projects',
      path: '/projects',
      icon: FolderKanban,
      roles: ['admin', 'employee'],
    },
    {
      name: 'Teams',
      path: '/teams',
      icon: Users,
      roles: ['admin', 'employee'],
    },
    {
      name: 'My Tasks',
      path: '/worker',
      icon: MessageSquare,
      roles: ['employee'],
    },
    {
      name: 'All Tasks',
      path: '/worker',
      icon: MessageSquare,
      roles: ['admin'],
    },
    {
      name: 'Chatbot',
      path: '/chatbot',
      icon: MessageCircle,
      roles: ['client'],
    },
    {
      name: 'Feedback',
      path: '/feedback',
      icon: MessageCircle,
      roles: ['admin', 'employee', 'client'],
    },
    {
      name: 'Settings',
      path: '/settings',
      icon: Settings,
      roles: ['admin', 'employee', 'client'],
    },
  ];

  const filteredNavItems = navigationItems.filter((item) =>
    item.roles.includes((currentUser.role as any) || 'client')
  );

  return (
    <div className="flex h-screen bg-slate-50">
      {/* Sidebar */}
      <aside
        className={`${
          isSidebarOpen ? 'w-64' : 'w-20'
        } bg-white border-r border-slate-200 transition-all duration-300 flex flex-col`}
      >
        {/* Logo */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-slate-200">
          {isSidebarOpen && (
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">PM</span>
              </div>
              <span className="font-semibold text-slate-800">ProjectSync</span>
            </div>
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="h-8 w-8 p-0"
          >
            {isSidebarOpen ? (
              <X className="h-4 w-4" />
            ) : (
              <Menu className="h-4 w-4" />
            )}
          </Button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          {filteredNavItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;

            return (
              <Link key={item.path} to={item.path}>
                <div
                  className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-blue-50 text-blue-600'
                      : 'text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  <Icon className="h-5 w-5 flex-shrink-0" />
                  {isSidebarOpen && <span>{item.name}</span>}
                </div>
              </Link>
            );
          })}
        </nav>

        {/* User Role Badge */}
        {isSidebarOpen && (
          <div className="p-4 border-t border-slate-200">
            <Badge
              variant={
                currentUser.role === 'admin'
                  ? 'default'
                  : currentUser.role === 'employee'
                  ? 'secondary'
                  : 'outline'
              }
              className="w-full justify-center"
            >
              {(currentUser.role || 'client').toUpperCase()}
            </Badge>
          </div>
        )}
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar */}
        <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6">
          <div>
            <h1 className="text-slate-800 font-semibold">
              Welcome back, {currentUser.name.split(' ')[0]}
            </h1>
            <p className="text-sm text-slate-500">
              {new Date().toLocaleDateString('en-US', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })}
            </p>
          </div>

          <div className="flex items-center gap-4">
            {/* Notifications */}
            <Button variant="ghost" size="icon" className="relative">
              <Bell className="h-5 w-5" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
            </Button>

            {/* User Menu */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="flex items-center gap-2 h-auto py-2">
                  <Avatar className="h-8 w-8">
                    <AvatarFallback className="bg-gradient-to-br from-blue-500 to-purple-600 text-white text-sm">
                      {getInitials(currentUser.name)}
                    </AvatarFallback>
                  </Avatar>
                  <div className="text-left">
                    <p className="text-sm font-medium">{currentUser.name || 'User'}</p>
                    <p className="text-xs text-slate-500">{currentUser.email || 'No email'}</p>
                  </div>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuLabel>My Account</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem>
                  <LogOut className="mr-2 h-4 w-4" />
                  <span onClick={handleLogout}>Log out</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
};