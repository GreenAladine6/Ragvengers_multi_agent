import React, { useState } from 'react';
import { Star, MessageSquare, Calendar, Send } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { getProjects, getFeedbacks, createFeedback } from '../services/data';
import { Project, Feedback as FeedbackType } from '../types';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Badge } from '../components/ui/badge';

export const Feedback: React.FC = () => {
  const { currentUser } = useAuth();
  const [selectedProject, setSelectedProject] = useState<string>('');
  const [rating, setRating] = useState<number>(0);
  const [feedbackText, setFeedbackText] = useState('');
  const [projectsList, setProjectsList] = useState<Project[]>([]);
  const [feedbacksList, setFeedbacksList] = useState<FeedbackType[]>([]);
  const [loading, setLoading] = useState(true);

  React.useEffect(() => {
    const fetchData = async () => {
      try {
        const [projectsData, feedbacksData] = await Promise.all([
          getProjects(),
          getFeedbacks()
        ]);
        setProjectsList(projectsData);
        setFeedbacksList(feedbacksData);
        if (projectsData.length > 0) {
          setSelectedProject(projectsData[0].id);
        }
      } catch (error) {
        console.error('Failed to fetch data', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  // Safety check
  if (!currentUser) {
    return null;
  }

  // Filter projects based on role
  const userProjects =
    currentUser.role === 'admin'
      ? projectsList // Admin sees all projects
      : currentUser.role === 'employee'
        ? projectsList.filter((p) => p.assignedTo.includes(currentUser.id)) // Employee sees collaboration projects
        : projectsList.filter((p) => p.assignedTo.includes(currentUser.id)); // Client sees purchased projects

  // Filter feedback based on role
  const projectFeedbacks =
    currentUser.role === 'client'
      ? feedbacksList.filter((f) => f.projectId === selectedProject) // Client sees feedback for selected project
      : currentUser.role === 'employee'
        ? feedbacksList.filter(
          (f) =>
            f.projectId === selectedProject &&
            userProjects.some((p) => p.id === f.projectId)
        ) // Employee sees feedback only on their collaboration projects
        : feedbacksList.filter((f) => f.projectId === selectedProject); // Admin sees all feedback

  const handleSubmit = async () => {
    if (feedbackText.trim() && rating > 0 && currentUser) {
      try {
        await createFeedback({
          text: feedbackText,
          rating: rating,
          id_project: parseInt(selectedProject),
          id_client: parseInt(currentUser.id) // Assuming currentUser.id is client id
        });
        alert('Feedback submitted successfully!');
        setFeedbackText('');
        setRating(0);
        // Refresh feedbacks
        const updatedFeedbacks = await getFeedbacks();
        setFeedbacksList(updatedFeedbacks);
      } catch (error) {
        alert('Failed to submit feedback');
      }
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-semibold text-slate-800">Feedback & Comments</h2>
        <p className="text-slate-600 mt-1">
          Share your thoughts and feedback on project progress
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Submit Feedback Form */}
        <div className="lg:col-span-2">
          <Card className="border-slate-200 shadow-sm">
            <CardHeader>
              <CardTitle className="text-slate-800">Submit Feedback</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium text-slate-700 mb-2 block">
                  Select Project
                </label>
                <Select value={selectedProject} onValueChange={setSelectedProject}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {userProjects.map((project) => (
                      <SelectItem key={project.id} value={project.id}>
                        {project.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-sm font-medium text-slate-700 mb-2 block">
                  Your Rating
                </label>
                <div className="flex gap-2">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      key={star}
                      onClick={() => setRating(star)}
                      className="transition-transform hover:scale-110"
                    >
                      <Star
                        className={`h-8 w-8 ${star <= rating
                          ? 'fill-amber-400 text-amber-400'
                          : 'text-slate-300'
                          }`}
                      />
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-slate-700 mb-2 block">
                  Your Feedback
                </label>
                <Textarea
                  placeholder="Share your thoughts, suggestions, or concerns..."
                  value={feedbackText}
                  onChange={(e) => setFeedbackText(e.target.value)}
                  rows={6}
                  className="resize-none"
                />
              </div>

              <Button
                onClick={handleSubmit}
                disabled={!feedbackText.trim() || rating === 0}
                className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700"
              >
                <Send className="h-4 w-4 mr-2" />
                Submit Feedback
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Project Info Card */}
        <div className="lg:col-span-1">
          <Card className="border-slate-200 shadow-sm">
            <CardHeader>
              <CardTitle className="text-slate-800">Project Info</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {projectsList
                .filter((p) => p.id === selectedProject)
                .map((project) => {
                  const avgProgress =
                    (project.progress.frontend +
                      project.progress.backend +
                      project.progress.database +
                      project.progress.chatbot) /
                    4;

                  return (
                    <div key={project.id} className="space-y-3">
                      <div>
                        <h3 className="font-semibold text-slate-800 mb-1">
                          {project.name}
                        </h3>
                        <p className="text-sm text-slate-600">{project.description}</p>
                      </div>

                      <div className="pt-3 border-t border-slate-200 space-y-2">
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-slate-600">Status</span>
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
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-slate-600">Progress</span>
                          <span className="font-medium text-slate-800">
                            {Math.round(avgProgress)}%
                          </span>
                        </div>
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-slate-600">Due Date</span>
                          <span className="font-medium text-slate-800">
                            {new Date(project.dueDate).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                    </div>
                  );
                })}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Previous Feedback */}
      <Card className="border-slate-200 shadow-sm">
        <CardHeader>
          <CardTitle className="text-slate-800 flex items-center gap-2">
            <MessageSquare className="h-5 w-5" />
            Previous Feedback
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {projectFeedbacks.length > 0 ? (
              projectFeedbacks.map((feedback) => (
                <div
                  key={feedback.id}
                  className="p-4 rounded-lg border border-slate-200 bg-white hover:border-blue-300 transition-colors"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex gap-1">
                      {[1, 2, 3, 4, 5].map((star) => (
                        <Star
                          key={star}
                          className={`h-4 w-4 ${star <= (feedback.rating || 0)
                            ? 'fill-amber-400 text-amber-400'
                            : 'text-slate-300'
                            }`}
                        />
                      ))}
                    </div>
                    <div className="flex items-center gap-2 text-xs text-slate-500">
                      <Calendar className="h-3.5 w-3.5" />
                      {new Date(feedback.timestamp).toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric',
                        year: 'numeric',
                      })}
                    </div>
                  </div>
                  <p className="text-sm text-slate-700">{feedback.message}</p>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-slate-500">
                No feedback yet for this project. Be the first to share your thoughts!
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};