import React, { createContext, useContext, useState, ReactNode } from 'react';
import { User } from '../types';

interface AuthContextType {
  currentUser: User | null;
  login: (role: 'admin' | 'employee' | 'client', name: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<User | null>(null);

  const login = (role: 'admin' | 'employee' | 'client', name: string) => {
    const newUser: User = {
      id: `user-${Date.now()}`,
      name: name,
      role: role,
      email: `${name.toLowerCase().replace(/\s+/g, '.')}@example.com`,
      avatar: '',
    };
    setCurrentUser(newUser);
  };

  const logout = () => {
    setCurrentUser(null);
  };

  return (
    <AuthContext.Provider value={{ currentUser, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};