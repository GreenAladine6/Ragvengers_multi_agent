import api from './api';
import { Project, Feedback, ChatMessage } from '../types';

// Projects
export const getProjects = async (): Promise<Project[]> => {
    const response = await api.get<any[]>('/projects/');
    return response.data.map((p) => ({
        id: p.id_project.toString(),
        name: p.git_repo ? p.git_repo.split('/').pop() || `Project ${p.id_project}` : `Project ${p.id_project}`,
        description: p.git_repo || 'No description available',
        status: (p.status as any) || 'pending',
        progress: {
            frontend: 0,
            backend: 0,
            database: 0,
            chatbot: 0,
        },
        teamId: '0',
        assignedTo: [], // TODO: Fetch from assigned employees
        startDate: p.start_date || new Date().toISOString(),
        dueDate: p.end_date || new Date().toISOString(),
    }));
};

export const createProject = async (projectData: any): Promise<Project> => {
    const response = await api.post<Project>('/projects/', projectData);
    return response.data;
};

// Feedback
export const getFeedbacks = async (): Promise<Feedback[]> => {
    const response = await api.get<Feedback[]>('/feedback/');
    return response.data;
};

export const createFeedback = async (feedbackData: any): Promise<Feedback> => {
    const response = await api.post<Feedback>('/feedback/', feedbackData);
    return response.data;
};

// Chatbot
export const chatWithBot = async (query: string, projectKey: string = 'PRJ'): Promise<string> => {
    try {
        const response = await api.post<{ response: string }>('/chat/', { query, project_key: projectKey });
        return response.data.response;
    } catch (error) {
        console.error("Chatbot API Error:", error);
        return "I'm currently unable to connect to the AI service. Please ensure the backend is running and Jira credentials are configured.";
    }
};
