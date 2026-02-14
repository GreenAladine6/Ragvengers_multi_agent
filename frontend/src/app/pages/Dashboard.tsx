import React from 'react';
import {
  FolderKanban,
  Users,
  CheckCircle2,
  TrendingUp,
  Clock,
  CheckCircle,
  AlertCircle,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { projects, teams, tasks } from '../data/mockData';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Progress } from '../components/ui/progress';
import { Badge } from '../components/ui/badge';

export const Dashboard: React.FC = () => {
  const { currentUser } = useAuth();

  // Safety check
  if (!currentUser) {
    return null;
  }

  // Filter projects based on role
  const userProjects =
    currentUser.role === 'admin'
      ? projects
      : currentUser.role === 'employee'
      ? projects.filter((p) => p.assignedTo.includes(currentUser.id))
      : projects.filter((p) => p.assignedTo.includes(currentUser.id)); // Client sees purchased projects

  // Calculate statistics
  const totalProjects = userProjects.length;
  const completedTasks = currentUser.role === 'admin'
    ? tasks.filter((t) => t.status === 'completed').length
    : currentUser.role === 'employee'
    ? tasks.filter((t) => t.assignedTo === currentUser.id && t.status === 'completed').length
    : 0; // Clients don't see tasks
  const totalTasks = currentUser.role === 'admin'
    ? tasks.length
    : currentUser.role === 'employee'
    ? tasks.filter((t) => t.assignedTo === currentUser.id).length
    : 0;
  const inProgressProjects = userProjects.filter(
    (p) => p.status === 'in-progress'
  ).length;
  const completedProjects = userProjects.filter((p) => p.status === 'done').length;

  const avgProgress =
    userProjects.reduce((acc, p) => {
      const projectAvg =
        (p.progress.frontend +
          p.progress.backend +
          p.progress.database +
          p.progress.chatbot) /
        4;
      return acc + projectAvg;
    }, 0) / (userProjects.length || 1);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'done':
        return 'bg-green-100 text-green-700 border-green-200';
      case 'in-progress':
        return 'bg-blue-100 text-blue-700 border-blue-200';
      case 'pending':
        return 'bg-amber-100 text-amber-700 border-amber-200';
      default:
        return 'bg-slate-100 text-slate-700 border-slate-200';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'done':
        return <CheckCircle className="h-4 w-4" />;
      case 'in-progress':
        return <Clock className="h-4 w-4" />;
      case 'pending':
        return <AlertCircle className="h-4 w-4" />;
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-slate-800">Dashboard Overview</h2>
        <p className="text-slate-600 mt-1">
          Track your projects and team performance
        </p>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="border-slate-200 shadow-sm hover:shadow-md transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-slate-600">
              Total Projects
            </CardTitle>
            <div className="h-10 w-10 rounded-lg bg-blue-100 flex items-center justify-center">
              <FolderKanban className="h-5 w-5 text-blue-600" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-slate-800">{totalProjects}</div>
            <p className="text-xs text-slate-500 mt-1">
              {inProgressProjects} in progress
            </p>
          </CardContent>
        </Card>

        <Card className="border-slate-200 shadow-sm hover:shadow-md transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-slate-600">
              Team Members
            </CardTitle>
            <div className="h-10 w-10 rounded-lg bg-purple-100 flex items-center justify-center">
              <Users className="h-5 w-5 text-purple-600" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-slate-800">
              {currentUser.role === 'admin' ? teams.reduce((acc, t) => acc + t.members.length, 0) : '-'}
            </div>
            <p className="text-xs text-slate-500 mt-1">
              {currentUser.role === 'admin' ? `${teams.length} teams` : 'View in Teams page'}
            </p>
          </CardContent>
        </Card>

        <Card className="border-slate-200 shadow-sm hover:shadow-md transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-slate-600">
              Completed Tasks
            </CardTitle>
            <div className="h-10 w-10 rounded-lg bg-green-100 flex items-center justify-center">
              <CheckCircle2 className="h-5 w-5 text-green-600" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-slate-800">
              {completedTasks}/{totalTasks}
            </div>
            <p className="text-xs text-slate-500 mt-1">
              {Math.round((completedTasks / totalTasks) * 100)}% completion rate
            </p>
          </CardContent>
        </Card>

        <Card className="border-slate-200 shadow-sm hover:shadow-md transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-slate-600">
              Progress Rate
            </CardTitle>
            <div className="h-10 w-10 rounded-lg bg-indigo-100 flex items-center justify-center">
              <TrendingUp className="h-5 w-5 text-indigo-600" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-slate-800">
              {Math.round(avgProgress)}%
            </div>
            <p className="text-xs text-slate-500 mt-1">Average across all projects</p>
          </CardContent>
        </Card>
      </div>

      {/* Active Projects */}
      <Card className="border-slate-200 shadow-sm">
        <CardHeader>
          <CardTitle className="text-slate-800">Active Projects</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {userProjects.slice(0, 5).map((project) => {
              const avgProjectProgress =
                (project.progress.frontend +
                  project.progress.backend +
                  project.progress.database +
                  project.progress.chatbot) /
                4;

              return (
                <div
                  key={project.id}
                  className="p-4 rounded-lg border border-slate-200 hover:border-blue-300 transition-colors bg-white"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-semibold text-slate-800">
                          {project.name}
                        </h4>
                        <Badge
                          variant="outline"
                          className={getStatusColor(project.status)}
                        >
                          {getStatusIcon(project.status)}
                          <span className="ml-1 capitalize">
                            {project.status.replace('-', ' ')}
                          </span>
                        </Badge>
                      </div>
                      <p className="text-sm text-slate-600">{project.description}</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 mt-4">
                    <div>
                      <div className="flex items-center justify-between text-xs mb-1">
                        <span className="text-slate-600">Frontend</span>
                        <span className="font-medium text-slate-700">
                          {project.progress.frontend}%
                        </span>
                      </div>
                      <Progress
                        value={project.progress.frontend}
                        className="h-2 bg-slate-100"
                      />
                    </div>
                    <div>
                      <div className="flex items-center justify-between text-xs mb-1">
                        <span className="text-slate-600">Backend</span>
                        <span className="font-medium text-slate-700">
                          {project.progress.backend}%
                        </span>
                      </div>
                      <Progress
                        value={project.progress.backend}
                        className="h-2 bg-slate-100"
                      />
                    </div>
                    <div>
                      <div className="flex items-center justify-between text-xs mb-1">
                        <span className="text-slate-600">Database</span>
                        <span className="font-medium text-slate-700">
                          {project.progress.database}%
                        </span>
                      </div>
                      <Progress
                        value={project.progress.database}
                        className="h-2 bg-slate-100"
                      />
                    </div>
                    <div>
                      <div className="flex items-center justify-between text-xs mb-1">
                        <span className="text-slate-600">Chatbot</span>
                        <span className="font-medium text-slate-700">
                          {project.progress.chatbot}%
                        </span>
                      </div>
                      <Progress
                        value={project.progress.chatbot}
                        className="h-2 bg-slate-100"
                      />
                    </div>
                  </div>

                  <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                    <span>Due: {new Date(project.dueDate).toLocaleDateString()}</span>
                    <span className="font-medium text-slate-700">
                      Overall: {Math.round(avgProjectProgress)}%
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};