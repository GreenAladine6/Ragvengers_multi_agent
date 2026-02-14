import React, { useState } from 'react';
import {
  CheckCircle2,
  Circle,
  Clock,
  AlertCircle,
  FolderKanban,
  Database,
  Code,
  Server,
  MessageSquare,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { projects, tasks } from '../data/mockData';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Progress } from '../components/ui/progress';

export const Worker: React.FC = () => {
  const { currentUser } = useAuth();
  const [selectedProject, setSelectedProject] = useState<string | null>(null);

  // Safety check
  if (!currentUser) {
    return null;
  }

  // Get user's assigned projects based on role
  const userProjects =
    currentUser.role === 'admin'
      ? projects // Admin sees all projects
      : projects.filter((p) => p.assignedTo.includes(currentUser.id)); // Employee sees only collaboration projects

  // Get tasks for selected project or user
  const projectTasks = selectedProject
    ? currentUser.role === 'admin'
      ? tasks.filter((t) => t.projectId === selectedProject) // Admin sees all tasks for project
      : tasks.filter(
          (t) => t.projectId === selectedProject && t.assignedTo === currentUser.id
        ) // Employee sees only their tasks for project
    : currentUser.role === 'admin'
    ? tasks.filter((t) => userProjects.some((p) => p.id === t.projectId)) // Admin sees all tasks
    : tasks.filter(
        (t) =>
          userProjects.some((p) => p.id === t.projectId) &&
          t.assignedTo === currentUser.id
      ); // Employee sees only their tasks

  const selectedProjectData = selectedProject
    ? projects.find((p) => p.id === selectedProject)
    : null;

  const getTaskIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="h-5 w-5 text-green-600" />;
      case 'in-progress':
        return <Clock className="h-5 w-5 text-blue-600" />;
      default:
        return <Circle className="h-5 w-5 text-slate-400" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-700 border-red-200';
      case 'medium':
        return 'bg-amber-100 text-amber-700 border-amber-200';
      default:
        return 'bg-slate-100 text-slate-700 border-slate-200';
    }
  };

  const getTaskStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-50 text-green-700 border-green-200';
      case 'in-progress':
        return 'bg-blue-50 text-blue-700 border-blue-200';
      default:
        return 'bg-slate-50 text-slate-700 border-slate-200';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-semibold text-slate-800">Worker Interface</h2>
        <p className="text-slate-600 mt-1">
          Manage your tasks and view project structure
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Projects List */}
        <Card className="border-slate-200 shadow-sm lg:col-span-1">
          <CardHeader>
            <CardTitle className="text-slate-800">My Projects</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {userProjects.map((project) => (
                <div
                  key={project.id}
                  onClick={() => setSelectedProject(project.id)}
                  className={`p-3 rounded-lg border cursor-pointer transition-all ${
                    selectedProject === project.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-slate-200 hover:border-blue-300 hover:bg-slate-50'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <FolderKanban className="h-4 w-4 text-blue-600" />
                    <span className="font-medium text-sm text-slate-800">
                      {project.name}
                    </span>
                  </div>
                  <p className="text-xs text-slate-600 mb-2">
                    {project.description.substring(0, 60)}...
                  </p>
                  <Badge
                    variant="outline"
                    className={
                      project.status === 'done'
                        ? 'bg-green-100 text-green-700 border-green-200'
                        : project.status === 'in-progress'
                        ? 'bg-blue-100 text-blue-700 border-blue-200'
                        : 'bg-amber-100 text-amber-700 border-amber-200'
                    }
                  >
                    {project.status}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {selectedProjectData ? (
            <>
              {/* Project Structure */}
              <Card className="border-slate-200 shadow-sm">
                <CardHeader>
                  <CardTitle className="text-slate-800">
                    Project Structure: {selectedProjectData.name}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 rounded-lg border border-slate-200 bg-gradient-to-br from-blue-50 to-blue-100">
                      <div className="flex items-center gap-3 mb-3">
                        <div className="h-10 w-10 rounded-lg bg-blue-600 flex items-center justify-center">
                          <Code className="h-5 w-5 text-white" />
                        </div>
                        <div>
                          <h4 className="font-medium text-slate-800">Frontend</h4>
                          <p className="text-xs text-slate-600">React/TypeScript</p>
                        </div>
                      </div>
                      <div className="space-y-1">
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-slate-700">Progress</span>
                          <span className="font-semibold text-blue-700">
                            {selectedProjectData.progress.frontend}%
                          </span>
                        </div>
                        <Progress
                          value={selectedProjectData.progress.frontend}
                          className="h-2"
                        />
                      </div>
                    </div>

                    <div className="p-4 rounded-lg border border-slate-200 bg-gradient-to-br from-purple-50 to-purple-100">
                      <div className="flex items-center gap-3 mb-3">
                        <div className="h-10 w-10 rounded-lg bg-purple-600 flex items-center justify-center">
                          <Server className="h-5 w-5 text-white" />
                        </div>
                        <div>
                          <h4 className="font-medium text-slate-800">Backend</h4>
                          <p className="text-xs text-slate-600">Node.js/Express</p>
                        </div>
                      </div>
                      <div className="space-y-1">
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-slate-700">Progress</span>
                          <span className="font-semibold text-purple-700">
                            {selectedProjectData.progress.backend}%
                          </span>
                        </div>
                        <Progress
                          value={selectedProjectData.progress.backend}
                          className="h-2"
                        />
                      </div>
                    </div>

                    <div className="p-4 rounded-lg border border-slate-200 bg-gradient-to-br from-green-50 to-green-100">
                      <div className="flex items-center gap-3 mb-3">
                        <div className="h-10 w-10 rounded-lg bg-green-600 flex items-center justify-center">
                          <Database className="h-5 w-5 text-white" />
                        </div>
                        <div>
                          <h4 className="font-medium text-slate-800">Database</h4>
                          <p className="text-xs text-slate-600">PostgreSQL</p>
                        </div>
                      </div>
                      <div className="space-y-1">
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-slate-700">Progress</span>
                          <span className="font-semibold text-green-700">
                            {selectedProjectData.progress.database}%
                          </span>
                        </div>
                        <Progress
                          value={selectedProjectData.progress.database}
                          className="h-2"
                        />
                      </div>
                    </div>

                    <div className="p-4 rounded-lg border border-slate-200 bg-gradient-to-br from-indigo-50 to-indigo-100">
                      <div className="flex items-center gap-3 mb-3">
                        <div className="h-10 w-10 rounded-lg bg-indigo-600 flex items-center justify-center">
                          <MessageSquare className="h-5 w-5 text-white" />
                        </div>
                        <div>
                          <h4 className="font-medium text-slate-800">Chatbot</h4>
                          <p className="text-xs text-slate-600">AI Assistant</p>
                        </div>
                      </div>
                      <div className="space-y-1">
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-slate-700">Progress</span>
                          <span className="font-semibold text-indigo-700">
                            {selectedProjectData.progress.chatbot}%
                          </span>
                        </div>
                        <Progress
                          value={selectedProjectData.progress.chatbot}
                          className="h-2"
                        />
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Tasks for Selected Project */}
              <Card className="border-slate-200 shadow-sm">
                <CardHeader>
                  <CardTitle className="text-slate-800">Tasks</CardTitle>
                </CardHeader>
                <CardContent>
                  <Tabs defaultValue="all">
                    <TabsList className="grid w-full grid-cols-4 mb-4">
                      <TabsTrigger value="all">All</TabsTrigger>
                      <TabsTrigger value="todo">To Do</TabsTrigger>
                      <TabsTrigger value="in-progress">In Progress</TabsTrigger>
                      <TabsTrigger value="completed">Completed</TabsTrigger>
                    </TabsList>

                    <TabsContent value="all" className="space-y-3">
                      {projectTasks.map((task) => (
                        <div
                          key={task.id}
                          className="p-4 rounded-lg border border-slate-200 hover:border-blue-300 transition-colors bg-white"
                        >
                          <div className="flex items-start gap-3">
                            {getTaskIcon(task.status)}
                            <div className="flex-1">
                              <div className="flex items-start justify-between mb-2">
                                <h4 className="font-medium text-slate-800">
                                  {task.title}
                                </h4>
                                <div className="flex gap-2">
                                  <Badge
                                    variant="outline"
                                    className={getPriorityColor(task.priority)}
                                  >
                                    {task.priority}
                                  </Badge>
                                  <Badge
                                    variant="outline"
                                    className={getTaskStatusColor(task.status)}
                                  >
                                    {task.status}
                                  </Badge>
                                </div>
                              </div>
                              <p className="text-sm text-slate-600 mb-2">
                                {task.description}
                              </p>
                              <div className="flex items-center gap-4 text-xs text-slate-500">
                                <span>Due: {new Date(task.dueDate).toLocaleDateString()}</span>
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </TabsContent>

                    <TabsContent value="todo" className="space-y-3">
                      {projectTasks
                        .filter((t) => t.status === 'todo')
                        .map((task) => (
                          <div
                            key={task.id}
                            className="p-4 rounded-lg border border-slate-200 hover:border-blue-300 transition-colors bg-white"
                          >
                            <div className="flex items-start gap-3">
                              {getTaskIcon(task.status)}
                              <div className="flex-1">
                                <div className="flex items-start justify-between mb-2">
                                  <h4 className="font-medium text-slate-800">
                                    {task.title}
                                  </h4>
                                  <Badge
                                    variant="outline"
                                    className={getPriorityColor(task.priority)}
                                  >
                                    {task.priority}
                                  </Badge>
                                </div>
                                <p className="text-sm text-slate-600 mb-2">
                                  {task.description}
                                </p>
                                <div className="flex items-center gap-4 text-xs text-slate-500">
                                  <span>Due: {new Date(task.dueDate).toLocaleDateString()}</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        ))}
                    </TabsContent>

                    <TabsContent value="in-progress" className="space-y-3">
                      {projectTasks
                        .filter((t) => t.status === 'in-progress')
                        .map((task) => (
                          <div
                            key={task.id}
                            className="p-4 rounded-lg border border-slate-200 hover:border-blue-300 transition-colors bg-white"
                          >
                            <div className="flex items-start gap-3">
                              {getTaskIcon(task.status)}
                              <div className="flex-1">
                                <div className="flex items-start justify-between mb-2">
                                  <h4 className="font-medium text-slate-800">
                                    {task.title}
                                  </h4>
                                  <Badge
                                    variant="outline"
                                    className={getPriorityColor(task.priority)}
                                  >
                                    {task.priority}
                                  </Badge>
                                </div>
                                <p className="text-sm text-slate-600 mb-2">
                                  {task.description}
                                </p>
                                <div className="flex items-center gap-4 text-xs text-slate-500">
                                  <span>Due: {new Date(task.dueDate).toLocaleDateString()}</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        ))}
                    </TabsContent>

                    <TabsContent value="completed" className="space-y-3">
                      {projectTasks
                        .filter((t) => t.status === 'completed')
                        .map((task) => (
                          <div
                            key={task.id}
                            className="p-4 rounded-lg border border-slate-200 hover:border-blue-300 transition-colors bg-white"
                          >
                            <div className="flex items-start gap-3">
                              {getTaskIcon(task.status)}
                              <div className="flex-1">
                                <div className="flex items-start justify-between mb-2">
                                  <h4 className="font-medium text-slate-800 line-through">
                                    {task.title}
                                  </h4>
                                  <Badge
                                    variant="outline"
                                    className={getPriorityColor(task.priority)}
                                  >
                                    {task.priority}
                                  </Badge>
                                </div>
                                <p className="text-sm text-slate-600 mb-2">
                                  {task.description}
                                </p>
                                <div className="flex items-center gap-4 text-xs text-slate-500">
                                  <span>Due: {new Date(task.dueDate).toLocaleDateString()}</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        ))}
                    </TabsContent>
                  </Tabs>
                </CardContent>
              </Card>
            </>
          ) : (
            <Card className="border-slate-200 shadow-sm">
              <CardContent className="py-12 text-center">
                <AlertCircle className="h-12 w-12 text-slate-300 mx-auto mb-3" />
                <p className="text-slate-500">
                  Select a project to view its structure and tasks
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};