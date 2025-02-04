import React from 'react';
import { Clock } from 'lucide-react';

interface ScheduleItemProps {
  time: string;
  title: string;
  description: string;
  type: 'workshop' | 'break' | 'ceremony' | 'session';
}

const ScheduleCard: React.FC<ScheduleItemProps> = ({ time, title, description, type }) => {
  const getTypeStyles = () => {
    switch (type) {
      case 'workshop':
        return 'bg-violet-600';
      case 'break':
        return 'bg-indigo-600';
      case 'ceremony':
        return 'bg-purple-600';
      default:
        return 'bg-blue-600';
    }
  };

  return (
    <div className="flex items-start space-x-4 bg-indigo-900/30 p-6 rounded-lg">
      <div className={`${getTypeStyles()} p-3 rounded-full`}>
        <Clock className="h-6 w-6 text-white" />
      </div>
      <div>
        <p className="text-violet-200 text-sm">{time}</p>
        <h3 className="text-white font-medium mt-1">{title}</h3>
        <p className="text-violet-300 mt-2">{description}</p>
      </div>
    </div>
  );
};

export default ScheduleCard;