import React from 'react';
import { useNavigate } from 'react-router';
import { AlertCircle, Home } from 'lucide-react';
import { Card, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';

export const NotFound: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <Card className="border-slate-200 shadow-lg max-w-md">
        <CardContent className="pt-12 pb-12 text-center">
          <div className="flex justify-center mb-4">
            <div className="h-16 w-16 rounded-full bg-red-100 flex items-center justify-center">
              <AlertCircle className="h-8 w-8 text-red-600" />
            </div>
          </div>
          <h2 className="text-3xl font-bold text-slate-800 mb-2">404</h2>
          <h3 className="text-xl font-semibold text-slate-700 mb-3">
            Page Not Found
          </h3>
          <p className="text-slate-600 mb-6">
            The page you're looking for doesn't exist or has been moved.
          </p>
          <Button
            onClick={() => navigate('/')}
            className="bg-blue-600 hover:bg-blue-700"
          >
            <Home className="h-4 w-4 mr-2" />
            Back to Dashboard
          </Button>
        </CardContent>
      </Card>
    </div>
  );
};
