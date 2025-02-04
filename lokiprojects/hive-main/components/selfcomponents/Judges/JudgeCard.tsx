import React from 'react';
import { Linkedin } from 'lucide-react';

interface JudgeCardProps {
  name: string;
  role: string;
  company: string;
  expertise: string[];
  image: string;
  linkedin?: string;
}

const JudgeCard: React.FC<JudgeCardProps> = ({ name, role, company, expertise, image, linkedin }) => {
  return (
    <div className="bg-indigo-900/30 rounded-lg p-6">
      <div className="flex items-center space-x-4">
        <img src={image} alt={name} className="w-16 h-16 rounded-full object-cover" />
        <div>
          <h3 className="text-lg font-semibold text-white">{name}</h3>
          <p className="text-violet-300">{role}</p>
          <p className="text-violet-400 text-sm">{company}</p>
        </div>
      </div>
      <div className="mt-4">
        <h4 className="text-sm font-medium text-violet-200 mb-2">Expertise</h4>
        <div className="flex flex-wrap gap-2">
          {expertise.map((skill) => (
            <span key={skill} className="px-2 py-1 bg-violet-900/50 rounded-full text-xs text-violet-200">
              {skill}
            </span>
          ))}
        </div>
      </div>
      {linkedin && (
        <div className="mt-4">
          <a href={linkedin} className="text-violet-300 hover:text-violet-100">
            <Linkedin className="h-5 w-5" />
          </a>
        </div>
      )}
    </div>
  );
};

export default JudgeCard;