export type UserRole = 'admin' | 'employee' | 'client';

export type ProjectStatus = 'in-progress' | 'done' | 'pending';

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  avatar?: string;
}

export interface Project {
  id: string;
  name: string;
  description: string;
  status: ProjectStatus;
  progress: {
    frontend: number;
    backend: number;
    database: number;
    chatbot: number;
  };
  teamId: string;
  assignedTo: string[];
  startDate: string;
  dueDate: string;
}

export interface Team {
  id: string;
  name: string;
  members: User[];
  projectIds: string[];
}

export interface Task {
  id: string;
  title: string;
  description: string;
  projectId: string;
  assignedTo: string;
  status: 'todo' | 'in-progress' | 'completed';
  priority: 'low' | 'medium' | 'high';
  dueDate: string;
}

export interface ChatMessage {
  id: string;
  projectId: string;
  userId: string;
  message: string;
  timestamp: string;
  isBot: boolean;
}

export interface Feedback {
  id: string;
  projectId: string;
  userId: string;
  message: string;
  timestamp: string;
  rating?: number;
}
