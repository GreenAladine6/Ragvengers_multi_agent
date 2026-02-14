import React, { useState } from 'react';
import { Plus, Search, Filter, Calendar, Users as UsersIcon } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { projects } from '../data/mockData';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '../components/ui/dialog';
import { Label } from '../components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';

export const Projects: React.FC = () => {
  const { currentUser } = useAuth();
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);

  // Safety check
  if (!currentUser) {
    return null;
  }

  // Filter projects based on role
  const userProjects =
    currentUser.role === 'admin'
      ? projects // Admin sees all projects
      : currentUser.role === 'employee'
      ? projects.filter((p) => p.assignedTo.includes(currentUser.id)) // Employee sees only collaboration projects
      : projects.filter((p) => p.assignedTo.includes(currentUser.id)); // Client sees purchased projects

  // Apply search and filter
  const filteredProjects = userProjects.filter((project) => {
    const matchesSearch =
      project.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      project.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter =
      filterStatus === 'all' || project.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-slate-800">Projects</h2>
          <p className="text-slate-600 mt-1">
            Manage and track all your projects
          </p>
        </div>
        {currentUser.role === 'admin' && (
          <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
            <DialogTrigger asChild>
              <Button className="bg-blue-600 hover:bg-blue-700">
                <Plus className="h-4 w-4 mr-2" />
                Add Project
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[500px]">
              <DialogHeader>
                <DialogTitle>Create New Project</DialogTitle>
                <DialogDescription>
                  Add a new project to the system. Fill in the details below.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Project Name</Label>
                  <Input id="name" placeholder="Enter project name" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="description">Description</Label>
                  <Input
                    id="description"
                    placeholder="Brief project description"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="status">Status</Label>
                  <Select defaultValue="pending">
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="pending">Pending</SelectItem>
                      <SelectItem value="in-progress">In Progress</SelectItem>
                      <SelectItem value="done">Done</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="startDate">Start Date</Label>
                    <Input id="startDate" type="date" />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="dueDate">Due Date</Label>
                    <Input id="dueDate" type="date" />
                  </div>
                </div>
              </div>
              <DialogFooter>
                <Button
                  variant="outline"
                  onClick={() => setIsAddDialogOpen(false)}
                >
                  Cancel
                </Button>
                <Button
                  className="bg-blue-600 hover:bg-blue-700"
                  onClick={() => setIsAddDialogOpen(false)}
                >
                  Create Project
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        )}
      </div>

      {/* Search and Filter */}
      <Card className="border-slate-200 shadow-sm">
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
              <Input
                placeholder="Search projects..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select value={filterStatus} onValueChange={setFilterStatus}>
              <SelectTrigger className="w-full md:w-48">
                <Filter className="h-4 w-4 mr-2" />
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Projects</SelectItem>
                <SelectItem value="in-progress">In Progress</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="done">Done</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Projects Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredProjects.map((project) => {
          const avgProgress =
            (project.progress.frontend +
              project.progress.backend +
              project.progress.database +
              project.progress.chatbot) /
            4;

          return (
            <Card
              key={project.id}
              className="border-slate-200 shadow-sm hover:shadow-md transition-all hover:border-blue-300"
            >
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg text-slate-800 mb-2">
                      {project.name}
                    </CardTitle>
                    <Badge
                      variant="outline"
                      className={getStatusColor(project.status)}
                    >
                      {project.status.replace('-', ' ').toUpperCase()}
                    </Badge>
                  </div>
                  {currentUser.role === 'admin' && (
                    <Button variant="ghost" size="sm">
                      Edit
                    </Button>
                  )}
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm text-slate-600">{project.description}</p>

                {/* Progress Sections */}
                <div className="space-y-3 pt-2">
                  <div>
                    <div className="flex items-center justify-between text-xs mb-1.5">
                      <span className="text-slate-600 font-medium">Frontend</span>
                      <span className="text-slate-700 font-semibold">
                        {project.progress.frontend}%
                      </span>
                    </div>
                    <Progress
                      value={project.progress.frontend}
                      className="h-2 bg-slate-100"
                    />
                  </div>
                  <div>
                    <div className="flex items-center justify-between text-xs mb-1.5">
                      <span className="text-slate-600 font-medium">Backend</span>
                      <span className="text-slate-700 font-semibold">
                        {project.progress.backend}%
                      </span>
                    </div>
                    <Progress
                      value={project.progress.backend}
                      className="h-2 bg-slate-100"
                    />
                  </div>
                  <div>
                    <div className="flex items-center justify-between text-xs mb-1.5">
                      <span className="text-slate-600 font-medium">Database</span>
                      <span className="text-slate-700 font-semibold">
                        {project.progress.database}%
                      </span>
                    </div>
                    <Progress
                      value={project.progress.database}
                      className="h-2 bg-slate-100"
                    />
                  </div>
                  <div>
                    <div className="flex items-center justify-between text-xs mb-1.5">
                      <span className="text-slate-600 font-medium">Chatbot</span>
                      <span className="text-slate-700 font-semibold">
                        {project.progress.chatbot}%
                      </span>
                    </div>
                    <Progress
                      value={project.progress.chatbot}
                      className="h-2 bg-slate-100"
                    />
                  </div>
                </div>

                {/* Overall Progress */}
                <div className="pt-3 border-t border-slate-100">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-slate-700">
                      Overall Progress
                    </span>
                    <span className="text-sm font-bold text-blue-600">
                      {Math.round(avgProgress)}%
                    </span>
                  </div>
                  <Progress
                    value={avgProgress}
                    className="h-2.5 bg-slate-100"
                  />
                </div>

                {/* Footer Info */}
                <div className="flex items-center justify-between pt-3 border-t border-slate-100 text-xs text-slate-500">
                  <div className="flex items-center gap-1">
                    <Calendar className="h-3.5 w-3.5" />
                    <span>Due: {new Date(project.dueDate).toLocaleDateString()}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <UsersIcon className="h-3.5 w-3.5" />
                    <span>{project.assignedTo.length} members</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {filteredProjects.length === 0 && (
        <Card className="border-slate-200 shadow-sm">
          <CardContent className="py-12 text-center">
            <p className="text-slate-500">No projects found matching your criteria.</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};