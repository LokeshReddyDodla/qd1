import React from 'react';

interface SponsorCardProps {
  name: string;
  tier: 'platinum' | 'gold' | 'silver';
  logo: string;
}

const SponsorCard: React.FC<SponsorCardProps> = ({ name, tier, logo }) => {
  const getTierStyles = () => {
    switch (tier) {
      case 'platinum':
        return 'border-violet-400';
      case 'gold':
        return 'border-yellow-400';
      case 'silver':
        return 'border-gray-400';
      default:
        return 'border-violet-600';
    }
  };

  return (
    <div className={`bg-indigo-900/30 p-6 rounded-lg border-2 ${getTierStyles()} hover:transform hover:scale-105 transition-transform duration-300`}>
      <img src={logo} alt={name} className="h-16 w-auto mx-auto" />
      <p className="text-center text-violet-200 mt-4">{name}</p>
      <p className="text-center text-violet-400 text-sm uppercase">{tier}</p>
    </div>
  );
};

export default SponsorCard;