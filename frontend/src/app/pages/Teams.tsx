import React from 'react';
import { Users as UsersIcon, Mail, FolderKanban } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { teams, projects } from '../data/mockData';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Avatar, AvatarFallback } from '../components/ui/avatar';
import { Badge } from '../components/ui/badge';

export const Teams: React.FC = () => {
  const { currentUser } = useAuth();

  // Safety check
  if (!currentUser) {
    return null;
  }

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase();
  };

  // Filter teams based on role
  const userTeams =
    currentUser.role === 'admin'
      ? teams // Admin sees all teams
      : teams.filter((t) => t.members.some((m) => m.id === currentUser.id)); // Employee sees only their team

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-semibold text-slate-800">Teams</h2>
        <p className="text-slate-600 mt-1">
          View all teams and their members
        </p>
      </div>

      {/* Teams Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {userTeams.map((team) => {
          const teamProjects = projects.filter((p) =>
            team.projectIds.includes(p.id)
          );

          return (
            <Card
              key={team.id}
              className="border-slate-200 shadow-sm hover:shadow-md transition-shadow"
            >
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="h-12 w-12 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                      <UsersIcon className="h-6 w-6 text-white" />
                    </div>
                    <div>
                      <CardTitle className="text-lg text-slate-800">
                        {team.name}
                      </CardTitle>
                      <p className="text-sm text-slate-500">
                        {team.members.length} members
                      </p>
                    </div>
                  </div>
                  <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
                    {teamProjects.length} projects
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Team Members */}
                <div>
                  <h4 className="text-sm font-medium text-slate-700 mb-3">
                    Team Members
                  </h4>
                  <div className="space-y-3">
                    {team.members.map((member) => (
                      <div
                        key={member.id}
                        className="flex items-center gap-3 p-3 rounded-lg bg-slate-50 hover:bg-slate-100 transition-colors"
                      >
                        <Avatar className="h-10 w-10">
                          <AvatarFallback className="bg-gradient-to-br from-blue-500 to-purple-600 text-white text-sm">
                            {getInitials(member.name)}
                          </AvatarFallback>
                        </Avatar>
                        <div className="flex-1">
                          <p className="font-medium text-slate-800 text-sm">
                            {member.name}
                          </p>
                          <div className="flex items-center gap-1 text-xs text-slate-500">
                            <Mail className="h-3 w-3" />
                            {member.email}
                          </div>
                        </div>
                        <Badge
                          variant="outline"
                          className={
                            member.role === 'admin'
                              ? 'bg-purple-50 text-purple-700 border-purple-200'
                              : 'bg-slate-50 text-slate-700 border-slate-200'
                          }
                        >
                          {member.role}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Assigned Projects */}
                <div className="pt-4 border-t border-slate-200">
                  <h4 className="text-sm font-medium text-slate-700 mb-3">
                    Assigned Projects
                  </h4>
                  <div className="space-y-2">
                    {teamProjects.map((project) => (
                      <div
                        key={project.id}
                        className="flex items-center gap-2 text-sm p-2 rounded bg-white border border-slate-200"
                      >
                        <FolderKanban className="h-4 w-4 text-blue-500" />
                        <span className="text-slate-700">{project.name}</span>
                        <Badge
                          variant="outline"
                          className={
                            project.status === 'done'
                              ? 'ml-auto bg-green-50 text-green-700 border-green-200'
                              : project.status === 'in-progress'
                              ? 'ml-auto bg-blue-50 text-blue-700 border-blue-200'
                              : 'ml-auto bg-amber-50 text-amber-700 border-amber-200'
                          }
                        >
                          {project.status}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
};