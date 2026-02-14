import React from 'react';
import { createBrowserRouter } from 'react-router';
import { Layout } from './components/Layout';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Home } from './pages/Home';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { Projects } from './pages/Projects';
import { Teams } from './pages/Teams';
import { Worker } from './pages/Worker';
import { Chatbot } from './pages/Chatbot';
import { Feedback } from './pages/Feedback';
import { Settings } from './pages/Settings';
import { NotFound } from './pages/NotFound';

const ProtectedLayout = () => (
  <ProtectedRoute>
    <Layout />
  </ProtectedRoute>
);

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Home />,
  },
  {
    path: '/login',
    element: <Login />,
  },
  {
    path: '/dashboard',
    element: <ProtectedLayout />,
    children: [
      { index: true, Component: Dashboard },
      { path: 'projects', Component: Projects },
      { path: 'teams', Component: Teams },
      { path: 'worker', Component: Worker },
      { path: 'chatbot', Component: Chatbot },
      { path: 'feedback', Component: Feedback },
      { path: 'settings', Component: Settings },
    ],
  },
  {
    path: '/projects',
    element: <ProtectedLayout />,
    children: [{ index: true, Component: Projects }],
  },
  {
    path: '/teams',
    element: <ProtectedLayout />,
    children: [{ index: true, Component: Teams }],
  },
  {
    path: '/worker',
    element: <ProtectedLayout />,
    children: [{ index: true, Component: Worker }],
  },
  {
    path: '/chatbot',
    element: <ProtectedLayout />,
    children: [{ index: true, Component: Chatbot }],
  },
  {
    path: '/feedback',
    element: <ProtectedLayout />,
    children: [{ index: true, Component: Feedback }],
  },
  {
    path: '/settings',
    element: <ProtectedLayout />,
    children: [{ index: true, Component: Settings }],
  },
  {
    path: '*',
    Component: NotFound,
  },
]);
